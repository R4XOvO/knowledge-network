#!/usr/bin/env python3
"""MCP resource registry for P3."""

from __future__ import annotations

try:
    from .vault_reader import VaultReader
except ImportError:  # pragma: no cover
    from vault_reader import VaultReader


def list_resources(vault_path: str = "InterviewVault") -> list[dict]:
    reader = VaultReader(vault_path)
    return reader.resource_templates()


def read_resource(uri: str, vault_path: str = "InterviewVault") -> dict:
    reader = VaultReader(vault_path)
    return reader.read_resource(uri)
