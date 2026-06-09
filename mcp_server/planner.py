#!/usr/bin/env python3
"""Agent Assist planning helpers for P3."""

from __future__ import annotations

from datetime import datetime, timedelta

try:
    from .vault_reader import VaultReader
except ImportError:  # pragma: no cover - direct script fallback
    from vault_reader import VaultReader


INTENSITY_REVIEW_COUNTS = {
    "light": 3,
    "normal": 5,
    "intensive": 10,
}


def get_learning_plan(
    vault_path: str = "InterviewVault",
    days: int = 1,
    focus_domain: str | None = None,
    intensity: str = "normal",
) -> dict:
    """Generate a read-only Agent Assist plan."""
    if days < 1 or days > 14:
        return {"error": {"code": "invalid_range", "message": "days must be between 1 and 14"}}
    if intensity not in INTENSITY_REVIEW_COUNTS:
        return {"error": {"code": "invalid_choice", "message": "intensity must be light, normal, or intensive"}}

    reader = VaultReader(vault_path)
    review_count = INTENSITY_REVIEW_COUNTS[intensity]
    plan = []
    for offset in range(days):
        date = (datetime.now() + timedelta(days=offset)).strftime("%Y-%m-%d")
        due = reader.get_due_reviews(date=date, limit=review_count, include_mastered=False)
        weak = reader.list_weak_areas(limit=3, domain=focus_domain, min_attempts=1)
        blocks = []

        if due.get("total_due", 0) > 0:
            mode = "DEEP" if weak.get("weak_areas") else "FAST"
            blocks.append({
                "type": "review",
                "mode": mode,
                "count": min(review_count, due["total_due"]),
                "reason": "今日到期且需要保持间隔复习节奏",
                "suggested_command": f"复习 {min(review_count, due['total_due'])} 题，{mode} 模式",
            })

        if weak.get("weak_areas"):
            top = weak["weak_areas"][0]
            blocks.append({
                "type": "learn",
                "concept": top["concept"],
                "note_id": top["note_id"],
                "reason": f"{top['domain']} 薄弱概念，正确率 {top['correct_rate']}",
                "suggested_command": f"学习 {top['concept']}",
            })

        if not blocks:
            blocks.append({
                "type": "maintenance",
                "reason": "暂无到期题和显著薄弱点",
                "suggested_command": "看看进度",
            })

        plan.append({"date": date, "blocks": blocks})

    return {
        "mode": "agent-assist",
        "days": days,
        "focus_domain": focus_domain,
        "intensity": intensity,
        "plan": plan,
        "writes_required": False,
    }
