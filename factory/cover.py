"""Cover assembly derived from final interior publishing parameters."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from factory import __version__
from factory.io import load_book, save_json
from factory.layout import INCH_TO_PT, geometry_from_book


class CoverError(RuntimeError):
    """Cover cannot be built from current inputs."""


# Visible, configurable paperback spine assumptions (not buried magic).
# Amazon KDP white paper ~0.002252 in/page is a commonly cited estimate;
# operators may override via book.publishing.cover.spine_inches_per_page.
DEFAULT_SPINE_INCHES_PER_PAGE = 0.002252
DEFAULT_COVER_WRAP_IN = 0.125  # outside edge allowance beyond trim for wrap preview


def load_interior_page_count(book_id: str, repo_root: Path) -> int:
    manifest_path = repo_root / "output" / book_id / "build_manifest.json"
    if not manifest_path.is_file():
        raise CoverError(
            f"Interior build manifest required before cover: {manifest_path}"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    page_count = manifest.get("page_count")
    if not isinstance(page_count, int) or page_count < 1:
        raise CoverError("build_manifest.json missing valid page_count")
    return page_count


def cover_dimensions(
    book: dict[str, Any],
    *,
    page_count: int,
) -> dict[str, float]:
    geo = geometry_from_book(book)
    cover_cfg = ((book.get("publishing") or {}).get("cover") or {})
    spine_per_page = float(
        cover_cfg.get("spine_inches_per_page", DEFAULT_SPINE_INCHES_PER_PAGE)
    )
    wrap_in = float(cover_cfg.get("wrap_in", DEFAULT_COVER_WRAP_IN))
    spine_in = page_count * spine_per_page
    # Full wrap: back | spine | front, plus optional wrap margin on outsides.
    width_in = wrap_in + geo.trim_width_in + spine_in + geo.trim_width_in + wrap_in
    height_in = wrap_in + geo.trim_height_in + wrap_in
    return {
        "page_count": float(page_count),
        "trim_width_in": geo.trim_width_in,
        "trim_height_in": geo.trim_height_in,
        "spine_inches_per_page": spine_per_page,
        "spine_in": spine_in,
        "wrap_in": wrap_in,
        "width_in": width_in,
        "height_in": height_in,
        "dpi": float(geo.dpi),
    }


def _cover_source_dir(book_dir: Path) -> Path:
    path = book_dir / "artwork" / "cover" / "source"
    path.mkdir(parents=True, exist_ok=True)
    return path


def render_cover_source_png(
    book: dict[str, Any],
    dims: dict[str, float],
    dest: Path,
) -> Path:
    """Create an editable/source cover raster (placeholder art, original)."""
    dpi = int(dims["dpi"])
    width_px = int(round(dims["width_in"] * dpi))
    height_px = int(round(dims["height_in"] * dpi))
    wrap = int(round(dims["wrap_in"] * dpi))
    trim_w = int(round(dims["trim_width_in"] * dpi))
    spine = max(1, int(round(dims["spine_in"] * dpi)))

    img = Image.new("RGB", (width_px, height_px), "#f7f1e8")
    draw = ImageDraw.Draw(img)
    # Panel guides (source-editable cues, not final print marks only).
    back_x0 = wrap
    spine_x0 = wrap + trim_w
    front_x0 = spine_x0 + spine
    front_x1 = front_x0 + trim_w
    y0, y1 = wrap, height_px - wrap
    draw.rectangle([back_x0, y0, spine_x0, y1], outline="black", width=8)
    draw.rectangle([spine_x0, y0, front_x0, y1], outline="black", width=6)
    draw.rectangle([front_x0, y0, front_x1, y1], outline="black", width=8)

    try:
        font = ImageFont.load_default()
    except OSError:
        font = None

    title = book["title"]
    subtitle = (book.get("publishing") or {}).get("subtitle") or ""
    draw.text((front_x0 + 40, y0 + 80), title, fill="black", font=font)
    if subtitle:
        draw.text((front_x0 + 40, y0 + 140), subtitle, fill="black", font=font)
    draw.text((front_x0 + 40, y1 - 120), "COVER SOURCE (editable)", fill="black", font=font)
    draw.text((back_x0 + 40, y0 + 80), "BACK", fill="black", font=font)

    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, format="PNG")
    return dest


def build_cover(
    book_dir: Path | str,
    *,
    repo_root: Path | str | None = None,
) -> Path:
    book_dir = Path(book_dir).resolve()
    repo_root = Path(repo_root) if repo_root else book_dir.parents[1]
    book, _ = load_book(book_dir)
    page_count = load_interior_page_count(book["book_id"], repo_root)
    dims = cover_dimensions(book, page_count=page_count)

    source_dir = _cover_source_dir(book_dir)
    source_png = source_dir / "cover_wrap.png"
    # Preserve existing custom source if present; only generate when missing.
    if not source_png.is_file():
        render_cover_source_png(book, dims, source_png)

    out_dir = repo_root / "output" / book["book_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    cover_pdf = out_dir / f"{book['book_id']}_cover.pdf"

    width_pt = dims["width_in"] * INCH_TO_PT
    height_pt = dims["height_in"] * INCH_TO_PT
    c = canvas.Canvas(str(cover_pdf), pagesize=(width_pt, height_pt))
    with Image.open(source_png) as img:
        c.drawImage(
            ImageReader(img.convert("RGB")),
            0,
            0,
            width=width_pt,
            height=height_pt,
            preserveAspectRatio=False,
            mask="auto",
        )
    c.showPage()
    c.save()

    meta = {
        "book_id": book["book_id"],
        "factory_version": __version__,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "page_count_from_interior": page_count,
        "dimensions_in": dims,
        "source_png": str(source_png.relative_to(book_dir)),
        "cover_pdf": cover_pdf.name,
    }
    (out_dir / "cover_manifest.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )

    publishing = book.setdefault("publishing", {})
    cover_cfg = publishing.setdefault("cover", {})
    cover_cfg["source_path"] = str(source_png.relative_to(book_dir))
    cover_cfg["last_page_count"] = page_count
    save_json(book_dir / "book.json", book)
    return cover_pdf
