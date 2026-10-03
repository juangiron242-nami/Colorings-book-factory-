from pathlib import Path

from factory.io import load_book


BOOK = Path(__file__).resolve().parents[1] / "books" / "cozy-dogs-cats"


def test_first_book_validates():
    book, characters = load_book(BOOK)
    assert book["book_id"] == "cozy-dogs-cats"
    assert len(book["scenes"]) == 50
    assert {c["character_id"] for c in characters["characters"]} == {
        "etsy",
        "smoky",
        "fat-girl",
        "luna",
        "coco",
    }


def test_book_sections_puppy_then_mature():
    book, _ = load_book(BOOK)
    scenes = sorted(book["scenes"], key=lambda s: s["page_number"])
    assert [s["page_number"] for s in scenes] == list(range(1, 51))
    assert all(s["section"] == "puppy" for s in scenes[:20])
    assert all(s["section"] == "mature" for s in scenes[20:])


def test_approved_art_exists_for_every_scene():
    book, _ = load_book(BOOK)
    for scene in book["scenes"]:
        path = BOOK / scene["artwork"]["approved_path"]
        assert path.is_file(), path
        assert scene["art_status"] == "approved"
