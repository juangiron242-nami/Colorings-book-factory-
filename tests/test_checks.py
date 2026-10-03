from pathlib import Path

from factory.art import approve_artwork, create_placeholder_line_art, import_source
from factory.checks import run_preflight, write_preflight_reports
from factory.io import load_json, save_json
from factory.pdf import build_interior_pdf


def _prepared_book(tmp_path: Path) -> tuple[Path, Path]:
    src = Path(__file__).parent / "fixtures" / "minimal_book"
    book_dir = tmp_path / "book"
    repo = tmp_path / "repo"
    repo.mkdir()
    book_dir.mkdir()
    (book_dir / "artwork" / "source").mkdir(parents=True)
    (book_dir / "artwork" / "approved").mkdir(parents=True)
    book = load_json(src / "book.json")
    book["publishing"]["author"] = "Test Author"
    book["publishing"]["description"] = "A test description."
    save_json(book_dir / "book.json", book)
    save_json(book_dir / "characters.json", load_json(src / "characters.json"))
    art = tmp_path / "page.png"
    create_placeholder_line_art(art, title="One")
    import_source(book_dir, "scene-01", art)
    approve_artwork(book_dir, "scene-01")
    build_interior_pdf(book_dir, repo_root=repo)
    return book_dir, repo


def test_preflight_passes_after_build(tmp_path: Path):
    book_dir, repo = _prepared_book(tmp_path)
    report = run_preflight(book_dir, repo_root=repo)
    assert report["ok"] is True
    json_path, text_path = write_preflight_reports(book_dir, repo_root=repo)
    assert json_path.is_file()
    assert "PASS" in text_path.read_text(encoding="utf-8")


def test_preflight_fails_without_pdf(tmp_path: Path):
    book_dir, repo = _prepared_book(tmp_path)
    pdf = repo / "output" / "minimal-demo" / "minimal-demo_interior.pdf"
    pdf.unlink()
    report = run_preflight(book_dir, repo_root=repo)
    assert report["ok"] is False
    assert any(i["code"] == "missing_build_artifact" for i in report["issues"])
