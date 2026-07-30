"""tablecheck — Validate Markdown table structure from your terminal."""

import argparse
import re
import sys
from pathlib import Path

TABLE_RE = re.compile(r"^\|.+\|\s*$", re.MULTILINE)
PIPE_COUNT_RE = re.compile(r"\|")

IssueCode = str


class TableIssue:
    def __init__(self, file: str, line: int, code: IssueCode, message: str):
        self.file = file
        self.line = line
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: [{self.code}] {self.message}"


def find_tables(text: str) -> list[tuple[int, int, list[str]]]:
    lines = text.split("\n")
    tables: list[tuple[int, int, list[str]]] = []
    i = 0
    while i < len(lines):
        if TABLE_RE.match(lines[i]):
            start = i
            rows: list[str] = []
            while i < len(lines) and TABLE_RE.match(lines[i]):
                rows.append(lines[i])
                i += 1
            if len(rows) >= 2:
                tables.append((start + 1, start + len(rows), rows))
        else:
            i += 1
    return tables


def validate_table(
    rows: list[str], start_line: int, file: str
) -> list[TableIssue]:
    issues: list[TableIssue] = []

    header = rows[0]
    header_pipes = len(PIPE_COUNT_RE.findall(header))

    sep = rows[1]
    sep_pipes = len(PIPE_COUNT_RE.findall(sep))

    if header_pipes != sep_pipes:
        issues.append(
            TableIssue(
                file,
                start_line + 1,
                "E002",
                f"Separator has {sep_pipes} pipes but header has {header_pipes}",
            )
        )

    col_count = header_pipes - 1
    has_bad_cell = False

    sep_cells = sep.strip("|").split("|")
    for ci, cell in enumerate(sep_cells):
        cell = cell.strip()
        if cell and not re.fullmatch(r":?-{3,}:?", cell):
            has_bad_cell = True
            issues.append(
                TableIssue(
                    file,
                    start_line + 1,
                    "E003",
                    f"Column {ci + 1} alignment '{cell}' must match :?---+:? pattern",
                )
            )

    if not has_bad_cell and header_pipes == sep_pipes:
        pass
    elif not has_bad_cell:
        issues.append(
            TableIssue(
                file,
                start_line + 1,
                "E001",
                "Alignment row pipe count doesn't match header",
            )
        )

    data_rows = rows[2:]
    for ri, row in enumerate(data_rows):
        row_pipes = len(PIPE_COUNT_RE.findall(row))
        if row_pipes != header_pipes:
            issues.append(
                TableIssue(
                    file,
                    start_line + 2 + ri,
                    "E004",
                    f"Row has {row_pipes - 1} columns but header has {col_count}",
                )
            )

    if not data_rows:
        issues.append(
            TableIssue(
                file, start_line, "W001", "Table has no data rows (header + separator only)"
            )
        )

    return issues


def check_file(filepath: Path) -> tuple[int, int, list[TableIssue]]:
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return 1, 0, [TableIssue(str(filepath), 1, "F001", f"Cannot read file: {e}")]
    tables = find_tables(text)
    all_issues: list[TableIssue] = []
    for start, end, rows in tables:
        all_issues.extend(validate_table(rows, start, str(filepath)))
    return 0 if not all_issues else 1, len(tables), all_issues


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate Markdown table structure"
    )
    parser.add_argument("paths", nargs="+", help="Markdown files or directories to check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed report")
    args = parser.parse_args()

    files: list[Path] = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            files.extend(path.rglob("*.md"))
        else:
            files.append(path)

    if not files:
        print("No Markdown files found.")
        sys.exit(0)

    total_tables = 0
    total_issues = 0
    file_count = 0
    all_issues: list[TableIssue] = []

    for fpath in sorted(set(files)):
        rc, ntables, issues = check_file(fpath)
        if issues:
            file_count += 1
            all_issues.extend(issues)
        total_tables += ntables
        total_issues += len(issues)

    if args.verbose:
        print("─" * 55)
        print("  tablecheck — Markdown Table Report")
        print("─" * 55)
        print(f"  Files scanned     : {len(files)}")
        print(f"  Files with issues : {file_count}")
        print(f"  Tables found      : {total_tables}")
        print(f"  Total issues      : {total_issues}")

    if all_issues:
        current_file = ""
        for issue in all_issues:
            if args.verbose:
                if issue.file != current_file:
                    current_file = issue.file
                    print(f"\n  {issue.file}")
                print(f"    {issue.line:>4}  [{issue.code}] {issue.message}")
            else:
                print(str(issue))

    if args.verbose:
        print(f"\n  {'All tables valid.' if total_issues == 0 else f'{total_issues} issue(s) found across {file_count} file(s).'}")

    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
