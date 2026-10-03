from pathlib import Path

from factory.art import (
    approve_artwork,
    check_missing_assets,
    create_placeholder_line_art,
    import_source,
    replace_source,
    young_child_qc,
)
from factory.io import load_book, load_json, save_json


def _copy_minimal(tmp_path: Path) -> Path:
    src = Path(__file__).parent / "fixtures" / "minimal_book"
    book_dir = tmp_path / "book"
    book_dir.mkdir()
    (book_dir / "artwork" / "source").mkdir(parents=True)
    (book_dir / "artwork" / "approved").mkdir(parents=True)
    save_json(book_dir / "book.json", load_json(src / "book.json"))
    save_json(book_dir / "characters.json", load_json(src / "characters.json"))
    return book_dir


def test_import_approve_and_replace(tmp_path: Path):
    book_dir = _copy_minimal(tmp_path)
    original = tmp_path / "page.png"
    create_placeholder_line_art(original, title="One")

    imported = import_source(book_dir, "scene-01", original)
    assert imported.is_file()
    assert (book_dir / "artwork" / "source" / "scene-01.png").is_file()

    approved = approve_artwork(book_dir, "scene-01")
    assert approved.is_file()
    book, _ = load_book(book_dir)
    assert book["scenes"][0]["art_status"] == "approved"
    assert book["art_status"] == "approved"

    # Original outside the book tree is untouched.
    assert original.is_file()

    replacement = tmp_path / "page2.png"
    create_placeholder_line_art(replacement, title="Two")
    replace_source(book_dir, "scene-01", replacement)
    book, _ = load_book(book_dir)
    assert book["scenes"][0]["art_status"] == "source"
    assert book["scenes"][0]["artwork"]["approved_path"] is None
    assert list((book_dir / "artwork" / "source").glob("scene-01.png.bak"))
    assert not list((book_dir / "artwork" / "approved").glob("scene-01.*"))


def test_missing_assets_detected(tmp_path: Path):
    book_dir = _copy_minimal(tmp_path)
    result = check_missing_assets(book_dir)
    assert result.ok is False
    assert result.issues[0].code == "missing_source"


def test_young_child_qc_on_placeholder(tmp_path: Path):
    path = tmp_path / "art.png"
    create_placeholder_line_art(path, title="QC")
    result = young_child_qc(path, scene_id="scene-01")
    assert result.ok is True
