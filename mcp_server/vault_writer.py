#!/usr/bin/env python3
"""Confirmed Vault writes and audit logging for P3 MCP tools."""

from __future__ import annotations

import copy
import importlib.util
import json
from datetime import datetime
from pathlib import Path

try:
    from .vault_reader import VaultError, VaultReader
except ImportError:  # pragma: no cover
    from vault_reader import VaultError, VaultReader


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def atomic_write_json(path: Path, data: dict) -> None:
    atomic = load_module(PROJECT_ROOT / "scripts" / "atomic_write.py")
    atomic.atomic_write_json(str(path), data)


def atomic_write_text(path: Path, content: str) -> None:
    atomic = load_module(PROJECT_ROOT / "scripts" / "atomic_write.py")
    atomic.atomic_write_text(str(path), content)


def record_review_result(
    vault_path: str,
    question_id: str,
    score: int,
    mode: str,
    confirmed: bool,
) -> dict:
    """Record a review result after explicit confirmation."""
    if not question_id:
        return _error("missing_required", "question_id is required")
    if score < 1 or score > 5:
        return _error("invalid_score", "score must be between 1 and 5")
    if mode not in {"FAST", "DEEP", "INTERVIEW"}:
        return _error("invalid_mode", "mode must be FAST, DEEP, or INTERVIEW")

    reader = VaultReader(vault_path)
    schedule_path = reader.root / ".progress" / "schedule.json"
    stats_path = reader.root / ".progress" / "stats.json"
    audit_path = reader.root / ".progress" / "agent_actions.jsonl"

    schedule = reader.schedule()
    if question_id not in schedule.get("items", {}):
        return _error("not_found", f"Question ID not found: {question_id}")

    before_item = copy.deepcopy(schedule["items"][question_id])
    updated_schedule = copy.deepcopy(schedule)
    sm2 = load_module(PROJECT_ROOT / ".claude" / "skills" / "review" / "scripts" / "sm2.py")
    engine = sm2.SM2Engine()
    item = sm2.SM2Engine.from_dict(updated_schedule["items"][question_id])
    updated = engine.review(item, score)
    updated_schedule["items"][question_id] = engine.to_dict(updated)
    updated_schedule["last_updated"] = datetime.now().isoformat()

    dry_run_payload = {
        "written": False,
        "question_id": question_id,
        "before": _summarize_item(before_item),
        "after": _summarize_item(updated_schedule["items"][question_id]),
        "requires_confirmation": True,
    }
    if not confirmed:
        return dry_run_payload

    before_schedule_text = schedule_path.read_text(encoding="utf-8") if schedule_path.exists() else ""
    before_stats_text = stats_path.read_text(encoding="utf-8") if stats_path.exists() else ""
    before_audit_text = audit_path.read_text(encoding="utf-8") if audit_path.exists() else ""

    audit_id = f"{datetime.now().isoformat()}-{question_id}"
    audit_record = {
        "timestamp": datetime.now().isoformat(),
        "audit_id": audit_id,
        "actor": "agent-assist",
        "action": "record_review_result",
        "target": question_id,
        "confirmed": True,
        "mode": mode,
        "score": score,
        "before": _summarize_item(before_item),
        "after": _summarize_item(updated_schedule["items"][question_id]),
    }

    try:
        atomic_write_json(schedule_path, updated_schedule)

        stats_mod = load_module(PROJECT_ROOT / ".claude" / "skills" / "dashboard" / "scripts" / "stats.py")
        stats = stats_mod.recalculate_stats(str(reader.root))
        atomic_write_json(stats_path, stats)

        new_audit_text = before_audit_text + json.dumps(audit_record, ensure_ascii=False) + "\n"
        atomic_write_text(audit_path, new_audit_text)

        validate = load_module(PROJECT_ROOT / "scripts" / "validate_consistency.py")
        errors = validate.validate(str(reader.root))
        if errors:
            raise VaultError(f"Consistency validation failed: {errors}")
    except Exception as exc:
        if before_schedule_text:
            atomic_write_text(schedule_path, before_schedule_text)
        if before_stats_text:
            atomic_write_text(stats_path, before_stats_text)
        atomic_write_text(audit_path, before_audit_text)
        return _error("write_failed", str(exc))

    return {
        "written": True,
        "question_id": question_id,
        "before": _summarize_item(before_item),
        "after": _summarize_item(updated_schedule["items"][question_id]),
        "audit_id": audit_id,
    }


def _summarize_item(item: dict) -> dict:
    return {
        "status": item.get("status"),
        "interval": item.get("interval"),
        "next_review": item.get("next_review"),
        "ease_factor": item.get("ease_factor"),
    }


def _error(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}
