"""Artwork pipeline: source → review → approved."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from factory.io import load_book, load_json, save_json
from factory.schema import ArtStatus, ApprovalStatus


@dataclass
class ArtIssue:
    code: str
    message: str
    scene_id: str | None = None
    severity: str = "error"


@dataclass
class ArtCheckResult:
    ok: bool
    issues: list[ArtIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "issues": [asdict(issue) for issue in self.issues],
        }


def book_art_dirs(book_dir: Path | str) -> tuple[Path, Path]:
    book_dir = Path(book_dir)
    source = book_dir / "artwork" / "source"
    approved = book_dir / "artwork" / "approved"
    source.mkdir(parents=True, exist_ok=True)
    approved.mkdir(parents=True, exist_ok=True)
    return source, approved


def _scene_by_id(book: dict[str, Any], scene_id: str) -> dict[str, Any]:
    for scene in book["scenes"]:
        if scene["scene_id"] == scene_id:
            return scene
    raise KeyError(f"unknown scene_id: {scene_id}")


def import_source(
    book_dir: Path | str,
    scene_id: str,
    source_file: Path | str,
    *,
    overwrite: bool = False,
) -> Path:
    """Copy an original file into artwork/source without mutating the original."""
    book_dir = Path(book_dir)
    book, _ = load_book(book_dir)
    scene = _scene_by_id(book, scene_id)
    source_dir, _ = book_art_dirs(book_dir)
    source_file = Path(source_file)
    if not source_file.is_file():
        raise FileNotFoundError(source_file)

    dest = source_dir / f"{scene_id}{source_file.suffix.lower()}"
    if dest.exists() and not overwrite:
        raise FileExistsError(f"source already exists (refusing overwrite): {dest}")

    shutil.copy2(source_file, dest)
    scene.setdefault("artwork", {})
    scene["artwork"]["source_path"] = str(dest.relative_to(book_dir))
    scene["art_status"] = ArtStatus.SOURCE.value
    scene["approval_status"] = scene.get("approval_status", ApprovalStatus.IN_REVIEW.value)
    if scene["approval_status"] == ApprovalStatus.APPROVED.value:
        # Concept approval is separate from art approval; keep art in review.
        pass
    _refresh_book_art_status(book)
    save_json(book_dir / "book.json", book)
    return dest


def approve_artwork(
    book_dir: Path | str,
    scene_id: str,
    *,
    copy_from_source: bool = True,
) -> Path:
    """Promote source art to approved/ for layout. Source file is preserved."""
    book_dir = Path(book_dir)
    book, _ = load_book(book_dir)
    scene = _scene_by_id(book, scene_id)
    source_dir, approved_dir = book_art_dirs(book_dir)
    artwork = scene.setdefault("artwork", {})
    source_rel = artwork.get("source_path")
    if not source_rel:
        raise FileNotFoundError(f"no source_path recorded for scene {scene_id}")
    source_path = book_dir / source_rel
    if not source_path.is_file():
        # Fall back to conventional name if JSON path is stale but file exists.
        candidates = list(source_dir.glob(f"{scene_id}.*"))
        if not candidates:
            raise FileNotFoundError(source_path)
        source_path = candidates[0]
        artwork["source_path"] = str(source_path.relative_to(book_dir))

    dest = approved_dir / source_path.name
    if copy_from_source:
        shutil.copy2(source_path, dest)
    elif not dest.is_file():
        raise FileNotFoundError(dest)

    artwork["approved_path"] = str(dest.relative_to(book_dir))
    scene["art_status"] = ArtStatus.APPROVED.value
    _refresh_book_art_status(book)
    save_json(book_dir / "book.json", book)
    return dest


def replace_source(
    book_dir: Path | str,
    scene_id: str,
    new_source: Path | str,
) -> Path:
    """Replace one page's source art. Clears approval for that page only."""
    book_dir = Path(book_dir)
    book, _ = load_book(book_dir)
    scene = _scene_by_id(book, scene_id)
    source_dir, approved_dir = book_art_dirs(book_dir)
    new_source = Path(new_source)

    # Preserve prior source with a .bak suffix rather than deleting.
    existing = list(source_dir.glob(f"{scene_id}.*"))
    for path in existing:
        bak = path.with_suffix(path.suffix + ".bak")
        if bak.exists():
            bak.unlink()
        path.rename(bak)

    dest = source_dir / f"{scene_id}{new_source.suffix.lower()}"
    shutil.copy2(new_source, dest)

    # Remove approved copy for this scene only; leave other pages alone.
    for path in approved_dir.glob(f"{scene_id}.*"):
        path.unlink()

    scene.setdefault("artwork", {})
    scene["artwork"]["source_path"] = str(dest.relative_to(book_dir))
    scene["artwork"]["approved_path"] = None
    scene["art_status"] = ArtStatus.SOURCE.value
    _refresh_book_art_status(book)
    save_json(book_dir / "book.json", book)
    return dest


