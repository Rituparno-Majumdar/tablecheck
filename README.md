# tablecheck

Validate Markdown table structure — detect malformed tables, broken alignment rows, inconsistent column counts, and more.

## Quick Start

```bash
pip install -e /root/tablecheck

# Check specific files
tablecheck README.md docs/*.md

# Check entire directory
tablecheck docs/ --verbose
```

## What It Checks

| Code | Description |
| :--- | :--- |
| **E001** | Alignment row is malformed (invalid characters) |
| **E002** | Separator pipe count doesn't match header |
| **E003** | Column alignment pattern is broken |
| **E004** | Data row has different column count than header |
| **W001** | Table has no data rows |

Zero dependencies. Pure Python standard library.

## Exit Codes

- `0` — All tables valid
- `1` — One or more issues found

## License

MIT
