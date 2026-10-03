"""Assemble a final human-review release package."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from factory import __version__
from factory.checks import write_preflight_reports
from factory.cover import build_cover
from factory.io import load_book, save_json
from factory.metadata import export_metadata
from factory.pdf import build_interior_pdf
from factory.royalty import export_royalty
from factory.schema import ArtStatus, OutputStatus


class ReleaseError(RuntimeError):
    """Release package is not ready."""


REQUIRED_PACKAGE_FILES = [
    "interior.pdf",
    "cover.pdf",
    "qc_report.json",
    "qc_report.txt",
    "metadata.json",
    "royalty_summary.json",
    "royalty_summary.txt",
    "build_info.json",
]


def _require_approvals(book: dict[str, Any]) -> None:
    for scene in book["scenes"]:
        if scene.get("art_status") != ArtStatus.APPROVED.value:
            raise ReleaseError(
                f"scene {scene['scene_id']} art is not approved "
                f"(art_status={scene.get('art_status')})"
            )
        artwork = scene.get("artwork") or {}
        if not artwork.get("approved_path"):
            raise ReleaseError(f"scene {scene['scene_id']} missing approved_path")
    if book.get("art_status") != ArtStatus.APPROVED.value:
        raise ReleaseError(f"book.art_status must be approved, got {book.get('art_status')}")


def build_release_package(
    book_dir: Path | str,
    *,
    repo_root: Path | str | None = None,
    rebuild: bool = True,
) -> Path:
    book_dir = Path(book_dir).resolve()
    repo_root = Path(repo_root) if repo_root else book_dir.parents[1]
    book, _ = load_book(book_dir)
    _require_approvals(book)

    if rebuild:
        build_interior_pdf(book_dir, repo_root=repo_root)
        build_cover(book_dir, repo_root=repo_root)
        export_metadata(book_dir, repo_root=repo_root)
        export_royalty(book_dir, repo_root=repo_root)

    json_path, text_path = write_preflight_reports(book_dir, repo_root=repo_root)
    qc = json.loads(json_path.read_text(encoding="utf-8"))
    if not qc.get("ok"):
        raise ReleaseError(
            f"QC failed; release blocked. See {json_path} / {text_path}"
        )

    out_root = repo_root / "output" / book["book_id"]
    release_dir = out_root / "release"
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir(parents=True)

    mapping = {
        "interior.pdf": out_root / f"{book['book_id']}_interior.pdf",
        "cover.pdf": out_root / f"{book['book_id']}_cover.pdf",
        "qc_report.json": out_root / "qc_report.json",
        "qc_report.txt": out_root / "qc_report.txt",
        "metadata.json": out_root / "metadata.json",
        "royalty_summary.json": out_root / "royalty_summary.json",
        "royalty_summary.txt": out_root / "royalty_summary.txt",
    }
    for name, src in mapping.items():
        if not src.is_file():
            raise ReleaseError(f"missing required asset for release: {src}")
        shutil.copy2(src, release_dir / name)

    build_info = {
        "book_id": book["book_id"],
        "title": book["title"],
        "factory_version": __version__,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "qc_ok": True,
        "art_status": book.get("art_status"),
        "page_count": len(book["scenes"]),
        "source_book_dir": str(book_dir),
        "package_files": REQUIRED_PACKAGE_FILES,
        "notes": (
            "Package ready for human publishing review. "
            "Placeholder artwork is not final character likeness."
        ),
    }
    (release_dir / "build_info.json").write_text(
        json.dumps(build_info, indent=2) + "\n", encoding="utf-8"
    )

    for name in REQUIRED_PACKAGE_FILES:
        if not (release_dir / name).is_file():
            raise ReleaseError(f"release package incomplete: {name}")

    book["output_status"] = OutputStatus.READY.value
    save_json(book_dir / "book.json", book)
    return release_dir
