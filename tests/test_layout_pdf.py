from pathlib import Path

from pypdf import PdfReader

from factory.art import approve_artwork, create_placeholder_line_art, import_source
from factory.io import load_json, save_json
from factory.layout import geometry_from_book
from factory.pdf import build_interior_pdf


def _book_with_art(tmp_path: Path) -> Path:
    src = Path(__file__).parent / "fixtures" / "minimal_book"
    book_dir = tmp_path / "book"
    book_dir.mkdir()
    (book_dir / "artwork" / "source").mkdir(parents=True)
    (book_dir / "artwork" / "approved").mkdir(parents=True)
    book = load_json(src / "book.json")
    # Add a second page to verify order.
    book["scenes"].append(
        {
            "scene_id": "scene-02",
            "title": "Second",
            "description": "Second page",
            "page_number": 2,
            "character_ids": ["char-a"],
            "approval_status": "approved",
            "art_status": "missing",
        }
    )
    save_json(book_dir / "book.json", book)
    save_json(book_dir / "characters.json", load_json(src / "characters.json"))
    for scene_id in ("scene-01", "scene-02"):
        art = tmp_path / f"{scene_id}.png"
        create_placeholder_line_art(art, title=scene_id)
        import_source(book_dir, scene_id, art)
        approve_artwork(book_dir, scene_id)
    return book_dir


def test_geometry_uses_book_config():
    book = load_json(Path(__file__).parent / "fixtures" / "minimal_book" / "book.json")
    geo = geometry_from_book(book)
    assert geo.trim_width_in == 8.5
    assert geo.media_width_in == 8.5 + 2 * 0.125
    x0, y0, x1, y1 = geo.content_box_pt
    assert x0 == (0.125 + 0.5) * 72
    assert x1 > x0 and y1 > y0


def test_build_interior_pdf(tmp_path: Path):
    book_dir = _book_with_art(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    pdf_path = build_interior_pdf(book_dir, repo_root=repo)
    assert pdf_path.is_file()
    reader = PdfReader(str(pdf_path))
    assert len(reader.pages) == 2
    manifest = load_json(repo / "output" / "minimal-demo" / "build_manifest.json")
    assert manifest["page_count"] == 2
    assert [p["scene_id"] for p in manifest["pages"]] == ["scene-01", "scene-02"]
