from pathlib import Path

from factory.io import load_book


BOOK = Path(__file__).resolve().parents[1] / "books" / "cozy-dogs-cats"


def test_first_book_validates():
    book, characters = load_book(BOOK)
    assert book["book_id"] == "cozy-dogs-cats"
    assert len(book["scenes"]) == 4
    assert {c["character_id"] for c in characters["characters"]} == {
        "etsy",
        "smoky",
        "fat-girl",
        "luna",
        "coco",
    }


def test_first_book_known_scene_ids():
    book, _ = load_book(BOOK)
    assert [s["scene_id"] for s in sorted(book["scenes"], key=lambda s: s["page_number"])] == [
        "bed-cozy",
        "garden-play",
        "picnic",
        "rainy-day",
    ]
