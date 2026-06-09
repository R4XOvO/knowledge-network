#!/usr/bin/env python3
"""P3 MCP smoke tests."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from mcp_server.resources import list_resources
from mcp_server.server import handle_request
from mcp_server.tools import call_tool, list_tools
from mcp_server.vault_reader import VaultError, VaultReader


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def run(vault_path: str = "InterviewVault") -> bool:
    print("P3 MCP Smoke Test")
    tools = list_tools()
    resources = list_resources(vault_path)
    assert_true(len(tools) == 5, f"expected 5 tools, got {len(tools)}")
    assert_true(len(resources) == 4, f"expected 4 resources, got {len(resources)}")

    query = call_tool("query_knowledge", {"concept": "java-jvm-gc"}, vault_path)
    assert_true("note" in query or "error" in query, "query_knowledge returned invalid shape")

    response = handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, vault_path)
    assert_true(response["result"]["tools"], "tools/list returned empty tools")

    try:
        VaultReader(str(ROOT.parent))
        raise AssertionError("CWD escape should have failed")
    except VaultError:
        pass

    print("[OK] P3 MCP smoke test passed")
    return True


if __name__ == "__main__":
    vp = sys.argv[1] if len(sys.argv) > 1 else "InterviewVault"
    raise SystemExit(0 if run(vp) else 1)
