"""Publishing metadata export."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from factory.io import load_book


def build_metadata_document(book: dict[str, Any]) -> dict[str, Any]:
    publishing = book.get("publishing") or {}
    return {
        "book_id": book["book_id"],
        "title": book["title"],
        "subtitle": publishing.get("subtitle", ""),
        "description": publishing.get("description", ""),
        "keywords": publishing.get("keywords") or [],
        "categories": publishing.get("categories") or [],
        "author": publishing.get("author", ""),
        "imprint": publishing.get("imprint", ""),
        "edition": publishing.get("edition", ""),
        "language": publishing.get("language", ""),
        "marketplace": publishing.get("marketplace", ""),
        "identifiers": publishing.get("identifiers") or {},
        "audience": book.get("audience", ""),
        "theme": book.get("theme", ""),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def export_metadata(
    book_dir: Path | str,
    *,
    repo_root: Path | str | None = None,
) -> Path:
    book_dir = Path(book_dir).resolve()
    repo_root = Path(repo_root) if repo_root else book_dir.parents[1]
    book, _ = load_book(book_dir)
    doc = build_metadata_document(book)
    out_dir = repo_root / "output" / book["book_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "metadata.json"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return path
