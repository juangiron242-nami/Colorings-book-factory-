# Product Requirements Document

## Product

**Coloring Book Factory**

## Problem

Creating a coherent KDP coloring book requires much more than generating
pictures. Characters need consistency, scenes need age-appropriate
composition, pages need print-safe layout, books need repeatable
assembly, and final files need publishing checks. The factory should
make that workflow reproducible.

## Primary User

The operator/creator building and publishing original coloring books.

## First Customer Experience

The first book targets very young children who are barely beginning to
draw/color. A parent purchases the book; the child colors it.

## First Book

Original cozy dogs-and-cats theme.

Known prototype scenes: - Bed / cozy sharing scene - Garden scene -
Picnic scene - Rainy-day scene

A prior four-page prototype was developed around these scene concepts.

## Known Character Source Material

Character concepts have been based on: - Etsy --- daughter pit bull -
Smoky --- gray father pit bull - Fat Girl --- mother, deceased - Luna
--- black cat - Coco --- Frenchie

Photos/source references may exist outside this transfer package. Do not
invent missing visual details. Ask for or locate approved source images
before locking character models.

## Functional Requirements

### Book definition

Each book needs a structured definition containing: - book ID/title -
audience - theme - trim/layout settings - character set - scene list -
art status - publishing metadata - output status

### Character system

Store reusable character records separately from scene prompts.
Character identity must survive across pages.

### Concept pipeline

Support: brief → scene concepts → approval → artwork → QC → layout.

### Artwork

Artwork must be replaceable without rebuilding the whole book. Keep
source art separate from final laid-out pages.

### Layout

Support configurable KDP-oriented: - trim dimensions - margins -
bleed/no-bleed - safe areas - page ordering

Do not hard-code dimensions until the selected KDP format is confirmed
for the specific book.

### Interior output

Assemble approved pages into a print-ready interior PDF.

### Cover output

Support a cover workflow separate from interior generation. Cover
dimensions must derive from final publishing parameters, including page
count and selected KDP settings.

### Quality control

Automated checks should catch, where technically possible: - missing
pages/assets - wrong dimensions - incorrect page count/order -
low-resolution raster assets - content outside safe areas - inconsistent
configuration - missing metadata - missing approvals

### Publishing metadata

Prepare reusable structured metadata such as title/subtitle,
description, keywords/categories where applicable, author/imprint
fields, and edition/book identifiers.

### Economics

Include a royalty/profit calculator based on configurable list price,
printing cost, marketplace assumptions, and royalty rules. Keep
assumptions visible rather than burying constants in code.

## Non-Goals for Early Slices

-   Do not build every future genre/theme at once.
-   Do not automate publishing-account actions before the core factory
    reliably produces validated files.
-   Do not replace human approval of character likeness or page quality
    with an opaque automatic pass.

## Definition of Done

A new book can be created from a structured brief, populated with
reusable characters/scenes, supplied with approved artwork, assembled
into final interior/cover deliverables, checked automatically, and
exported in an organized publishing package.
