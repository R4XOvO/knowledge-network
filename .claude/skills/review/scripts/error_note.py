#!/usr/bin/env python3
"""
错误笔记自动记录工具

当复习评分 <= 2 时，自动：
1. 在对应笔记文件末尾追加错误笔记
2. 在 03-Exam-Traps/{Domain}.md 中追加/更新陷阱条目

用法:
    python error_note.py <vault_path> <question_id> <score> \
        --answer "{用户回答}" \
        --misconception "{混淆点}" \
        --correct "{正确理解}"

完整规格见 DEV_SPEC 8.3.7 错误笔记系统
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """解析 Markdown 文件的 frontmatter，返回 (frontmatter_dict, body)"""
    if not content.startswith("---"):
        return {}, content

    end = content.find("---", 3)
    if end == -1:
        return {}, content

    fm = {}
    for line in content[3:end].splitlines():
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"\'')
            fm[key] = val

    body = content[end + 3:]
    return fm, body


def find_note_by_id(vault_path: str, note_id: str) -> Path | None:
    """根据 note_id 查找笔记文件路径"""
    notes_dir = Path(vault_path) / "01-Notes"
    if not notes_dir.exists():
        return None

    for note_file in notes_dir.rglob("*.md"):
        with open(note_file, "r", encoding="utf-8") as f:
            content = f.read()
        fm, _ = parse_frontmatter(content)
        if fm.get("id") == note_id:
            return note_file
    return None


def find_question_file(vault_path: str, question_id: str) -> tuple[Path, dict] | None:
    """根据 question_id 查找 Q&A 文件路径和 frontmatter"""
    questions_dir = Path(vault_path) / "02-Questions"
    if not questions_dir.exists():
        return None

    # question_id 格式: {note-id}-q{NN}
    note_id = question_id.rsplit("-q", 1)[0] if "-q" in question_id else question_id

    for qf in questions_dir.rglob("*.md"):
        with open(qf, "r", encoding="utf-8") as f:
            content = f.read()
        fm, body = parse_frontmatter(content)
        if fm.get("id") == note_id or fm.get("concept_id") == note_id:
            return qf, fm
    return None


def append_error_to_note(note_path: Path, question_id: str,
                         question_text: str, user_answer: str,
                         misconception: str, correct: str) -> None:
    """在笔记文件末尾追加错误笔记"""
    today = datetime.now().strftime("%Y-%m-%d")

    error_section = f"""
### 错误笔记

**{today} — {question_id}**
- **问题**：{question_text}
- **错误回答**：{user_answer}
- **混淆点**：{misconception}
- **正确理解**：{correct}
- **关联概念**：[[02-Questions/...]]

"""

    with open(note_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否已有错误笔记标题
    if "### 错误笔记" not in content:
        # 在文件末尾添加
        content = content.rstrip() + "\n\n" + error_section
    else:
        # 在最后一个 ### 错误笔记 后面追加
        idx = content.rfind("### 错误笔记")
        content = content[:idx] + error_section + content[idx:]

    with open(note_path, "w", encoding="utf-8") as f:
        f.write(content)


def ensure_exam_trap_file(vault_path: str, domain: str) -> Path:
    """确保 03-Exam-Traps/{Domain}.md 存在，不存在则创建模板"""
    traps_dir = Path(vault_path) / "03-Exam-Traps"
    traps_dir.mkdir(parents=True, exist_ok=True)

    trap_file = traps_dir / f"{domain}.md"
    if not trap_file.exists():
        today = datetime.now().strftime("%Y-%m-%d")
        template = f"""---
domain: "{domain}"
keywords: exam-traps, interview, {domain.lower()}
updated_at: "{today}"
---

# {domain} — 面试陷阱

#interview-traps #{domain.lower()}

> [!warning] 本笔记用途
> 记录 {domain} 领域面试中最容易踩坑、最容易混淆的知识点。

