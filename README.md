# tablecheck

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CLI](https://img.shields.io/badge/CLI-ready-2ea043?style=for-the-badge)
![Zero Dependencies](https://img.shields.io/badge/Dependencies-0-4c1d95?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

</div>

**Validate Markdown table structure** — detect malformed tables, broken alignment rows, inconsistent column counts, and more. Zero dependencies.

---

## Why?

Markdown tables break silently:

- Alignment rows (`|---|:---:|`) get malformed characters that render as garbage.
- Header and body rows disagree on column count — cells shift and data misaligns.
- A table with no body rows renders empty but still passes most validators.

`tablecheck` scans your docs and flags every structural issue with a precise error code, so broken tables get caught in review — not after they ship to your readers.

## Install

```bash
pip install .
```

## Usage

```bash
tablecheck [paths...] [--verbose]
```

```bash
$ tablecheck README.md docs/
docs/guide.md:12: E003 — column alignment pattern is broken
docs/api.md:40: E004 — data row has different column count than header

2 table issue(s) found.
```

## What It Checks

| Code | Description |
| :--- | :--- |
| **E001** | Alignment row is malformed (invalid characters) |
| **E002** | Separator pipe count doesn't match header |
| **E003** | Column alignment pattern is broken |
| **E004** | Data row has different column count than header |
| **W001** | Table has no data rows |

## Exit Codes

- `0` — All tables valid
- `1` — One or more issues found
- `2` — Usage error

## Quality

Zero dependencies. Pure Python standard library. Uses `ruff`, `bandit`, and `pytest` in CI.

## License

MIT
