from pathlib import Path

from factory.io import load_book, load_json


BOOK = Path(__file__).resolve().parents[1] / "books" / "cozy-dogs-cats"
MANIFEST = BOOK / "artwork" / "source" / "references" / "MANIFEST.json"


def test_reference_manifest_present_and_linked():
    assert MANIFEST.is_file()
    manifest = load_json(MANIFEST)
    assert manifest["book_id"] == "cozy-dogs-cats"
    # 42 Etsy + 4 Coco + 13 Smoky + 5 Fat Girl + 5 Luna = 69
    assert len(manifest["photos"]) == 69
    for photo in manifest["photos"]:
        assert (BOOK / photo["path"]).is_file()

    counts = {}
    for photo in manifest["photos"]:
        counts[photo["character_id"]] = counts.get(photo["character_id"], 0) + 1
    assert counts["etsy"] == 42
    assert counts["smoky"] == 13
    assert counts["fat-girl"] == 5
    assert counts["coco"] == 4
    assert counts["luna"] == 5

    book, characters = load_book(BOOK)
    assert book["book_id"] == "cozy-dogs-cats"
    by_id = {c["character_id"]: c for c in characters["characters"]}
    assert by_id["etsy"]["source_refs"]
    assert by_id["coco"]["source_refs"]
    assert by_id["smoky"]["source_refs"]
    assert by_id["fat-girl"]["source_refs"]
    assert by_id["luna"]["source_refs"]
    assert by_id["etsy"]["name"] == "Etsy Penelope Sochi"
    assert by_id["etsy"]["approval_status"] == "in_review"
    assert by_id["luna"]["approval_status"] == "in_review"
    assert manifest["missing_in_this_batch"] == []
