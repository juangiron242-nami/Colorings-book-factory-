"""Automated preflight / QC for publishing inputs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

from factory.art import check_missing_assets, young_child_qc
from factory.io import load_book
from factory.layout import geometry_from_book, ordered_scenes
from factory.schema import ArtStatus


@dataclass
class CheckIssue:
    code: str
    message: str
    severity: str = "error"  # error | warning
    scene_id: str | None = None


@dataclass
class PreflightReport:
    book_id: str
    ok: bool
    checked_at: str
    issues: list[CheckIssue] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "book_id": self.book_id,
            "ok": self.ok,
            "checked_at": self.checked_at,
            "issues": [asdict(i) for i in self.issues],
            "summary": self.summary,
        }


def _add(
    issues: list[CheckIssue],
    code: str,
    message: str,
    *,
    severity: str = "error",
    scene_id: str | None = None,
) -> None:
    issues.append(CheckIssue(code=code, message=message, severity=severity, scene_id=scene_id))


def run_preflight(
    book_dir: Path | str,
    *,
    repo_root: Path | str | None = None,
) -> dict[str, Any]:
    book_dir = Path(book_dir).resolve()
    repo_root = Path(repo_root) if repo_root else book_dir.parents[1]
    book, characters = load_book(book_dir)
    issues: list[CheckIssue] = []
    geo = geometry_from_book(book)
    scenes = ordered_scenes(book)

    # Required configuration
    for key in ("title", "audience", "theme", "layout", "publishing"):
        if key not in book or book[key] in (None, "", []):
            _add(issues, "missing_configuration", f"Missing or empty book.{key}")

    publishing = book.get("publishing") or {}
    for key in ("description", "author"):
        if not str(publishing.get(key) or "").strip():
            _add(
                issues,
                "missing_metadata",
                f"publishing.{key} is empty",
                severity="warning",
            )

    # Characters present
    if not characters.get("characters"):
        _add(issues, "missing_configuration", "No characters defined")

    # Artwork missing / unapproved
    missing = check_missing_assets(book_dir)
    for item in missing.issues:
        _add(issues, item.code, item.message, severity=item.severity, scene_id=item.scene_id)

    for scene in scenes:
        sid = scene["scene_id"]
        if scene.get("art_status") != ArtStatus.APPROVED.value:
            _add(
                issues,
                "unapproved_artwork",
                f"Scene {sid} art_status={scene.get('art_status')}",
                scene_id=sid,
            )
        artwork = scene.get("artwork") or {}
        approved_rel = artwork.get("approved_path")
        if approved_rel and (book_dir / approved_rel).is_file():
            path = book_dir / approved_rel
            with Image.open(path) as img:
                width, height = img.size
            min_px_w = int(geo.trim_width_in * geo.dpi)
            min_px_h = int(geo.trim_height_in * geo.dpi)
            # Effective resolution vs trim at configured DPI.
            if width < min_px_w * 0.9 or height < min_px_h * 0.9:
                _add(
                    issues,
                    "low_resolution",
                    f"Scene {sid} image {width}x{height} below ~{min_px_w}x{min_px_h} @ {geo.dpi}dpi",
                    scene_id=sid,
                    severity="warning",
                )
            yc = young_child_qc(path, scene_id=sid)
            for yc_issue in yc.issues:
                _add(
                    issues,
                    yc_issue.code,
                    yc_issue.message,
                    severity=yc_issue.severity,
                    scene_id=sid,
                )

    # Page order / count
    pages = [s["page_number"] for s in scenes]
    if pages != list(range(1, len(pages) + 1)):
        _add(
            issues,
            "bad_page_order",
            f"page_number sequence is {pages}; expected contiguous 1..N",
        )

    # Build artifacts
    out_dir = repo_root / "output" / book["book_id"]
    pdf_path = out_dir / f"{book['book_id']}_interior.pdf"
    manifest_path = out_dir / "build_manifest.json"
    if not pdf_path.is_file():
        _add(issues, "missing_build_artifact", f"Interior PDF missing: {pdf_path}")
    if not manifest_path.is_file():
        _add(issues, "missing_build_artifact", f"Build manifest missing: {manifest_path}")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("page_count") != len(scenes):
            _add(
                issues,
                "stale_build_artifact",
                f"Manifest page_count={manifest.get('page_count')} != scenes={len(scenes)}",
            )
        manifest_ids = [p.get("scene_id") for p in manifest.get("pages", [])]
        expected_ids = [s["scene_id"] for s in scenes]
        if manifest_ids != expected_ids:
            _add(
                issues,
                "stale_build_artifact",
                "Manifest page order/scene ids do not match book.json",
            )
        m_layout = manifest.get("layout") or {}
        for key in ("trim_width_in", "trim_height_in", "margin_in", "bleed_in", "dpi"):
            if m_layout.get(key) != book["layout"].get(key):
                _add(
                    issues,
                    "stale_build_artifact",
                    f"Manifest layout.{key} mismatches book.layout",
                )
                break

    errors = [i for i in issues if i.severity == "error"]
    report = PreflightReport(
        book_id=book["book_id"],
        ok=not errors,
        checked_at=datetime.now(timezone.utc).isoformat(),
        issues=issues,
        summary={
            "scene_count": len(scenes),
            "error_count": len(errors),
            "warning_count": len(issues) - len(errors),
            "interior_pdf": str(pdf_path) if pdf_path.is_file() else None,
        },
    )
    return report.to_dict()


def write_preflight_reports(
    book_dir: Path | str,
    *,
    repo_root: Path | str | None = None,
) -> tuple[Path, Path]:
    """Write machine JSON + human-readable text QC reports."""
    book_dir = Path(book_dir)
    repo_root = Path(repo_root) if repo_root else book_dir.parents[1]
    report = run_preflight(book_dir, repo_root=repo_root)
    out_dir = repo_root / "output" / report["book_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "qc_report.json"
    text_path = out_dir / "qc_report.txt"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        f"QC Report — {report['book_id']}",
        f"Checked at: {report['checked_at']}",
        f"Result: {'PASS' if report['ok'] else 'FAIL'}",
        f"Errors: {report['summary']['error_count']}  Warnings: {report['summary']['warning_count']}",
        "",
    ]
    if not report["issues"]:
        lines.append("No issues found.")
    for issue in report["issues"]:
        loc = f" [{issue['scene_id']}]" if issue.get("scene_id") else ""
        lines.append(f"- ({issue['severity']}) {issue['code']}{loc}: {issue['message']}")
    text_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, text_path
