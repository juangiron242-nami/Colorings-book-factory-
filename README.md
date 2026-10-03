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

## Build the first book

```bash
source .venv/bin/activate
cbf validate books/cozy-dogs-cats
cbf build-interior books/cozy-dogs-cats
cbf qc books/cozy-dogs-cats
cbf build-cover books/cozy-dogs-cats
cbf metadata books/cozy-dogs-cats
cbf royalty books/cozy-dogs-cats
cbf release books/cozy-dogs-cats
```

Release package lands in `output/cozy-dogs-cats/release/`.

## Layout

- `books/` — book-specific content and configuration
- `factory/` — reusable software
- `templates/` — starter structures
- `tests/` — automated checks
- `output/` — generated deliverables only (gitignored)
- `scripts/gauntlet.sh` — full verification loop

## Notes

- First-book artwork currently uses clearly labeled **placeholders** until
  approved character likeness references are provided.
- Layout trim/bleed values are configuration-driven and provisional until
  the selected KDP format is confirmed.
