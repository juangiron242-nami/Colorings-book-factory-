"""Command-line entry point for the Coloring Book Factory."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def cmd_validate(args: argparse.Namespace) -> int:
    from factory.io import load_book

    load_book(args.book_dir)
    print(f"OK: {args.book_dir}")
    return 0


def cmd_build_interior(args: argparse.Namespace) -> int:
    from factory.pdf import build_interior_pdf

    pdf = build_interior_pdf(args.book_dir, repo_root=_repo_root())
    print(pdf)
    return 0


def cmd_seed_placeholders(args: argparse.Namespace) -> int:
    from factory.art import seed_placeholders_for_book

    paths = seed_placeholders_for_book(args.book_dir)
    print(f"seeded {len(paths)} placeholder pages")
    return 0


def cmd_qc(args: argparse.Namespace) -> int:
    from factory.checks import write_preflight_reports

    json_path, text_path = write_preflight_reports(args.book_dir, repo_root=_repo_root())
    print(json_path)
    print(text_path)
    report = json.loads(json_path.read_text(encoding="utf-8"))
    return 0 if report["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cbf", description="Coloring Book Factory")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="Validate book + characters JSON")
    p.add_argument("book_dir", type=Path)
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("seed-placeholders", help="Create placeholder line art for all scenes")
    p.add_argument("book_dir", type=Path)
    p.set_defaults(func=cmd_seed_placeholders)

    p = sub.add_parser("build-interior", help="Build interior PDF into output/<book_id>/")
    p.add_argument("book_dir", type=Path)
    p.set_defaults(func=cmd_build_interior)

    p = sub.add_parser("qc", help="Run automated preflight checks")
    p.add_argument("book_dir", type=Path)
    p.set_defaults(func=cmd_qc)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
