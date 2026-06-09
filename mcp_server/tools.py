#!/usr/bin/env python3
"""MCP tool registry and dispatch for P3."""

from __future__ import annotations

try:
    from .planner import get_learning_plan
    from .vault_reader import VaultReader
    from .vault_writer import record_review_result
except ImportError:  # pragma: no cover
    from planner import get_learning_plan
    from vault_reader import VaultReader
    from vault_writer import record_review_result


TOOL_SCHEMAS = {
    "query_knowledge": {
        "description": "查询某个概念的笔记、相关 Q&A 和面试陷阱。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "concept": {"type": "string"},
                "domain": {"type": "string"},
                "include_questions": {"type": "boolean", "default": True},
                "include_traps": {"type": "boolean", "default": True},
            },
            "required": ["concept"],
        },
        "readOnlyHint": True,
    },
    "list_weak_areas": {
        "description": "列出当前薄弱概念。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
                "domain": {"type": "string"},
                "min_attempts": {"type": "integer", "minimum": 0, "default": 1},
            },
        },
        "readOnlyHint": True,
    },
    "get_due_reviews": {
        "description": "获取指定日期到期的复习题。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
                "include_mastered": {"type": "boolean", "default": False},
            },
        },
        "readOnlyHint": True,
    },
    "get_learning_plan": {
        "description": "生成 Agent Assist 学习计划，不写入 Vault。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "minimum": 1, "maximum": 14, "default": 1},
                "focus_domain": {"type": "string"},
                "intensity": {"type": "string", "enum": ["light", "normal", "intensive"], "default": "normal"},
            },
        },
        "readOnlyHint": True,
    },
    "record_review_result": {
        "description": "确认后记录一次复习结果，并更新 SM-2 调度。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question_id": {"type": "string"},
                "score": {"type": "integer", "minimum": 1, "maximum": 5},
                "mode": {"type": "string", "enum": ["FAST", "DEEP", "INTERVIEW"]},
                "confirmed": {"type": "boolean"},
            },
            "required": ["question_id", "score", "mode", "confirmed"],
        },
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
    },
}


def list_tools() -> list[dict]:
    return [
        {
            "name": name,
            "description": schema["description"],
            "inputSchema": schema["inputSchema"],
            "annotations": {
                "readOnlyHint": schema.get("readOnlyHint", False),
                "destructiveHint": schema.get("destructiveHint", False),
                "idempotentHint": schema.get("idempotentHint", True),
            },
        }
        for name, schema in TOOL_SCHEMAS.items()
    ]


def call_tool(name: str, args: dict | None, vault_path: str = "InterviewVault") -> dict:
    args = args or {}
    if name not in TOOL_SCHEMAS:
        return _error("unknown_tool", f"Unknown tool: {name}")

    missing = [field for field in TOOL_SCHEMAS[name]["inputSchema"].get("required", []) if field not in args]
    if missing:
        return _error("missing_required", f"Missing required field(s): {', '.join(missing)}")

    reader = VaultReader(vault_path)
    if name == "query_knowledge":
        return reader.query_knowledge(
            concept=args["concept"],
            domain=args.get("domain"),
            include_questions=args.get("include_questions", True),
            include_traps=args.get("include_traps", True),
        )
    if name == "list_weak_areas":
        return reader.list_weak_areas(
            limit=int(args.get("limit", 5)),
            domain=args.get("domain"),
            min_attempts=int(args.get("min_attempts", 1)),
        )
    if name == "get_due_reviews":
        return reader.get_due_reviews(
            date=args.get("date"),
            limit=int(args.get("limit", 10)),
            include_mastered=bool(args.get("include_mastered", False)),
        )
    if name == "get_learning_plan":
        return get_learning_plan(
            vault_path=vault_path,
            days=int(args.get("days", 1)),
            focus_domain=args.get("focus_domain"),
            intensity=args.get("intensity", "normal"),
        )
    if name == "record_review_result":
        return record_review_result(
            vault_path=vault_path,
            question_id=args["question_id"],
            score=int(args["score"]),
            mode=args["mode"],
            confirmed=bool(args["confirmed"]),
        )
    return _error("unhandled_tool", f"Tool not implemented: {name}")


def _error(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}
