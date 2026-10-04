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
    by_id = {c["character_id"]: c for c in characters["characters"]}
    assert by_id["etsy"]["name"] == "Etsy Penelope Sochi"
    assert by_id["smoky"]["source_refs"]
    assert by_id["fat-girl"]["source_refs"]


def test_book_sections_puppy_then_later():
    book, _ = load_book(BOOK)
    scenes = sorted(book["scenes"], key=lambda s: s["page_number"])
    assert [s["page_number"] for s in scenes] == list(range(1, 51))
    assert all(s["section"] == "puppy" for s in scenes[:20])
    # Pages 21–50 are mature life + family/parent scenes
    assert all(s["section"] in {"mature", "family"} for s in scenes[20:])
    family_ids = {s["scene_id"] for s in scenes if s["section"] == "family"}
    assert "smoky-porch-sit" in family_ids
    assert "fat-girl-portrait" in family_ids
    assert "family-portrait" in family_ids


def test_approved_art_exists_for_every_scene():
    book, _ = load_book(BOOK)
    for scene in book["scenes"]:
        path = BOOK / scene["artwork"]["approved_path"]
        assert path.is_file(), path
        assert scene["art_status"] == "approved"


def test_baseline_printing_spec():
    book, _ = load_book(BOOK)
    layout = book["layout"]
    printing = book["printing"]
    assert layout["trim_width_in"] == 8.5
    assert layout["trim_height_in"] == 11.0
    assert layout["bleed_in"] == 0.0
    assert printing["blank_backs"] is True
    assert printing["target_illustration_count"] == 50
    assert printing["front_matter"] == ["title", "belongs_to", "copyright"]
