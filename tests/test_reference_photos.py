from pathlib import Path

from factory.io import load_book, load_json


BOOK = Path(__file__).resolve().parents[1] / "books" / "cozy-dogs-cats"
MANIFEST = BOOK / "artwork" / "source" / "references" / "MANIFEST.json"


def test_reference_manifest_present_and_linked():
    assert MANIFEST.is_file()
    manifest = load_json(MANIFEST)
    assert manifest["book_id"] == "cozy-dogs-cats"
    assert len(manifest["photos"]) == 46
    for photo in manifest["photos"]:
        assert (BOOK / photo["path"]).is_file()

    book, characters = load_book(BOOK)
    assert book["book_id"] == "cozy-dogs-cats"
    by_id = {c["character_id"]: c for c in characters["characters"]}
    assert by_id["etsy"]["source_refs"]
    assert by_id["coco"]["source_refs"]
    assert by_id["etsy"]["approval_status"] == "in_review"
    assert by_id["luna"]["source_refs"] == []
    assert "smoky" in manifest["missing_in_this_batch"]
