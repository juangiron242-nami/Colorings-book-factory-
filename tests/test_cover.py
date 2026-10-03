from pathlib import Path

import pytest

from factory.art import approve_artwork, create_placeholder_line_art, import_source
from factory.cover import CoverError, build_cover, cover_dimensions
from factory.io import load_json, save_json
from factory.pdf import build_interior_pdf


def _book_ready(tmp_path: Path) -> tuple[Path, Path]:
    src = Path(__file__).parent / "fixtures" / "minimal_book"
    book_dir = tmp_path / "book"
    repo = tmp_path / "repo"
    repo.mkdir()
    book_dir.mkdir()
    (book_dir / "artwork" / "source").mkdir(parents=True)
    (book_dir / "artwork" / "approved").mkdir(parents=True)
    save_json(book_dir / "book.json", load_json(src / "book.json"))
    save_json(book_dir / "characters.json", load_json(src / "characters.json"))
    art = tmp_path / "page.png"
    create_placeholder_line_art(art, title="One")
    import_source(book_dir, "scene-01", art)
    approve_artwork(book_dir, "scene-01")
    build_interior_pdf(book_dir, repo_root=repo)
    return book_dir, repo


def test_cover_dimensions_use_page_count():
    book = load_json(Path(__file__).parent / "fixtures" / "minimal_book" / "book.json")
    dims = cover_dimensions(book, page_count=24)
    assert dims["spine_in"] == pytest.approx(24 * 0.002252)
    assert dims["width_in"] > 2 * book["layout"]["trim_width_in"]


def test_build_cover_requires_interior(tmp_path: Path):
    src = Path(__file__).parent / "fixtures" / "minimal_book"
    book_dir = tmp_path / "book"
    book_dir.mkdir()
    save_json(book_dir / "book.json", load_json(src / "book.json"))
    save_json(book_dir / "characters.json", load_json(src / "characters.json"))
    with pytest.raises(CoverError, match="Interior build manifest"):
        build_cover(book_dir, repo_root=tmp_path / "repo")


def test_build_cover_writes_pdf_and_preserves_source(tmp_path: Path):
    book_dir, repo = _book_ready(tmp_path)
    cover_pdf = build_cover(book_dir, repo_root=repo)
    assert cover_pdf.is_file()
    source = book_dir / "artwork" / "cover" / "source" / "cover_wrap.png"
    assert source.is_file()
    # Rebuild must not destroy existing source.
    mtime = source.stat().st_mtime_ns
    build_cover(book_dir, repo_root=repo)
    assert source.stat().st_mtime_ns == mtime
