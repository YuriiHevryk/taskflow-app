import logging
import re
import subprocess
import sys
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from mcp.server import MCPServer

mcp = MCPServer("TaskFlow Vault")

VAULT_PATH = Path(__file__).resolve().parents[2] / "taskflow-knowledge-base"


@mcp.tool()
def ping() -> str:
    """Перевірити роботу MCP-сервера."""
    return "TaskFlow MCP server is working"


@mcp.tool()
def search_notes(query: str) -> str:
    """Шукати релевантні фрагменти нотаток через векторний індекс."""

    query = query.strip()

    if not query:
        return "Помилка: порожній пошуковий запит."

    try:
        with redirect_stdout(sys.stderr):
            if __package__:
                from .rag_index import semantic_search
            else:
                from rag_index import semantic_search

            return semantic_search(query)
    except Exception as error:
        logging.getLogger(__name__).exception(
            "Semantic search failed"
        )
        return f"Помилка векторного пошуку: {error}"


NOTE_FOLDERS = {
    "concept": "Concepts",
    "component": "Components",
    "decision": "Decisions",
    "glossary": "Glossary",
}


def run_vault_git(*arguments: str) -> str:
    """Виконати Git-команду в репозиторії Obsidian."""

    result = subprocess.run(
        ["git", "-C", str(VAULT_PATH), *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(message)

    return result.stdout.strip()


@mcp.tool()
def ingest_note(
    title: str,
    note_type: str,
    content: str,
    links: list[str] | None = None,
    approved: bool = False,
) -> str:
    """Створити або оновити нотатку Obsidian та синхронізувати Git."""

    if not approved:
        return "Потрібне підтвердження користувача для запису."

    if note_type not in NOTE_FOLDERS:
        return "Помилка: невідомий тип нотатки."

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _-]{0,79}", title):
        return "Помилка: некоректна назва нотатки."

    if not content.strip():
        return "Помилка: порожній вміст."

    if not VAULT_PATH.is_dir():
        return "Помилка: Obsidian vault не знайдено."

    folder = VAULT_PATH / NOTE_FOLDERS[note_type]
    target = folder / f"{title}.md"

    if not target.resolve().is_relative_to(VAULT_PATH.resolve()):
        return "Помилка: некоректний шлях."

    try:
        status = run_vault_git("status", "--porcelain")

        if status:
            return (
                "Помилка: у репозиторії vault є незбережені "
                "зміни Git. Спочатку перевір їх."
            )

        run_vault_git("pull", "--ff-only", "origin", "main")

        old_text = ""

        if target.exists():
            old_text = target.read_text(encoding="utf-8")

        created = date.today().isoformat()

        if old_text:
            match = re.search(
                r"(?m)^created:\s*(\d{4}-\d{2}-\d{2})",
                old_text,
            )
            if match:
                created = match.group(1)

        metadata = (
            "---\n"
            f"type: {note_type}\n"
            f"created: {created}\n"
            "tags:\n"
            "  - taskflow\n"
            f"  - {note_type}\n"
        )

        if note_type == "decision":
            metadata += "status: accepted\n"

        metadata += "---\n\n"

        body = f"# {title}\n\n{content.strip()}\n"

        if links:
            body += "\n## Пов'язані нотатки\n\n"
            for link in links:
                if not re.fullmatch(
                    r"[A-Za-z0-9][A-Za-z0-9 _-]{0,79}",
                    link,
                ):
                    return "Помилка: некоректна назва посилання."
                body += f"- [[{link}]]\n"

        new_text = metadata + body

        if new_text == old_text:
            return f"Без змін: {target.name}"

        folder.mkdir(parents=True, exist_ok=True)
        target.write_text(new_text, encoding="utf-8")

        relative_path = target.relative_to(VAULT_PATH).as_posix()

        run_vault_git("add", "--", relative_path)
        run_vault_git("commit", "-m", f"docs: ingest {title}")
        run_vault_git("push", "origin", "main")

        action = "updated" if old_text else "created"

        return (
            f"Успішно: {action}\n"
            f"Файл: {relative_path}\n"
            "Git commit і push виконано."
        )

    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        return f"Помилка синхронізації: {error}"


if __name__ == "__main__":
    mcp.run()