# Project Inventory — Slice 00

Generated from the empty GitHub seed repo plus the
`Coloring_Book_Factory_Cursor_Transfer` handoff package.

## Current tree

```text
.
├── ARCHITECTURE.md          # imported from transfer package
├── CURSOR_HANDOFF.md        # imported from transfer package
├── PRODUCT_PRD.md           # imported from transfer package
├── PROJECT_INVENTORY.md     # this file
├── README.md                # seed: "Colorings-book-factory-"
├── SKILL.md                 # imported from transfer package
├── WORKFLOW.md              # imported from transfer package
└── slices/
    ├── 00_inventory.md
    ├── 01_schema.md
    ├── 02_first_book.md
    ├── 03_art_pipeline.md
    ├── 04_layout_pdf.md
    ├── 05_qc.md
    ├── 06_cover.md
    ├── 07_metadata_royalty.md
    └── 08_release_package.md
```

## What works

- Transfer package product intent, architecture, workflow, and slice
  instructions are present in-repo as source of truth.
- Git remote is connected; `main` contains only the seed README.

## What is incomplete / missing

Compared to `PRODUCT_PRD.md` and `ARCHITECTURE.md`, nothing of the
factory exists yet:

| Area | Status |
|------|--------|
| `books/` book definitions | Missing |
| `factory/` layout/pdf/cover/checks/metadata/royalty | Missing |
| `templates/` | Missing |
| `tests/` | Missing |
| `output/` | Missing |
| Four-page dogs-and-cats prototype | Not in repo or transfer zip |
| Character/source images | Not in repo or transfer zip |
| Generated PDFs / covers | Not in repo or transfer zip |
| Book/config/metadata runtime files | Missing |
| Dependencies / entry points | None yet |
| Runtime / build command | None yet |

## Valuable assets to preserve

- Seed `README.md` (history only; will be updated additively later).
- All transfer docs: `SKILL.md`, `PRODUCT_PRD.md`, `ARCHITECTURE.md`,
  `WORKFLOW.md`, `CURSOR_HANDOFF.md`, and `slices/*.md`.
- Known first-book character names and scene concepts (documented in
  PRD/slices; no visual references shipped here).

## Duplicates / abandoned experiments

None found. The repository was a greenfield seed.

## Items that need more context

- Approved character visual references (Etsy, Smoky, Fat Girl, Luna,
  Coco) are named but not provided; do not invent likeness details.
- Confirmed KDP trim/bleed settings for the first book are not locked;
  layout must stay configuration-driven.
- Prior four-page prototype artwork/PDF is referenced in the PRD but
  was not included in this transfer package.

## Recommended next slice

`slices/01_schema.md` — define book/character/scene schemas with
validation and a minimal test fixture before any art or PDF work.
