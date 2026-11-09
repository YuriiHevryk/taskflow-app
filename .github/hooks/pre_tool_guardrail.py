
import json
import re
import sys


SHELL_TOOLS = (
    "powershell", "bash", "terminal",
    "shell", "execute", "run_command"
)

WRITE_TOOLS = (
    "edit", "write", "create",
    "apply_patch", "replace", "str_replace"
)

DELETE_TOOLS = (
    "delete", "remove_file",
    "remove_directory", "unlink"
)


FORCE_PUSH = re.compile(
    r"\bgit(?:\.exe)?\b[^\r\n]*?\bpush\b[^\r\n]*?"
    r"(?:--force(?:-with-lease)?(?:=\S+)?(?=\s|$)|-f(?=\s|$))",
    re.IGNORECASE,
)

GIT_PUSH = re.compile(
    r"\bgit(?:\.exe)?\b[^\r\n]*?\bpush\b",
    re.IGNORECASE,
)

DELETE_COMMAND = re.compile(
    r"\b(?:rm|rmdir|rd|del|erase|unlink|remove-item)\b",
    re.IGNORECASE,
)

RECURSIVE = re.compile(
    r"(?:\s-rf\b|\s-fr\b|\s-r\b|"
    r"\s--recursive\b|\s-recurse\b|\s/s\b)",
    re.IGNORECASE,
)

DECISIONS_PATH = re.compile(
    r"\bDecisions[\\/]",
    re.IGNORECASE,
)

REPO_NAME = re.compile(
    r"\btaskflow-(?:app|knowledge-base)\b",
    re.IGNORECASE,
)

CORE_PATH = re.compile(
    r"\bconnector[\\/]server\.py\b",
    re.IGNORECASE,
)

DOC_PATH = re.compile(
    r"\bdocs[\\/][^\s\"']+\.md\b",
    re.IGNORECASE,
)

SAFE_STATUS = re.compile(
    r"git(?:\.exe)?"
    r"(?:\s+-C\s+(?:\"[^\"]+\"|'[^']+'|\S+))?"
    r"\s+status(?:\s+--short)?\s*",
    re.IGNORECASE,
)


def parse_args(value):
    if isinstance(value, str):
        if value.lstrip().startswith(("{", "[")):
            return json.loads(value)
    return value


def find_command(value):
    value = parse_args(value)

    if isinstance(value, dict):
        for key in (
            "command", "commandLine",
            "cmd", "script", "code"
        ):
            if key in value:
                return find_command(value[key])
        return ""

    if isinstance(value, list):
        return "\n".join(
            find_command(item) for item in value
        )

    return value if isinstance(value, str) else ""


def decision(kind, code, reason):
    return {
        "permissionDecision": kind,
        "permissionDecisionReason": f"{code}: {reason}"
    }


def check(event):
    name = str(
        event.get("toolName", event.get("tool_name", ""))
    ).casefold()

    args = parse_args(
        event.get("toolArgs", event.get("tool_input", {}))
    )

    command = find_command(args)

    payload = command + "\n" + json.dumps(
        args, ensure_ascii=False
    )

    shell = any(
        part in name for part in SHELL_TOOLS
    )

    write = any(
        part in name for part in WRITE_TOOLS
    )

    delete_tool = any(
        part in name for part in DELETE_TOOLS
    )

    delete_action = (
        (shell and bool(DELETE_COMMAND.search(command)))
        or delete_tool
        or "*** Delete File:" in payload
    )

    # BLOCK RULES

    # B-01: Force push
    if shell and FORCE_PUSH.search(command):
        return decision(
            "deny",
            "BLOCK B-01",
            "Force push is prohibited by TaskFlow guardrails."
        )

    # B-02: Delete architecture decisions
    if delete_action and DECISIONS_PATH.search(payload):
        return decision(
            "deny",
            "BLOCK B-02",
            "Deleting architecture decisions is prohibited."
        )

    # B-03: Delete repositories recursively
    if REPO_NAME.search(payload):
        if delete_tool or (
            shell
            and DELETE_COMMAND.search(command)
            and RECURSIVE.search(command)
        ):
            return decision(
                "deny",
                "BLOCK B-03",
                "Recursive deletion of TaskFlow repositories "
                "is prohibited."
            )

    # WARN RULES

    # W-02: Write notes via MCP
    if "ingest_note" in name:
        return decision(
            "ask",
            "WARN W-02",
            "Confirm the Obsidian note change "
            "before continuing."
        )

    # W-01: Modify MCP server code
    if CORE_PATH.search(payload):
        shell_write = shell and re.search(
            r"\b(?:set-content|add-content|out-file|sed)\b|>",
            command,
            re.IGNORECASE,
        )

        if write or shell_write:
            return decision(
                "ask",
                "WARN W-01",
                "Confirm changes to connector/server.py."
            )

    # W-03: Normal Git push
    if shell and GIT_PUSH.search(command):
        return decision(
            "ask",
            "WARN W-03",
            "Confirm Git push before continuing."
        )

    # ALLOW RULES

    # A-02: Search Obsidian
    if "search_notes" in name:
        return {"permissionDecision": "allow"}

    # A-01: Read documentation
    if ("view" in name or "read" in name):
        if DOC_PATH.search(payload):
            return {"permissionDecision": "allow"}

    # A-03: Check Git status
    if shell and SAFE_STATUS.fullmatch(command.strip()):
        return {"permissionDecision": "allow"}

    # Other actions use default permissions
    return {}


def main():
    try:
        event = json.load(sys.stdin)
        result = check(event)

        print(json.dumps(result, ensure_ascii=True))

    except Exception as error:
        result = decision(
            "deny",
            "BLOCK",
            "Guardrail validation failed: "
            + type(error).__name__
        )

        print(json.dumps(result))


if __name__ == "__main__":
    main()
