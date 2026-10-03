# Coloring Book Factory

Reusable factory for original Amazon KDP-ready children's coloring books.

Product intent and architecture live in:

- `SKILL.md`
- `PRODUCT_PRD.md`
- `ARCHITECTURE.md`
- `WORKFLOW.md`
- `slices/`

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
./scripts/gauntlet.sh
```

## Layout

- `books/` — book-specific content and configuration
- `factory/` — reusable software
- `templates/` — starter structures
- `tests/` — automated checks
- `output/` — generated deliverables only
