"""Load and save book/character JSON configurations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from factory.schema import validate_book_with_characters


def load_json(path: Path | str) -> Any:
    path = Path(path)
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path | str, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=False)
        handle.write("\n")


def book_paths(book_dir: Path | str) -> tuple[Path, Path]:
    book_dir = Path(book_dir)
    return book_dir / "book.json", book_dir / "characters.json"


def load_book(book_dir: Path | str) -> tuple[dict[str, Any], dict[str, Any]]:
    book_path, characters_path = book_paths(book_dir)
    book = load_json(book_path)
    characters = load_json(characters_path)
    validate_book_with_characters(book, characters)
    return book, characters
