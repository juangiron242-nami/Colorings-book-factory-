"""Royalty / profit calculator with visible assumptions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from factory.io import load_book

# Default marketplace assumptions — documented and overridable via
# books/<id>/economics.json (preferred) or book.publishing.economics.
DEFAULT_ASSUMPTIONS = {
    "list_price_usd": 7.99,
    "printing_cost_usd": 2.15,
    "marketplace": "Amazon KDP",
    "royalty_rate": 0.60,
    "royalty_rate_note": (
        "Assumes KDP paperback 60% royalty channel when list price and marketplace "
        "eligibility rules are met. Operators must confirm current KDP terms."
    ),
    "currency": "USD",
    "units_for_projection": 100,
}


def load_economics_config(book_dir: Path, book: dict[str, Any]) -> dict[str, Any]:
    config = dict(DEFAULT_ASSUMPTIONS)
    economics_path = book_dir / "economics.json"
    if economics_path.is_file():
        config.update(json.loads(economics_path.read_text(encoding="utf-8")))
    embedded = ((book.get("publishing") or {}).get("economics")) or {}
    if isinstance(embedded, dict):
        config.update(embedded)
    return config


def calculate_royalty(assumptions: dict[str, Any]) -> dict[str, Any]:
    list_price = float(assumptions["list_price_usd"])
    printing = float(assumptions["printing_cost_usd"])
    rate = float(assumptions["royalty_rate"])
    units = int(assumptions.get("units_for_projection", 100))

    royalty_base = list_price * rate
    profit_per_unit = royalty_base - printing
    return {
        "assumptions": assumptions,
        "per_unit": {
            "list_price_usd": list_price,
            "royalty_before_print_usd": round(royalty_base, 4),
            "printing_cost_usd": printing,
            "estimated_profit_usd": round(profit_per_unit, 4),
        },
        "projection": {
            "units": units,
            "estimated_profit_usd": round(profit_per_unit * units, 2),
        },
        "formula": (
            "estimated_profit = (list_price_usd * royalty_rate) - printing_cost_usd"
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": (
            "Estimates only. Confirm current marketplace royalty rules, tax, "
            "and printing quotes before publishing decisions."
        ),
    }


def export_royalty(
    book_dir: Path | str,
    *,
    repo_root: Path | str | None = None,
) -> Path:
    book_dir = Path(book_dir).resolve()
    repo_root = Path(repo_root) if repo_root else book_dir.parents[1]
    book, _ = load_book(book_dir)
    assumptions = load_economics_config(book_dir, book)
    result = calculate_royalty(assumptions)
    result["book_id"] = book["book_id"]
    out_dir = repo_root / "output" / book["book_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "royalty_summary.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    text_path = out_dir / "royalty_summary.txt"
    pu = result["per_unit"]
    lines = [
        f"Royalty summary — {book['book_id']}",
        f"Marketplace: {assumptions['marketplace']}",
        f"List price: ${pu['list_price_usd']:.2f}",
        f"Royalty rate: {assumptions['royalty_rate']:.0%} ({assumptions.get('royalty_rate_note', '')})",
        f"Printing cost: ${pu['printing_cost_usd']:.2f}",
        f"Estimated profit / unit: ${pu['estimated_profit_usd']:.2f}",
        f"Projection ({result['projection']['units']} units): "
        f"${result['projection']['estimated_profit_usd']:.2f}",
        f"Formula: {result['formula']}",
        result["disclaimer"],
    ]
    text_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