def _refresh_book_art_status(book: dict[str, Any]) -> None:
    statuses = {scene.get("art_status", ArtStatus.MISSING.value) for scene in book["scenes"]}
    if statuses == {ArtStatus.APPROVED.value}:
        book["art_status"] = ArtStatus.APPROVED.value
    elif ArtStatus.MISSING.value in statuses and len(statuses) == 1:
        book["art_status"] = ArtStatus.MISSING.value
    elif ArtStatus.APPROVED.value in statuses or ArtStatus.SOURCE.value in statuses:
        book["art_status"] = ArtStatus.IN_REVIEW.value
    else:
        book["art_status"] = ArtStatus.IN_REVIEW.value


def check_missing_assets(book_dir: Path | str) -> ArtCheckResult:
    book_dir = Path(book_dir)
    book, _ = load_book(book_dir)
    issues: list[ArtIssue] = []
    for scene in book["scenes"]:
        sid = scene["scene_id"]
        artwork = scene.get("artwork") or {}
        source_rel = artwork.get("source_path")
        if not source_rel or not (book_dir / source_rel).is_file():
            issues.append(
                ArtIssue(
                    code="missing_source",
                    message=f"Missing source artwork for scene {sid}",
                    scene_id=sid,
                )
            )
        if scene.get("art_status") == ArtStatus.APPROVED.value:
            approved_rel = artwork.get("approved_path")
            if not approved_rel or not (book_dir / approved_rel).is_file():
                issues.append(
                    ArtIssue(
                        code="missing_approved",
                        message=f"Scene {sid} marked approved but approved file missing",
                        scene_id=sid,
                    )
                )
    return ArtCheckResult(ok=not issues, issues=issues)


def young_child_qc(image_path: Path | str, *, scene_id: str | None = None) -> ArtCheckResult:
    """Heuristic flags for young-child coloring suitability.

    These are advisory signals, not a substitute for human approval.
    """
    image_path = Path(image_path)
    issues: list[ArtIssue] = []
    with Image.open(image_path) as img:
        gray = img.convert("L")
        width, height = gray.size
        pixels = list(gray.getdata())
        total = len(pixels)
        if total == 0:
            return ArtCheckResult(
                ok=False,
                issues=[ArtIssue("empty_image", "Image has no pixels", scene_id)],
            )

        whiteish = sum(1 for p in pixels if p >= 240)
        dark = sum(1 for p in pixels if p <= 40)
        white_ratio = whiteish / total
        dark_ratio = dark / total

        # Large open areas: expect plenty of near-white fill space.
        if white_ratio < 0.55:
            issues.append(
                ArtIssue(
                    "low_open_area",
                    f"Open/white area ratio {white_ratio:.2f} < 0.55 (may be too dense)",
                    scene_id,
                    severity="warning",
                )
            )

        # Thick outlines: expect a modest dark ink presence, not near-zero.
        if dark_ratio < 0.005:
            issues.append(
                ArtIssue(
                    "thin_or_missing_outlines",
                    f"Dark pixel ratio {dark_ratio:.4f} < 0.005 (outlines may be too thin)",
                    scene_id,
                    severity="warning",
                )
            )

        # Clutter proxy: too many mid-tone edge-ish pixels relative to size.
        mid = sum(1 for p in pixels if 40 < p < 200)
        mid_ratio = mid / total
        if mid_ratio > 0.35:
            issues.append(
                ArtIssue(
                    "possible_clutter",
                    f"Mid-tone ratio {mid_ratio:.2f} > 0.35 (may be too detailed)",
                    scene_id,
                    severity="warning",
                )
            )

        # Tiny canvas is not print-legible for coloring.
        if min(width, height) < 800:
            issues.append(
                ArtIssue(
                    "low_pixel_size",
                    f"Image {width}x{height} is smaller than 800px on shortest side",
                    scene_id,
                    severity="warning",
                )
            )

    # Warnings do not hard-fail; human approval remains the gate.
    hard = [i for i in issues if i.severity == "error"]
    return ArtCheckResult(ok=not hard, issues=issues)


