from pathlib import Path

import pytest

from factory.art import approve_artwork, create_placeholder_line_art, import_source
from factory.io import load_book, load_json, save_json
from factory.release import ReleaseError, build_release_package


def _ready_book(tmp_path: Path) -> tuple[Path, Path]:
    src = Path(__file__).parent / "fixtures" / "minimal_book"
    book_dir = tmp_path / "book"
    repo = tmp_path / "repo"
    repo.mkdir()
    book_dir.mkdir()
    (book_dir / "artwork" / "source").mkdir(parents=True)
    (book_dir / "artwork" / "approved").mkdir(parents=True)
    book = load_json(src / "book.json")
    book["publishing"]["author"] = "Test Author"
    book["publishing"]["description"] = "A complete description."
    save_json(book_dir / "book.json", book)
    save_json(book_dir / "characters.json", load_json(src / "characters.json"))
    art = tmp_path / "page.png"
    create_placeholder_line_art(art, title="One")
    import_source(book_dir, "scene-01", art)
    approve_artwork(book_dir, "scene-01")
    return book_dir, repo


def test_release_package_contents(tmp_path: Path):
    book_dir, repo = _ready_book(tmp_path)
    release_dir = build_release_package(book_dir, repo_root=repo)
    for name in (
        "interior.pdf",
        "cover.pdf",
        "qc_report.json",
        "qc_report.txt",
        "metadata.json",
        "royalty_summary.json",
        "royalty_summary.txt",
        "build_info.json",
    ):
        assert (release_dir / name).is_file()
    book, _ = load_book(book_dir)
    assert book["output_status"] == "ready"


def test_release_blocked_without_approval(tmp_path: Path):
    book_dir, repo = _ready_book(tmp_path)
    book = load_json(book_dir / "book.json")
    book["scenes"][0]["art_status"] = "source"
    book["art_status"] = "in_review"
    save_json(book_dir / "book.json", book)
    with pytest.raises(ReleaseError, match="not approved"):
        build_release_package(book_dir, repo_root=repo, rebuild=False)
