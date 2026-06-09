#!/usr/bin/env python3
"""P3 Agent confirmed-write E2E test."""

from pathlib import Path
import importlib.util
import json
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from mcp_server.tools import call_tool


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def run(source_vault: str = "InterviewVault") -> bool:
    print("P3 Agent Confirmed-write E2E")
    with tempfile.TemporaryDirectory(dir=str(ROOT)) as tmp:
        vault = Path(tmp) / "InterviewVault"
        shutil.copytree(source_vault, vault)

        schedule_path = vault / ".progress" / "schedule.json"
        before_schedule = schedule_path.read_text(encoding="utf-8")

        dry = call_tool(
            "record_review_result",
            {"question_id": "java-jvm-gc-q01", "score": 4, "mode": "FAST", "confirmed": False},
            str(vault),
        )
        assert_true(dry["written"] is False, "dry-run must not write")
        assert_true(schedule_path.read_text(encoding="utf-8") == before_schedule, "dry-run changed schedule")

        written = call_tool(
            "record_review_result",
            {"question_id": "java-jvm-gc-q01", "score": 4, "mode": "FAST", "confirmed": True},
            str(vault),
        )
        assert_true(written["written"] is True, f"confirmed write failed: {written}")
        assert_true((vault / ".progress" / "agent_actions.jsonl").exists(), "audit log missing")
        audit_lines = (vault / ".progress" / "agent_actions.jsonl").read_text(encoding="utf-8").splitlines()
        assert_true(any("record_review_result" in line for line in audit_lines), "audit record missing action")

        schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
        item = schedule["items"]["java-jvm-gc-q01"]
        assert_true(item["total_attempts"] >= 1, "schedule item was not updated")

        validate = load_module(ROOT / "scripts" / "validate_consistency.py")
        errors = validate.validate(str(vault))
        assert_true(errors == [], f"consistency errors: {errors}")

    print("[OK] P3 Agent E2E test passed")
    return True


if __name__ == "__main__":
    vp = sys.argv[1] if len(sys.argv) > 1 else "InterviewVault"
    raise SystemExit(0 if run(vp) else 1)
