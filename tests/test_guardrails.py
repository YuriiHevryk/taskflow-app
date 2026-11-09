
import json
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

HOOK_PATH = (
    PROJECT_ROOT
    / ".github"
    / "hooks"
    / "pre_tool_guardrail.py"
)


class TestGuardrails(unittest.TestCase):

    def check_rule(self, tool_name, tool_args, expected, rule=None):
        """Run the hook with a simulated tool event."""

        event = {
            "toolName": tool_name,
            "toolArgs": tool_args,
        }

        process = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=json.dumps(event, ensure_ascii=True),
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=PROJECT_ROOT,
            timeout=10,
        )

        self.assertEqual(
            process.returncode,
            0,
            msg=process.stderr,
        )

        result = json.loads(process.stdout)

        self.assertEqual(
            result.get("permissionDecision"),
            expected,
        )

        if rule:
            self.assertIn(
                rule,
                result.get("permissionDecisionReason", ""),
            )

    # ALLOW

    def test_A01_read_documentation(self):
        self.check_rule(
            "view",
            {"file_path": "docs/app-requirements.md"},
            "allow",
        )

    def test_A02_search_notes(self):
        self.check_rule(
            "taskflow-vault_search_notes",
            {"query": "SQLite"},
            "allow",
        )

    def test_A03_git_status(self):
        self.check_rule(
            "powershell",
            {"command": "git status"},
            "allow",
        )

    # WARN

    def test_W01_edit_server(self):
        self.check_rule(
            "edit",
            {"file_path": "connector/server.py"},
            "ask",
            "WARN W-01",
        )

    def test_W02_ingest_note(self):
        self.check_rule(
            "taskflow-vault_ingest_note",
            {
                "title": "Test Note",
                "note_type": "concept",
                "content": "Test content",
                "approved": False,
            },
            "ask",
            "WARN W-02",
        )

    def test_W03_git_push(self):
        self.check_rule(
            "powershell",
            {"command": "git push --dry-run origin main"},
            "ask",
            "WARN W-03",
        )

    # BLOCK

    def test_B01_force_push(self):
        self.check_rule(
            "powershell",
            {
                "command":
                "git push --force --dry-run origin main"
            },
            "deny",
            "BLOCK B-01",
        )

    def test_B02_delete_decision(self):
        self.check_rule(
            "delete_file",
            {
                "path":
                "Decisions/SQLite Storage Decision.md"
            },
            "deny",
            "BLOCK B-02",
        )

    def test_B03_delete_repository(self):
        self.check_rule(
            "powershell",
            {
                "command":
                "Remove-Item -Recurse -WhatIf "
                "..\\taskflow-knowledge-base"
            },
            "deny",
            "BLOCK B-03",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