def create_placeholder_line_art(
    dest: Path | str,
    *,
    title: str,
    size_px: int = 2550,
) -> Path:
    """Create original simple line-art placeholder (not character likeness)."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (size_px, size_px), "white")
    draw = ImageDraw.Draw(img)
    margin = int(size_px * 0.12)
    # Outer frame
    for offset in range(0, 18, 6):
        draw.rectangle(
            [margin - offset, margin - offset, size_px - margin + offset, size_px - margin + offset],
            outline="black",
            width=10,
        )
    # Simple subject: large circle + oval body (generic pet shape, not a likeness)
    cx, cy = size_px // 2, int(size_px * 0.42)
    r = int(size_px * 0.16)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="black", width=14)
    body_w, body_h = int(size_px * 0.34), int(size_px * 0.22)
    bx, by = cx - body_w // 2, cy + int(r * 0.7)
    draw.ellipse([bx, by, bx + body_w, by + body_h], outline="black", width=14)
    # Ears
    ear = int(r * 0.45)
    draw.ellipse([cx - r - ear // 2, cy - r, cx - r + ear, cy - r + ear * 2], outline="black", width=12)
    draw.ellipse([cx + r - ear, cy - r, cx + r + ear // 2, cy - r + ear * 2], outline="black", width=12)
    # Ground line
    gy = int(size_px * 0.78)
    draw.line([margin + 40, gy, size_px - margin - 40, gy], fill="black", width=12)
    # Title label (factory placeholder cue)
    try:
        font = ImageFont.load_default()
    except OSError:
        font = None
    label = f"PLACEHOLDER — {title}"
    draw.text((margin, size_px - margin + 20), label, fill="black", font=font)
    img.save(dest, format="PNG")
    return dest


def seed_placeholders_for_book(book_dir: Path | str) -> list[Path]:
    """Generate and approve placeholder pages for every scene (demo/factory path)."""
    book_dir = Path(book_dir)
    book, _ = load_book(book_dir)
    source_dir, _ = book_art_dirs(book_dir)
    created: list[Path] = []
    for scene in sorted(book["scenes"], key=lambda s: s["page_number"]):
        sid = scene["scene_id"]
        temp = source_dir / f"{sid}.png"
        create_placeholder_line_art(temp, title=scene["title"])
        # import_source would copy; file already in place — record paths via approve path
        scene.setdefault("artwork", {})
        scene["artwork"]["source_path"] = str(temp.relative_to(book_dir))
        scene["art_status"] = ArtStatus.SOURCE.value
        created.append(temp)
    _refresh_book_art_status(book)
    save_json(book_dir / "book.json", book)
    for scene in book["scenes"]:
        approve_artwork(book_dir, scene["scene_id"])
    return created


def write_art_report(book_dir: Path | str, dest: Path | str | None = None) -> dict[str, Any]:
    book_dir = Path(book_dir)
    missing = check_missing_assets(book_dir)
    book, _ = load_book(book_dir)
    qc_issues: list[dict[str, Any]] = []
    for scene in book["scenes"]:
        artwork = scene.get("artwork") or {}
        for key in ("approved_path", "source_path"):
            rel = artwork.get(key)
            if rel and (book_dir / rel).is_file():
                result = young_child_qc(book_dir / rel, scene_id=scene["scene_id"])
                qc_issues.extend(result.to_dict()["issues"])
                break
    report = {
        "book_id": book["book_id"],
        "missing_assets": missing.to_dict(),
        "young_child_qc": qc_issues,
    }
    if dest:
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
