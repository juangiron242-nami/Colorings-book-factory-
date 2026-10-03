from pathlib import Path

from factory.io import load_json, save_json
from factory.metadata import build_metadata_document, export_metadata
from factory.royalty import calculate_royalty, export_royalty, load_economics_config


def test_metadata_export(tmp_path: Path):
    src = Path(__file__).parent / "fixtures" / "minimal_book"
    book_dir = tmp_path / "book"
    book_dir.mkdir()
    book = load_json(src / "book.json")
    book["publishing"]["author"] = "Ada"
    save_json(book_dir / "book.json", book)
    save_json(book_dir / "characters.json", load_json(src / "characters.json"))
    repo = tmp_path / "repo"
    path = export_metadata(book_dir, repo_root=repo)
    doc = load_json(path)
    assert doc["title"] == "Minimal Demo Book"
    assert doc["author"] == "Ada"
    assert build_metadata_document(book)["book_id"] == "minimal-demo"


def test_royalty_uses_visible_assumptions(tmp_path: Path):
    src = Path(__file__).parent / "fixtures" / "minimal_book"
    book_dir = tmp_path / "book"
    book_dir.mkdir()
    save_json(book_dir / "book.json", load_json(src / "book.json"))
    save_json(book_dir / "characters.json", load_json(src / "characters.json"))
    save_json(
        book_dir / "economics.json",
        {
            "list_price_usd": 10.0,
            "printing_cost_usd": 2.0,
            "royalty_rate": 0.6,
            "marketplace": "Amazon KDP",
            "units_for_projection": 10,
        },
    )
    book = load_json(book_dir / "book.json")
    assumptions = load_economics_config(book_dir, book)
    result = calculate_royalty(assumptions)
    assert result["per_unit"]["estimated_profit_usd"] == 4.0
    assert "assumptions" in result
    path = export_royalty(book_dir, repo_root=tmp_path / "repo")
    assert path.is_file()
