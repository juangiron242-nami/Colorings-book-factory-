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


def output_dir_for(book_id: str, repo_root: Path | str | None = None) -> Path:
    root = Path(repo_root) if repo_root else Path.cwd()
    path = root / "output" / book_id
    path.mkdir(parents=True, exist_ok=True)
    return path


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

    out_dir = output_dir_for(book["book_id"], repo_root=repo_root or book_dir.parents[1])
    pdf_path = out_dir / f"{book['book_id']}_interior.pdf"
    manifest_path = out_dir / "build_manifest.json"

    c = canvas.Canvas(str(pdf_path), pagesize=(geo.media_width_pt, geo.media_height_pt))
    page_records: list[dict[str, Any]] = []

    for scene in scenes:
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
            # Center within safe content box.
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

        page_records.append(
            {
                "page_number": scene["page_number"],
                "scene_id": scene["scene_id"],
                "approved_path": str(image_path.relative_to(book_dir)),
                "placed_pt": {
                    "x": dx,
                    "y": dy,
                    "width": draw_w,
                    "height": draw_h,
                },
            }
        )
        c.showPage()

    c.save()

    book["output_status"] = OutputStatus.PARTIAL.value
    from factory.io import save_json

    save_json(book_dir / "book.json", book)

    manifest = {
        "book_id": book["book_id"],
        "factory_version": __version__,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "interior_pdf": str(pdf_path.name),
        "page_count": len(page_records),
        "layout": {
            "trim_width_in": geo.trim_width_in,
            "trim_height_in": geo.trim_height_in,
            "margin_in": geo.margin_in,
            "bleed_in": geo.bleed_in,
            "dpi": geo.dpi,
            "media_width_in": geo.media_width_in,
            "media_height_in": geo.media_height_in,
        },
        "pages": page_records,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return pdf_path
