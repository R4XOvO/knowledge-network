#!/usr/bin/env python3
"""P3 MCP tool contract tests."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from mcp_server.resources import read_resource
from mcp_server.tools import TOOL_SCHEMAS, call_tool


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(vault_path: str = "InterviewVault") -> bool:
    print("P3 MCP Contract Test")
    expected = {
        "query_knowledge",
        "list_weak_areas",
        "get_due_reviews",
        "get_learning_plan",
        "record_review_result",
    }
    assert_true(set(TOOL_SCHEMAS) == expected, "tool schema set changed")
    for name, schema in TOOL_SCHEMAS.items():
        assert_true("inputSchema" in schema, f"{name} missing inputSchema")
        assert_true(schema["inputSchema"]["type"] == "object", f"{name} schema must be object")

    missing = call_tool("query_knowledge", {}, vault_path)
    assert_true(missing["error"]["code"] == "missing_required", "missing required error shape changed")

    vault = Path(vault_path)
    schedule_hash = digest(vault / ".progress" / "schedule.json")
    stats_hash = digest(vault / ".progress" / "stats.json")
    call_tool("list_weak_areas", {"limit": 3, "min_attempts": 0}, vault_path)
    call_tool("get_due_reviews", {"limit": 3}, vault_path)
    call_tool("get_learning_plan", {"days": 1}, vault_path)
    read_resource("vault://stats", vault_path)
    assert_true(digest(vault / ".progress" / "schedule.json") == schedule_hash, "read tools changed schedule")
    assert_true(digest(vault / ".progress" / "stats.json") == stats_hash, "read tools changed stats")

    plan = call_tool("get_learning_plan", {"days": 1, "intensity": "normal"}, vault_path)
    assert_true(plan["writes_required"] is False, "learning plan must be dry-run")
    json.dumps(plan, ensure_ascii=False)

    print("[OK] P3 MCP contract test passed")
    return True


if __name__ == "__main__":
    vp = sys.argv[1] if len(sys.argv) > 1 else "InterviewVault"
    raise SystemExit(0 if run(vp) else 1)
