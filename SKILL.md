# Coloring Book Factory --- Master Skill

## Mission

Build an original, standalone **Coloring Book Factory** that can
repeatedly produce Amazon KDP-ready children's coloring books from
reusable characters, themes, and scene concepts.

The system is not just one coloring book. It is a reusable factory:
define a book, define characters and scenes, generate/approve art,
assemble the interior and cover, run quality checks, calculate
publishing economics, and export final deliverables.

## Current Product Direction

The first book is an original cozy **dogs-and-cats** coloring book for
very young children who are only beginning to color.

The parent is the buyer. The child is the user.

### First-book scene examples

-   Puppy and kitten sharing a bed
-   Garden play
-   Picnic
-   Rainy-day relaxation

## Art Rules

For the first young-child book: - Very thick, clean black outlines -
Large open coloring areas - Simple recognizable shapes - Minimal
clutter - One obvious subject/activity per page - No tiny decorative
detail that makes coloring frustrating - Pages must remain legible when
printed - Characters should remain visually consistent across scenes -
Art must be original and commercially usable

## Factory Capabilities

The finished system should support: 1. Recurring characters and reusable
character definitions 2. Themes and book briefs 3. Scene/concept
generation and approval 4. Coloring-page art generation/import 5.
Consistency checks 6. KDP trim size, margins, bleed, and layout
configuration 7. Interior PDF assembly 8. Cover assembly 9. Automated
QC/preflight 10. Metadata preparation 11. Royalty/profit calculations
12. Reusable book templates 13. Organized output packages for publishing

## Engineering Principle

Work in **small vertical slices**. Each slice must produce a testable
result. Do not attempt a giant rewrite.

For every slice: 1. Read the product requirements. 2. Inspect existing
files before changing them. 3. State the smallest useful outcome. 4.
Implement only that slice. 5. Run its checks/tests. 6. Document what
changed. 7. Stop at the slice boundary unless explicitly told to
continue.

## Preservation Rule

Never delete or overwrite original project assets merely to reorganize
the project. Prefer additive migration and explicit versioning.

## Source of Truth

The repository should contain the product intent, architecture,
execution slices, book definitions, character definitions, art inputs,
generated outputs, and QC rules so another coding agent can continue
without relying on chat history.
