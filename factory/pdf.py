"""Assemble approved artwork into an interior PDF."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from factory import __version__
from factory.io import load_book
from factory.layout import geometry_from_book, ordered_scenes
from factory.schema import ArtStatus, OutputStatus


class BuildError(RuntimeError):
    """Interior build cannot proceed."""


DEFAULT_FRONT_MATTER = ["title", "belongs_to", "copyright"]


def output_dir_for(book_id: str, repo_root: Path | str | None = None) -> Path:
    root = Path(repo_root) if repo_root else Path.cwd()
    path = root / "output" / book_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def printing_options(book: dict[str, Any]) -> dict[str, Any]:
    printing = dict(book.get("printing") or {})
    printing.setdefault("format", "paperback")
    printing.setdefault("color", "black_and_white")
    printing.setdefault("blank_backs", False)
    printing.setdefault("front_matter", [])
    printing.setdefault("individual_pages", True)
    return printing


def expected_pdf_page_count(book: dict[str, Any]) -> int:
    scenes = ordered_scenes(book)
    opts = printing_options(book)
    front = list(opts.get("front_matter") or [])
    per_illustration = 2 if opts.get("blank_backs") else 1
    return len(front) + len(scenes) * per_illustration


def approved_image_path(book_dir: Path, scene: dict[str, Any]) -> Path:
    if scene.get("art_status") != ArtStatus.APPROVED.value:
        raise BuildError(f"scene {scene['scene_id']} is not approved for layout")
    artwork = scene.get("artwork") or {}
    rel = artwork.get("approved_path")
    if not rel:
        raise BuildError(f"scene {scene['scene_id']} has no approved_path")
    path = book_dir / rel
    if not path.is_file():
        raise BuildError(f"missing approved artwork: {path}")
    return path


def _draw_centered_text(
    c: canvas.Canvas,
    text: str,
    *,
    x_center: float,
    y: float,
    font: str = "Helvetica",
    size: int = 18,
) -> None:
    c.setFont(font, size)
    c.drawCentredString(x_center, y, text)


def _render_front_matter_page(
    c: canvas.Canvas,
    book: dict[str, Any],
    kind: str,
    geo,
) -> dict[str, Any]:
    width = geo.media_width_pt
    height = geo.media_height_pt
    cx = width / 2
    publishing = book.get("publishing") or {}
    c.setFillColorRGB(0, 0, 0)

    if kind == "title":
        _draw_centered_text(c, book["title"], x_center=cx, y=height * 0.62, font="Helvetica-Bold", size=28)
        subtitle = str(publishing.get("subtitle") or "").strip()
        if subtitle:
            _draw_centered_text(c, subtitle, x_center=cx, y=height * 0.55, size=14)
        _draw_centered_text(
            c,
            str(book.get("audience") or "Ages 3–5"),
            x_center=cx,
            y=height * 0.42,
            size=12,
        )
    elif kind == "belongs_to":
        _draw_centered_text(
            c,
            "This Book Belongs To",
            x_center=cx,
            y=height * 0.72,
            font="Helvetica-Bold",
            size=22,
        )
        # Ownership writing lines for a child/parent.
        left = geo.content_box_pt[0]
        right = geo.content_box_pt[2]
        y = height * 0.55
        for label in ("Name", "Age", "Date"):
            c.setFont("Helvetica", 12)
            c.drawString(left, y + 10, f"{label}:")
            c.line(left, y, right, y)
            y -= 48
    elif kind == "copyright":
        year = datetime.now(timezone.utc).year
        author = str(publishing.get("author") or "All rights reserved").strip()
        imprint = str(publishing.get("imprint") or "").strip()
        lines = [
            f"Copyright © {year}",
            author if author else "All rights reserved.",
            imprint,
            "For personal coloring use. All illustrations original.",
            "Printed in black and white on white paper.",
        ]
        y = height * 0.58
        for line in lines:
            if not line:
                continue
            _draw_centered_text(c, line, x_center=cx, y=y, size=11)
            y -= 22
    else:
        raise BuildError(f"unknown front matter kind: {kind}")

    c.showPage()
    return {"type": "front_matter", "kind": kind}


def _render_illustration_page(
    c: canvas.Canvas,
    book_dir: Path,
    scene: dict[str, Any],
    geo,
) -> dict[str, Any]:
    image_path = approved_image_path(book_dir, scene)
    x0, y0, x1, y1 = geo.content_box_pt
    content_w = x1 - x0
    content_h = y1 - y0

    with Image.open(image_path) as img:
        img = img.convert("RGB")
        iw, ih = img.size
        scale = min(content_w / iw, content_h / ih)
        draw_w = iw * scale
        draw_h = ih * scale
        dx = x0 + (content_w - draw_w) / 2
        dy = y0 + (content_h - draw_h) / 2
        c.drawImage(
            ImageReader(img),
            dx,
            dy,
            width=draw_w,
            height=draw_h,
            preserveAspectRatio=True,
            mask="auto",
        )

    c.showPage()
    return {
        "type": "illustration",
        "scene_id": scene["scene_id"],
        "illustration_number": scene["page_number"],
        "approved_path": str(image_path.relative_to(book_dir)),
        "placed_pt": {"x": dx, "y": dy, "width": draw_w, "height": draw_h},
    }


def _render_blank_page(c: canvas.Canvas) -> dict[str, Any]:
    # Intentionally empty back to reduce bleed-through of markers/crayons.
    c.showPage()
    return {"type": "blank_back"}


def build_interior_pdf(
    book_dir: Path | str,
    *,
    repo_root: Path | str | None = None,
) -> Path:
    book_dir = Path(book_dir).resolve()
    book, _ = load_book(book_dir)
    geo = geometry_from_book(book)
    scenes = ordered_scenes(book)
    if not scenes:
        raise BuildError("book has no scenes")

    opts = printing_options(book)
    out_dir = output_dir_for(book["book_id"], repo_root=repo_root or book_dir.parents[1])
    pdf_path = out_dir / f"{book['book_id']}_interior.pdf"
    manifest_path = out_dir / "build_manifest.json"

    c = canvas.Canvas(str(pdf_path), pagesize=(geo.media_width_pt, geo.media_height_pt))
    page_records: list[dict[str, Any]] = []
    pdf_page = 0

    for kind in list(opts.get("front_matter") or []):
        record = _render_front_matter_page(c, book, kind, geo)
        pdf_page += 1
        record["pdf_page"] = pdf_page
        page_records.append(record)

    for scene in scenes:
        record = _render_illustration_page(c, book_dir, scene, geo)
        pdf_page += 1
        record["pdf_page"] = pdf_page
        page_records.append(record)
        if opts.get("blank_backs"):
            blank = _render_blank_page(c)
            pdf_page += 1
            blank["pdf_page"] = pdf_page
            blank["after_scene_id"] = scene["scene_id"]
            page_records.append(blank)

    c.save()

    expected = expected_pdf_page_count(book)
    if pdf_page != expected:
        raise BuildError(f"PDF page count {pdf_page} != expected {expected}")

    book["output_status"] = OutputStatus.PARTIAL.value
    from factory.io import save_json

    save_json(book_dir / "book.json", book)

    illustration_ids = [s["scene_id"] for s in scenes]
    manifest = {
        "book_id": book["book_id"],
        "factory_version": __version__,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "interior_pdf": str(pdf_path.name),
        "page_count": pdf_page,
        "illustration_count": len(scenes),
        "expected_page_count": expected,
        "printing": opts,
        "layout": {
            "trim_width_in": geo.trim_width_in,
            "trim_height_in": geo.trim_height_in,
            "margin_in": geo.margin_in,
            "bleed_in": geo.bleed_in,
            "dpi": geo.dpi,
            "media_width_in": geo.media_width_in,
            "media_height_in": geo.media_height_in,
        },
        "illustration_order": illustration_ids,
        "pages": page_records,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return pdf_path
