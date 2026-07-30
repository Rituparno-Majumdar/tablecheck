"""Tests for tablecheck — Markdown table structure validator."""

from pathlib import Path
from tablecheck.cli import find_tables, validate_table, check_file


def test_find_tables_no_tables():
    text = "Just some text\n\nNo tables here\n"
    assert find_tables(text) == []


def test_find_tables_finds_table():
    text = "Before\n| a | b |\n| --- | --- |\n| 1 | 2 |\nAfter"
    tables = find_tables(text)
    assert len(tables) == 1
    assert tables[0][0] == 2  # start line


def test_valid_table_no_issues():
    rows = ["| a | b |", "| --- | --- |", "| 1 | 2 |"]
    issues = validate_table(rows, 1, "test.md")
    assert len(issues) == 0


def test_bad_separator():
    rows = ["| a | b |", "| xxx | yyy |", "| 1 | 2 |"]
    issues = validate_table(rows, 1, "test.md")
    codes = {i.code for i in issues}
    assert "E003" in codes


def test_column_mismatch():
    rows = ["| a | b | c |", "| --- | --- |", "| 1 | 2 | 3 |"]
    issues = validate_table(rows, 1, "test.md")
    assert any(i.code == "E002" for i in issues)


def test_bad_alignment_column():
    rows = ["| a | b |", "| --- | bad |", "| 1 | 2 |"]
    issues = validate_table(rows, 1, "test.md")
    assert any(i.code == "E003" for i in issues)


def test_row_column_count_mismatch():
    rows = ["| a | b |", "| --- | --- |", "| 1 | 2 | 3 |"]
    issues = validate_table(rows, 1, "test.md")
    assert any(i.code == "E004" for i in issues)


def test_empty_table_warning():
    rows = ["| a | b |", "| --- | --- |"]
    issues = validate_table(rows, 1, "test.md")
    assert any(i.code == "W001" for i in issues)


def test_check_file_valid(tmp_path: Path):
    f = tmp_path / "test.md"
    f.write_text("| a | b |\n| --- | --- |\n| 1 | 2 |\n")
    rc, ntables, issues = check_file(f)
    assert rc == 0
    assert ntables == 1
    assert len(issues) == 0


def test_check_file_invalid(tmp_path: Path):
    f = tmp_path / "bad.md"
    f.write_text("| a | b |\n| xxx | yyy |\n| 1 | 2 |\n")
    rc, ntables, issues = check_file(f)
    assert rc == 1
    assert len(issues) >= 1


def test_colon_alignment_valid():
    rows = ["| a | b | c |", "| :--- | :---: | ---: |", "| 1 | 2 | 3 |"]
    issues = validate_table(rows, 1, "test.md")
    assert len(issues) == 0


def test_multiple_tables():
    text = "| h1 | h2 |\n| --- | --- |\n| d1 | d2 |\n\n| x |\n| --- |\n| y |\n"
    tables = find_tables(text)
    assert len(tables) == 2
