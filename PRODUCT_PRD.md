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

## Baseline Publishing Specification

Master target for the first young-kid paperback coloring book:

1. **Age range:** 3 to 5 years old.
2. **Trim size:** 8.5 inches wide by 11 inches tall.
3. **Format:** paperback.
4. **Interior:** black-and-white ink on white paper.
5. **Content target:** fifty unique coloring illustrations.
6. **Printing layout:** one coloring illustration on the front of each
   sheet; leave the back blank to help prevent marker/crayon
   bleed-through from ruining another drawing.
7. **Total finished page target:** approximately 100 to 110 pages,
   including blank backs and front/end matter.
8. **Interior bleed:** none. Keep drawings and important content safely
   inside the trim edges (margin/safe area).
9. **Artwork style:** thick black outlines, simple shapes, large open
   coloring spaces, and low complexity designed for little kids.
10. **Interior file:** print-ready PDF of individual pages (not
    two-page spreads).
11. **Front matter:** title page, ownership / “This Book Belongs To”
    page, and copyright information.
12. **Cover:** separate print-ready cover file. Exact cover dimensions
    are not finalized until the interior is finished, because final page
    count determines spine width.

## First Customer Experience

The first book targets children ages 3–5 who are beginning to color. A
parent purchases the book; the child colors it.

## First Book

Original cozy dogs-and-cats theme (Etsy-forward life moments with friend
appearances by Coco and Luna).

## Known Character Source Material

Character concepts have been based on: - Etsy Penelope Sochi ---
daughter pit bull (first, middle, last) - Smoky (aka Smoking) --- gray
father pit bull - Fat Girl --- mother pit bull - Luna --- black cat -
Coco --- Frenchie

Photos/source references may exist in-repo under book artwork references.
Do not invent missing visual details for characters without refs.

## Functional Requirements

### Book definition

Each book needs a structured definition containing: - book ID/title -
audience - theme - trim/layout settings - printing layout rules -
character set - scene/illustration list - art status - publishing
metadata - output status

### Character system

Store reusable character records separately from scene prompts.
Character identity must survive across pages.

### Concept pipeline

Support: brief → scene concepts → approval → artwork → QC → layout.

### Artwork

Artwork must be replaceable without rebuilding the whole book. Keep
source art separate from final laid-out pages. Target fifty unique
approved illustrations for the first book.

### Layout

Support configurable KDP-oriented: - trim dimensions - margins -
bleed/no-bleed - safe areas - single-sided illustration + blank back -
front matter pages - page ordering

First-book defaults follow the Baseline Publishing Specification above.

### Interior output

Assemble approved pages into a print-ready interior PDF of individual
pages (title / belongs-to / copyright, then illustration + blank pairs).

### Cover output

Support a cover workflow separate from interior generation. Cover
dimensions must derive from final publishing parameters, including page
count and selected KDP settings.

### Quality control

Automated checks should catch, where technically possible: - missing
pages/assets - wrong dimensions - incorrect page count/order -
low-resolution raster assets - content outside safe areas - inconsistent
configuration - missing metadata - missing approvals - mismatched
blank-back / front-matter assembly

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
into final interior/cover deliverables under the baseline publishing
spec, checked automatically, and exported in an organized publishing
package.
