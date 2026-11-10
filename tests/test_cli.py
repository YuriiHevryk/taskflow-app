import pytest

from taskflow.cli import default_database_path, main


def test_cli_help_is_available(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--help"])

    assert exit_info.value.code == 0
    assert "Create and list TaskFlow tasks" in capsys.readouterr().out


def test_cli_add_and_list_across_invocations(tmp_path, capsys):
    database = tmp_path / "tasks.sqlite3"

    assert main(
        [
            "--database",
            str(database),
            "add",
            "--title",
            "Write tests",
            "--description",
            "Cover the CLI",
            "--priority",
            "high",
            "--status",
            "planned",
            "--due-date",
            "2026-11-20",
        ]
    ) == 0
    assert "Created task 1: Write tests" in capsys.readouterr().out

    assert main(["--database", str(database), "list"]) == 0
    output = capsys.readouterr().out
    assert "Write tests" in output
    assert "Cover the CLI" in output
    assert "high" in output
    assert "planned" in output
    assert "2026-11-20" in output


def test_cli_reports_invalid_input_without_writing(tmp_path, capsys):
    database = tmp_path / "tasks.sqlite3"

    assert main(
        [
            "--database",
            str(database),
            "add",
            "--title",
            "   ",
            "--description",
            "",
            "--priority",
            "medium",
            "--status",
            "planned",
        ]
    ) == 2
    assert "Invalid task: Title must not be empty." in capsys.readouterr().err

    assert main(["--database", str(database), "list"]) == 0
    assert "No tasks found." in capsys.readouterr().out


def test_cli_reports_database_errors(tmp_path, capsys):
    database_directory = tmp_path / "database-directory"
    database_directory.mkdir()

    assert main(["--database", str(database_directory), "list"]) == 1
    assert "Unable to access task storage:" in capsys.readouterr().err


def test_cli_rejects_invalid_date_without_writing(tmp_path, capsys):
    database = tmp_path / "tasks.sqlite3"

    assert main(
        [
            "--database",
            str(database),
            "add",
            "--title",
            "Task",
            "--description",
            "",
            "--priority",
            "medium",
            "--status",
            "planned",
            "--due-date",
            "not-a-date",
        ]
    ) == 2
    assert "Due date must use YYYY-MM-DD format." in capsys.readouterr().err

    assert main(["--database", str(database), "list"]) == 0
    assert "No tasks found." in capsys.readouterr().out


@pytest.mark.parametrize("required_option", ["--priority", "--status"])
def test_cli_requires_explicit_priority_and_status(
    required_option, tmp_path, capsys
):
    database = tmp_path / "tasks.sqlite3"
    arguments = [
        "--database",
        str(database),
        "add",
        "--title",
        "Task",
        "--description",
        "",
        "--priority",
        "medium",
        "--status",
        "planned",
    ]
    option_index = arguments.index(required_option)
    del arguments[option_index : option_index + 2]

    with pytest.raises(SystemExit) as exit_info:
        main(arguments)

    assert exit_info.value.code == 2
    error = capsys.readouterr().err
    assert required_option in error
    assert not database.exists()


def test_default_database_path_uses_windows_user_data_directory(
    monkeypatch, tmp_path
):
    monkeypatch.setattr("taskflow.cli.sys.platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local App Data"))

    assert default_database_path() == (
        tmp_path / "Local App Data" / "TaskFlow" / "tasks.sqlite3"
    )


def test_default_database_path_uses_absolute_xdg_data_home(
    monkeypatch, tmp_path
):
    monkeypatch.setattr("taskflow.cli.sys.platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg-data"))

    assert default_database_path() == (
        tmp_path / "xdg-data" / "TaskFlow" / "tasks.sqlite3"
    )


def test_default_database_path_ignores_relative_xdg_data_home(
    monkeypatch, tmp_path
):
    monkeypatch.setattr("taskflow.cli.sys.platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", "relative-data")
    monkeypatch.setattr("taskflow.cli.Path.home", lambda: tmp_path)

    assert default_database_path() == (
        tmp_path / ".local" / "share" / "TaskFlow" / "tasks.sqlite3"
    )


def test_default_database_path_uses_macos_application_support(
    monkeypatch, tmp_path
):
    monkeypatch.setattr("taskflow.cli.sys.platform", "darwin")
    monkeypatch.setattr("taskflow.cli.Path.home", lambda: tmp_path)

    assert default_database_path() == (
        tmp_path
        / "Library"
        / "Application Support"
        / "TaskFlow"
        / "tasks.sqlite3"
    )
