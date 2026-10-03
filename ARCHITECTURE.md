# Architecture

## Recommended Repository Shape

``` text
Coloring_Book_Factory/
├── SKILL.md
├── PRODUCT_PRD.md
├── ARCHITECTURE.md
├── WORKFLOW.md
├── CURSOR_HANDOFF.md
├── books/
│   └── <book_id>/
│       ├── book.json
│       ├── characters.json
│       ├── concepts/
│       ├── artwork/
│       │   ├── source/
│       │   └── approved/
│       └── notes/
├── factory/
│   ├── layout/
│   ├── pdf/
│   ├── cover/
│   ├── checks/
│   ├── metadata/
│   └── royalty/
├── templates/
├── tests/
├── output/
│   └── <book_id>/
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

## Separation of Concerns

-   `books/` = book-specific content and configuration.
-   `factory/` = reusable software.
-   `templates/` = reusable starting structures.
-   `output/` = generated deliverables only.
-   `slices/` = ordered implementation instructions.
-   Source artwork and generated/final artwork must not be mixed.

## Data First

Prefer explicit JSON/YAML-style configuration over values buried in
code. The factory should be able to build a different book by changing
data rather than rewriting the engine.

## Reproducibility

Generated outputs should be traceable to: - book configuration -
approved source assets - factory version - generation/build settings

## Safety Against Destructive Migration

When importing old HP/Codex material: - inventory first - copy first -
compare second - reorganize only after verification - never delete
originals as part of the initial migration