"""
        with open(trap_file, "w", encoding="utf-8") as f:
            f.write(template)

    return trap_file


def append_error_to_trap(trap_path: Path, concept_slug: str,
                         concept_name: str, trap_title: str,
                         what: str, why_confusing: str,
                         correct: str, scoring_answer: str) -> None:
    """在 Exam Traps 文件中追加/更新陷阱条目"""
    today = datetime.now().strftime("%Y-%m-%d")

    entry = f"""
---

## {concept_name}

> [!danger]- 陷阱：{trap_title}
> - **什么陷阱**：{what}
> - **为什么容易错**：{why_confusing}
> - **正确理解**：{correct}
> - **踩分回答**：{scoring_answer}
> - [[01-Notes/...|概念笔记]]
> - [[02-Questions/...|面试问答]]

"""

    with open(trap_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否已有该概念的陷阱条目
    if f"## {concept_name}" in content:
        # 在现有条目后追加新的 danger callout
        idx = content.find(f"## {concept_name}")
        next_heading = content.find("\n## ", idx + len(f"## {concept_name}"))
        if next_heading == -1:
            content = content.rstrip() + entry
        else:
            content = content[:next_heading] + entry + content[next_heading:]
    else:
        content = content.rstrip() + entry

    with open(trap_path, "w", encoding="utf-8") as f:
        f.write(content)


def record_error(vault_path: str, question_id: str, score: int,
                 user_answer: str = "", misconception: str = "",
                 correct: str = "", question_text: str = "") -> dict:
    """
    记录错误笔记

    Returns:
        {"success": bool, "note_updated": str|None, "trap_updated": str|None, "error": str|None}
    """
    result = {"success": False, "note_updated": None,
              "trap_updated": None, "error": None}

    if score > 2:
        result["error"] = "Score > 2, no error note needed"
        return result

    # 1. 查找 schedule 获取 note_id
    schedule_path = Path(vault_path) / ".progress" / "schedule.json"
    note_id = None
    if schedule_path.exists():
        with open(schedule_path, "r", encoding="utf-8") as f:
            schedule = json.load(f)
        item = schedule.get("items", {}).get(question_id, {})
        note_id = item.get("note_id")

    if not note_id:
        result["error"] = f"Cannot find note_id for question {question_id}"
        return result

    # 2. 查找笔记文件
    note_path = find_note_by_id(vault_path, note_id)
    if not note_path:
        result["error"] = f"Note file not found for id {note_id}"
        return result

    # 3. 获取概念信息
    with open(note_path, "r", encoding="utf-8") as f:
        note_fm, _ = parse_frontmatter(f.read())

    concept_name = note_fm.get("concept", note_id)
    domain = note_fm.get("domain", "Unknown")
    concept_slug = note_id  # 使用 id 作为 slug

    # 4. 追加错误笔记到笔记文件
    append_error_to_note(
        note_path, question_id, question_text or f"Q: {question_id}",
        user_answer or "（未记录）",
        misconception or "（未分析）",
        correct or "（未记录）"
    )
    result["note_updated"] = str(note_path.relative_to(vault_path))

    # 5. 追加/更新 Exam Traps
    trap_path = ensure_exam_trap_file(vault_path, domain)
    append_error_to_trap(
        trap_path, concept_slug, concept_name,
        trap_title=f"{concept_name} 常见错误",
        what=misconception or "概念理解错误",
        why_confusing="复习时评分较低",
        correct=correct or "请参考概念笔记",
        scoring_answer="请结合具体场景分析"
    )
    result["trap_updated"] = str(trap_path.relative_to(vault_path))

    result["success"] = True
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="记录错误笔记")
    parser.add_argument("vault_path", help="Vault 根目录路径")
    parser.add_argument("question_id", help="问题 ID")
    parser.add_argument("score", type=int, help="评分 (1-5)")
    parser.add_argument("--answer", default="", help="用户回答")
    parser.add_argument("--misconception", default="", help="混淆点")
    parser.add_argument("--correct", default="", help="正确理解")
    parser.add_argument("--question", default="", help="问题原文")

    args = parser.parse_args()

    result = record_error(
        args.vault_path, args.question_id, args.score,
        args.answer, args.misconception, args.correct, args.question
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["success"] else 1)
