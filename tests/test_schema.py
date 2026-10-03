from pathlib import Path

import pytest

from factory.io import load_book, load_json
from factory.schema import SchemaError, validate_book, validate_book_with_characters


FIXTURE = Path(__file__).parent / "fixtures" / "minimal_book"


def test_minimal_fixture_validates():
    book, characters = load_book(FIXTURE)
    assert book["book_id"] == "minimal-demo"
    assert characters["characters"][0]["character_id"] == "char-a"


def test_missing_required_field_fails():
    book = load_json(FIXTURE / "book.json")
    del book["theme"]
    with pytest.raises(SchemaError, match="theme"):
        validate_book(book)


def test_unknown_character_reference_fails():
    book = load_json(FIXTURE / "book.json")
    characters = load_json(FIXTURE / "characters.json")
    book["scenes"][0]["character_ids"] = ["nope"]
    with pytest.raises(SchemaError, match="unknown character_id"):
        validate_book_with_characters(book, characters)


def test_duplicate_page_number_fails():
    book = load_json(FIXTURE / "book.json")
    book["scenes"].append(
        {
            "scene_id": "scene-02",
            "title": "Another",
            "description": "Duplicate page",
            "page_number": 1,
            "character_ids": ["char-a"],
            "approval_status": "draft",
            "art_status": "missing",
        }
    )
    with pytest.raises(SchemaError, match="duplicate page_number"):
        validate_book(book)
