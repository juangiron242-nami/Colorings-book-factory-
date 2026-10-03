from pathlib import Path

from factory.io import load_book


BOOK = Path(__file__).resolve().parents[1] / "books" / "cozy-dogs-cats"

EXPECTED_SCENES = [
    "newborn-sleep",
    "box-nest",
    "bottle-time",
    "bow-day",
    "bed-cozy",
    "garden-play",
    "car-buddy",
    "rainy-day",
    "happy-smile",
    "picnic",
]


def test_first_book_validates():
    book, characters = load_book(BOOK)
    assert book["book_id"] == "cozy-dogs-cats"
    assert len(book["scenes"]) == 10
    assert {c["character_id"] for c in characters["characters"]} == {
        "etsy",
        "smoky",
        "fat-girl",
        "luna",
        "coco",
    }


def test_first_book_known_scene_ids():
    book, _ = load_book(BOOK)
    assert [
        s["scene_id"] for s in sorted(book["scenes"], key=lambda s: s["page_number"])
    ] == EXPECTED_SCENES


def test_approved_art_exists_for_every_scene():
    book, _ = load_book(BOOK)
    for scene in book["scenes"]:
        rel = scene["artwork"]["approved_path"]
        path = BOOK / rel
        assert path.is_file(), path
        assert scene["art_status"] == "approved"
