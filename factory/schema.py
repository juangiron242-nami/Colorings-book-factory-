"""Book, character, and scene schemas for the Coloring Book Factory.

Schemas are generic. Book-specific content lives in JSON under books/.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Status enums (string values for JSON friendliness)
# ---------------------------------------------------------------------------


class ApprovalStatus(str, Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class ArtStatus(str, Enum):
    MISSING = "missing"
    SOURCE = "source"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class OutputStatus(str, Enum):
    NOT_STARTED = "not_started"
    PARTIAL = "partial"
    READY = "ready"
    RELEASED = "released"


# ---------------------------------------------------------------------------
# Required / optional field contracts
# ---------------------------------------------------------------------------

BOOK_REQUIRED = {
    "book_id",
    "title",
    "audience",
    "theme",
    "layout",
    "character_ids",
    "scenes",
    "art_status",
    "publishing",
    "output_status",
}

LAYOUT_REQUIRED = {
    "trim_width_in",
    "trim_height_in",
    "margin_in",
    "bleed_in",
    "dpi",
}

SCENE_REQUIRED = {
    "scene_id",
    "title",
    "description",
    "page_number",
    "character_ids",
    "approval_status",
    "art_status",
}

CHARACTER_REQUIRED = {
    "character_id",
    "name",
    "species",
    "role",
    "approval_status",
}

PUBLISHING_OPTIONAL_KEYS = {
    "subtitle",
    "description",
    "keywords",
    "categories",
    "author",
    "imprint",
    "edition",
    "identifiers",
    "language",
    "marketplace",
}


class SchemaError(ValueError):
    """Raised when structured book/character/scene data is invalid."""


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SchemaError(f"{label} must be an object")
    return value


def _require_str(obj: dict[str, Any], key: str, label: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SchemaError(f"{label}.{key} must be a non-empty string")
    return value


def _require_number(obj: dict[str, Any], key: str, label: str, *, min_value: float = 0.0) -> float:
    value = obj.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise SchemaError(f"{label}.{key} must be a number")
    number = float(value)
    if number < min_value:
        raise SchemaError(f"{label}.{key} must be >= {min_value}")
    return number


def _require_enum(obj: dict[str, Any], key: str, label: str, enum_cls: type[Enum]) -> str:
    value = _require_str(obj, key, label)
    allowed = {item.value for item in enum_cls}
    if value not in allowed:
        raise SchemaError(f"{label}.{key} must be one of {sorted(allowed)}")
    return value


def _require_str_list(obj: dict[str, Any], key: str, label: str) -> list[str]:
    value = obj.get(key)
    if not isinstance(value, list) or not value:
        raise SchemaError(f"{label}.{key} must be a non-empty list of strings")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise SchemaError(f"{label}.{key} entries must be non-empty strings")
    return value


def validate_layout(layout: Any, *, label: str = "layout") -> dict[str, Any]:
    layout = _require_mapping(layout, label)
    missing = LAYOUT_REQUIRED - set(layout)
    if missing:
        raise SchemaError(f"{label} missing required fields: {sorted(missing)}")
    _require_number(layout, "trim_width_in", label, min_value=0.1)
    _require_number(layout, "trim_height_in", label, min_value=0.1)
    _require_number(layout, "margin_in", label, min_value=0.0)
    _require_number(layout, "bleed_in", label, min_value=0.0)
    dpi = _require_number(layout, "dpi", label, min_value=72)
    if dpi != int(dpi):
        raise SchemaError(f"{label}.dpi must be an integer")
    return layout


def validate_scene(scene: Any, *, label: str = "scene") -> dict[str, Any]:
    scene = _require_mapping(scene, label)
    missing = SCENE_REQUIRED - set(scene)
    if missing:
        raise SchemaError(f"{label} missing required fields: {sorted(missing)}")
    _require_str(scene, "scene_id", label)
    _require_str(scene, "title", label)
    _require_str(scene, "description", label)
    page = scene.get("page_number")
    if not isinstance(page, int) or isinstance(page, bool) or page < 1:
        raise SchemaError(f"{label}.page_number must be an integer >= 1")
    _require_str_list(scene, "character_ids", label)
    _require_enum(scene, "approval_status", label, ApprovalStatus)
    _require_enum(scene, "art_status", label, ArtStatus)
    if "artwork" in scene and scene["artwork"] is not None:
        artwork = _require_mapping(scene["artwork"], f"{label}.artwork")
        for key in ("source_path", "approved_path"):
            if key in artwork and artwork[key] is not None:
                if not isinstance(artwork[key], str):
                    raise SchemaError(f"{label}.artwork.{key} must be a string path")
    return scene


def validate_character(character: Any, *, label: str = "character") -> dict[str, Any]:
    character = _require_mapping(character, label)
    missing = CHARACTER_REQUIRED - set(character)
    if missing:
        raise SchemaError(f"{label} missing required fields: {sorted(missing)}")
    _require_str(character, "character_id", label)
    _require_str(character, "name", label)
    _require_str(character, "species", label)
    _require_str(character, "role", label)
    _require_enum(character, "approval_status", label, ApprovalStatus)
    # Visual notes are optional and must not invent locked likeness details.
    if "visual_notes" in character and character["visual_notes"] is not None:
        if not isinstance(character["visual_notes"], str):
            raise SchemaError(f"{label}.visual_notes must be a string")
    if "source_refs" in character and character["source_refs"] is not None:
        refs = character["source_refs"]
        if not isinstance(refs, list):
            raise SchemaError(f"{label}.source_refs must be a list")
        for ref in refs:
            if not isinstance(ref, str):
                raise SchemaError(f"{label}.source_refs entries must be strings")
    return character


def validate_publishing(publishing: Any, *, label: str = "publishing") -> dict[str, Any]:
    publishing = _require_mapping(publishing, label)
    # Publishing may start sparse; require only that known keys have sane types.
    if "title" in publishing:
        _require_str(publishing, "title", label)
    if "keywords" in publishing and publishing["keywords"] is not None:
        if not isinstance(publishing["keywords"], list):
            raise SchemaError(f"{label}.keywords must be a list")
    if "categories" in publishing and publishing["categories"] is not None:
        if not isinstance(publishing["categories"], list):
            raise SchemaError(f"{label}.categories must be a list")
    if "identifiers" in publishing and publishing["identifiers"] is not None:
        _require_mapping(publishing["identifiers"], f"{label}.identifiers")
    return publishing


def validate_book(book: Any) -> dict[str, Any]:
    book = _require_mapping(book, "book")
    missing = BOOK_REQUIRED - set(book)
    if missing:
        raise SchemaError(f"book missing required fields: {sorted(missing)}")

    _require_str(book, "book_id", "book")
    _require_str(book, "title", "book")
    _require_str(book, "audience", "book")
    _require_str(book, "theme", "book")
    validate_layout(book["layout"], label="book.layout")
    character_ids = _require_str_list(book, "character_ids", "book")

    scenes = book.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise SchemaError("book.scenes must be a non-empty list")

    page_numbers: set[int] = set()
    scene_ids: set[str] = set()
    for index, scene in enumerate(scenes):
        validated = validate_scene(scene, label=f"book.scenes[{index}]")
        scene_id = validated["scene_id"]
        if scene_id in scene_ids:
            raise SchemaError(f"duplicate scene_id: {scene_id}")
        scene_ids.add(scene_id)
        page = validated["page_number"]
        if page in page_numbers:
            raise SchemaError(f"duplicate page_number: {page}")
        page_numbers.add(page)
        for cid in validated["character_ids"]:
            if cid not in character_ids:
                raise SchemaError(
                    f"book.scenes[{index}] references unknown character_id: {cid}"
                )

    _require_enum(book, "art_status", "book", ArtStatus)
    validate_publishing(book["publishing"], label="book.publishing")
    _require_enum(book, "output_status", "book", OutputStatus)
    return book


def validate_characters_file(payload: Any) -> list[dict[str, Any]]:
    payload = _require_mapping(payload, "characters")
    characters = payload.get("characters")
    if not isinstance(characters, list) or not characters:
        raise SchemaError("characters.characters must be a non-empty list")
    seen: set[str] = set()
    validated: list[dict[str, Any]] = []
    for index, character in enumerate(characters):
        item = validate_character(character, label=f"characters[{index}]")
        cid = item["character_id"]
        if cid in seen:
            raise SchemaError(f"duplicate character_id: {cid}")
        seen.add(cid)
        validated.append(item)
    return validated


def validate_book_with_characters(book: Any, characters_payload: Any) -> dict[str, Any]:
    book = validate_book(book)
    characters = validate_characters_file(characters_payload)
    available = {c["character_id"] for c in characters}
    missing = [cid for cid in book["character_ids"] if cid not in available]
    if missing:
        raise SchemaError(f"book.character_ids missing from characters file: {missing}")
    return book
