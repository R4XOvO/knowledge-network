#!/usr/bin/env python3
"""Read-only Vault access helpers for the P3 MCP server."""

from __future__ import annotations

import json
import re
from datetime import datetime
from difflib import get_close_matches
from pathlib import Path
from typing import Any


class VaultError(Exception):
    """Base error for controlled Vault access failures."""


class VaultReader:
    """Safe read-only view over InterviewVault."""

    def __init__(self, vault_path: str = "InterviewVault", cwd: str | None = None):
        self.cwd = Path(cwd or Path.cwd()).resolve()
        self.root = Path(vault_path).resolve()
        if not self._is_within(self.root, self.cwd):
            raise VaultError(f"Vault path {self.root} is outside CWD {self.cwd}")
        if not self.root.exists():
            raise VaultError(f"Vault path not found: {self.root}")

    @staticmethod
    def _is_within(path: Path, parent: Path) -> bool:
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False

    def _safe_path(self, relative_path: str) -> Path:
        target = (self.root / relative_path).resolve()
        if not self._is_within(target, self.root):
            raise VaultError(f"Path escapes vault: {relative_path}")
        return target

    def relative(self, path: Path) -> str:
        return str(path.resolve().relative_to(self.root)).replace("\\", "/")

    def read_json(self, relative_path: str, default: Any) -> Any:
        path = self._safe_path(relative_path)
        if not path.exists():
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def read_text(self, relative_path: str, limit: int = 8000) -> str:
        path = self._safe_path(relative_path)
        if not path.exists():
            raise VaultError(f"File not found: {relative_path}")
        text = path.read_text(encoding="utf-8")
        return text[:limit]

    def stats(self) -> dict:
        return self.read_json(".progress/stats.json", {})

    def schedule(self) -> dict:
        return self.read_json(".progress/schedule.json", {"items": {}})

    def parse_frontmatter(self, content: str) -> tuple[dict, str]:
        if not content.startswith("---"):
            return {}, content
        end = content.find("---", 3)
        if end == -1:
            return {}, content
        fm = {}
        for line in content[3:end].splitlines():
            line = line.strip()
            if ":" not in line or line.startswith("#"):
                continue
            key, value = line.split(":", 1)
            fm[key.strip()] = value.strip().strip("\"'")
        return fm, content[end + 3:]

    def notes(self) -> list[dict]:
        notes = []
        notes_dir = self.root / "01-Notes"
        if not notes_dir.exists():
            return notes
        for path in notes_dir.rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            fm, body = self.parse_frontmatter(content)
            if not fm:
                continue
            notes.append({
                **fm,
                "note_id": fm.get("id", ""),
                "file_path": self.relative(path),
                "summary": self._summarize_markdown(body),
                "_body": body,
            })
        return notes

    def questions(self) -> list[dict]:
        results = []
        questions_dir = self.root / "02-Questions"
        if not questions_dir.exists():
            return results
        for path in questions_dir.rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            fm, body = self.parse_frontmatter(content)
            concept_id = fm.get("concept_id") or fm.get("id", "")
            for q in self._extract_questions(body, concept_id):
                results.append({
                    **q,
                    "concept_id": concept_id,
                    "domain": fm.get("domain", "Unknown"),
                    "frequency": fm.get("frequency", "常问"),
                    "file_path": self.relative(path),
                })
        return results

    def traps(self, domain: str | None = None) -> list[dict]:
        traps_dir = self.root / "03-Exam-Traps"
        if not traps_dir.exists():
            return []
        results = []
        paths = [traps_dir / f"{domain}.md"] if domain else list(traps_dir.glob("*.md"))
        for path in paths:
            if not path.exists():
                continue
            content = path.read_text(encoding="utf-8")
            for title in re.findall(r"^##\s+(.+)$", content, re.MULTILINE):
                results.append({
                    "title": title.strip(),
                    "domain": path.stem,
                    "file_path": self.relative(path),
                })
        return results

    def query_knowledge(
        self,
        concept: str,
        domain: str | None = None,
        include_questions: bool = True,
        include_traps: bool = True,
    ) -> dict:
        if not concept:
            return self._error("missing_required", "concept is required")

        all_notes = self.notes()
        note = self._find_note(all_notes, concept)
        if not note:
            candidates = get_close_matches(
                concept,
                [n.get("concept", "") for n in all_notes] + [n.get("note_id", "") for n in all_notes],
                n=5,
                cutoff=0.2,
            )
            return self._error("not_found", f"Concept not found: {concept}", {"candidates": candidates})

        if domain and note.get("domain") != domain:
            return self._error(
                "domain_mismatch",
                f"Concept exists in domain {note.get('domain')}, not {domain}",
                {"actual_domain": note.get("domain")},
            )

        note_id = note.get("note_id")
        payload = {
            "note": {
                "note_id": note_id,
                "concept": note.get("concept", note_id),
                "domain": note.get("domain", "Unknown"),
                "frequency": note.get("frequency", "常问"),
                "status": note.get("status", "learning"),
                "file_path": note.get("file_path", ""),
                "summary": note.get("summary", ""),
            },
            "questions": [],
            "traps": [],
        }

        if include_questions:
            payload["questions"] = [
                {
                    "question_id": q["question_id"],
                    "question": q["question"],
                    "file_path": q["file_path"],
                }
                for q in self.questions()
                if q.get("concept_id") == note_id
            ]

        if include_traps:
            payload["traps"] = self.traps(note.get("domain"))

        return payload

    def list_weak_areas(self, limit: int = 5, domain: str | None = None, min_attempts: int = 1) -> dict:
        schedule = self.schedule().get("items", {})
        notes_by_id = {n["note_id"]: n for n in self.notes()}
        areas = []
        for note_id, note in notes_by_id.items():
            items = [i for i in schedule.values() if i.get("note_id") == note_id]
            attempts = sum(i.get("total_attempts", 0) for i in items)
            correct = sum(i.get("total_correct", 0) for i in items)
            if attempts < min_attempts:
                continue
            rate = round(correct / attempts, 2) if attempts else 0.0
            is_weak = rate < 0.6 or any(i.get("status") == "weak" for i in items)
            if not is_weak:
                continue
            if domain and note.get("domain") != domain:
                continue
            areas.append({
                "note_id": note_id,
                "concept": note.get("concept", note_id),
                "domain": note.get("domain", "Unknown"),
                "correct_rate": rate,
                "attempts": attempts,
                "priority": "high" if rate < 0.4 else "medium",
                "recommended_action": "DEEP review" if rate < 0.6 else "FAST review",
            })
        areas.sort(key=lambda x: (x["correct_rate"], -x["attempts"]))
        return {"weak_areas": areas[:limit]}

    def get_due_reviews(
        self,
        date: str | None = None,
        limit: int = 10,
        include_mastered: bool = False,
    ) -> dict:
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        notes_by_id = {n["note_id"]: n for n in self.notes()}
        items = []
        for qid, item in self.schedule().get("items", {}).items():
            if item.get("next_review", "9999-99-99") > target_date:
                continue
            if not include_mastered and item.get("status") == "mastered":
                continue
            note = notes_by_id.get(item.get("note_id"), {})
            items.append({
                "question_id": qid,
                "note_id": item.get("note_id", ""),
                "concept": note.get("concept", item.get("note_id", "")),
                "domain": note.get("domain", "Unknown"),
                "frequency": note.get("frequency", "常问"),
                "next_review": item.get("next_review", ""),
                "status": item.get("status", "learning"),
            })
        items.sort(key=lambda x: (x["next_review"], x["frequency"] != "必问"))
        return {"date": target_date, "total_due": len(items), "items": items[:limit]}

    def read_resource(self, uri: str) -> dict:
        if uri == "vault://stats":
            return {"uri": uri, "source_path": ".progress/stats.json", "content": self.stats()}
        if uri == "vault://schedule":
            return {"uri": uri, "source_path": ".progress/schedule.json", "content": self.schedule()}
        if uri.startswith("vault://notes/"):
            note_id = uri.rsplit("/", 1)[-1]
            note = next((n for n in self.notes() if n.get("note_id") == note_id), None)
            if not note:
                return self._error("not_found", f"Note not found: {note_id}")
            return {
                "uri": uri,
                "source_path": note["file_path"],
                "content": self.read_text(note["file_path"]),
            }
        if uri.startswith("vault://questions/"):
            question_id = uri.rsplit("/", 1)[-1]
            question = next((q for q in self.questions() if q.get("question_id") == question_id), None)
            if not question:
                return self._error("not_found", f"Question not found: {question_id}")
            return {
                "uri": uri,
                "source_path": question["file_path"],
                "content": self.read_text(question["file_path"]),
            }
        return self._error("not_found", f"Unknown resource URI: {uri}")

    def resource_templates(self) -> list[dict]:
        return [
            {"uri": "vault://stats", "name": "Vault stats"},
            {"uri": "vault://schedule", "name": "Review schedule"},
            {"uriTemplate": "vault://notes/{note_id}", "name": "Concept note"},
            {"uriTemplate": "vault://questions/{question_id}", "name": "Interview question"},
        ]

    def _find_note(self, notes: list[dict], concept: str) -> dict | None:
        needle = concept.lower()
        for note in notes:
            if needle in (note.get("note_id") or "").lower():
                return note
            if needle in (note.get("concept") or "").lower():
                return note
        return None

    def _summarize_markdown(self, body: str, limit: int = 400) -> str:
        lines = []
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith(">"):
                continue
            lines.append(stripped)
            if sum(len(x) for x in lines) >= limit:
                break
        return " ".join(lines)[:limit]

    def _extract_questions(self, body: str, concept_id: str) -> list[dict]:
        matches = list(re.finditer(r"^##\s+Q(\d+)\s*[—-]\s*(.+)$", body, re.MULTILINE))
        questions = []
        for idx, match in enumerate(matches):
            number = match.group(1)
            title = match.group(2).strip()
            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
            block = body[start:end]
            q_text = self._extract_question_text(block) or title
            questions.append({
                "question_id": f"{concept_id}-q{number}",
                "question": q_text,
                "title": title,
            })
        return questions

    def _extract_question_text(self, block: str) -> str:
        marker = re.search(r"^###\s+问题\s*$", block, re.MULTILINE)
        if not marker:
            return ""
        after = block[marker.end():]
        lines = []
        for line in after.splitlines():
            stripped = line.strip()
            if stripped.startswith("> [!answer]") or stripped.startswith("---") or stripped.startswith("## "):
                break
            if stripped:
                lines.append(stripped)
        return " ".join(lines).strip()

    def _error(self, code: str, message: str, extra: dict | None = None) -> dict:
        return {"error": {"code": code, "message": message, **(extra or {})}}
