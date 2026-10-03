from pathlib import Path

from factory.io import load_book


BOOK = Path(__file__).resolve().parents[1] / "books" / "cozy-dogs-cats"

EXPECTED_SCENES = [
    "puppy-newborn-sleep",
    "puppy-newborn-closeup",
    "puppy-box-nest",
    "puppy-box-ball",
    "puppy-bottle-time",
    "puppy-held",
    "puppy-bow-day",
    "puppy-floor-look",
    "puppy-garden-play",
    "puppy-picnic",
    "mature-bed-luna",
    "mature-car-buddy",
    "mature-rainy-nap",
    "mature-happy-smile",
    "mature-plush-bed",
    "mature-sleep-closeup",
    "mature-hoodie",
    "mature-window-watch",
    "mature-big-smile",
]


def test_first_book_validates():
    book, characters = load_book(BOOK)
    assert book["book_id"] == "cozy-dogs-cats"
    assert len(book["scenes"]) == 19
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


def test_book_has_puppy_then_mature_sections():
    book, _ = load_book(BOOK)
    scenes = sorted(book["scenes"], key=lambda s: s["page_number"])
    assert all(s.get("section") == "puppy" for s in scenes[:10])
    assert all(s.get("section") == "mature" for s in scenes[10:])


def test_approved_art_exists_for_every_scene():
    book, _ = load_book(BOOK)
    for scene in book["scenes"]:
        path = BOOK / scene["artwork"]["approved_path"]
        assert path.is_file(), path
        assert scene["art_status"] == "approved"
