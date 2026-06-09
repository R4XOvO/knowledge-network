#!/usr/bin/env python3
"""Minimal stdio JSON-RPC server for Interview Knowledge System P3.

The implementation exposes MCP-compatible method names for local clients:
`tools/list`, `tools/call`, `resources/list`, and `resources/read`.
"""

from __future__ import annotations

import argparse
import json
import sys

try:
    from .resources import list_resources, read_resource
    from .tools import call_tool, list_tools
    from .vault_reader import VaultReader
except ImportError:  # pragma: no cover
    from resources import list_resources, read_resource
    from tools import call_tool, list_tools
    from vault_reader import VaultReader


def handle_request(request: dict, vault_path: str) -> dict:
    method = request.get("method")
    params = request.get("params") or {}
    request_id = request.get("id")
    try:
        if method == "initialize":
            result = {
                "protocolVersion": "2026-06-09-local",
                "serverInfo": {"name": "interview-knowledge-system", "version": "0.3"},
                "capabilities": {"tools": {}, "resources": {}},
            }
        elif method == "tools/list":
            result = {"tools": list_tools()}
        elif method == "tools/call":
            result = call_tool(params.get("name"), params.get("arguments", {}), vault_path)
        elif method == "resources/list":
            result = {"resources": list_resources(vault_path)}
        elif method == "resources/read":
            result = read_resource(params.get("uri", ""), vault_path)
        else:
            return _response(request_id, error={"code": -32601, "message": f"Method not found: {method}"})
        return _response(request_id, result=result)
    except Exception as exc:
        return _response(request_id, error={"code": -32000, "message": str(exc)})


def run_stdio(vault_path: str) -> None:
    VaultReader(vault_path)  # fail fast on unsafe or missing vault
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request, vault_path)
        except json.JSONDecodeError as exc:
            response = _response(None, error={"code": -32700, "message": str(exc)})
        print(json.dumps(response, ensure_ascii=False), flush=True)


def _response(request_id, result=None, error=None) -> dict:
    response = {"jsonrpc": "2.0", "id": request_id}
    if error is not None:
        response["error"] = error
    else:
        response["result"] = result
    return response


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", default="InterviewVault")
    args = parser.parse_args()
    run_stdio(args.vault)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
