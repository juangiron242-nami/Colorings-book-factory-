"""Configuration-driven page geometry for KDP-oriented interiors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


INCH_TO_PT = 72.0


@dataclass(frozen=True)
class PageGeometry:
    trim_width_in: float
    trim_height_in: float
    margin_in: float
    bleed_in: float
    dpi: int

    @property
    def media_width_in(self) -> float:
        return self.trim_width_in + 2 * self.bleed_in

    @property
    def media_height_in(self) -> float:
        return self.trim_height_in + 2 * self.bleed_in

    @property
    def media_width_pt(self) -> float:
        return self.media_width_in * INCH_TO_PT

    @property
    def media_height_pt(self) -> float:
        return self.media_height_in * INCH_TO_PT

    @property
    def trim_width_pt(self) -> float:
        return self.trim_width_in * INCH_TO_PT

    @property
    def trim_height_pt(self) -> float:
        return self.trim_height_in * INCH_TO_PT

    @property
    def bleed_pt(self) -> float:
        return self.bleed_in * INCH_TO_PT

    @property
    def margin_pt(self) -> float:
        return self.margin_in * INCH_TO_PT

    @property
    def content_box_pt(self) -> tuple[float, float, float, float]:
        """Safe content box in media coordinates (x0, y0, x1, y1)."""
        x0 = self.bleed_pt + self.margin_pt
        y0 = self.bleed_pt + self.margin_pt
        x1 = self.media_width_pt - self.bleed_pt - self.margin_pt
        y1 = self.media_height_pt - self.bleed_pt - self.margin_pt
        return x0, y0, x1, y1

    @property
    def content_width_pt(self) -> float:
        x0, _, x1, _ = self.content_box_pt
        return x1 - x0

    @property
    def content_height_pt(self) -> float:
        _, y0, _, y1 = self.content_box_pt
        return y1 - y0

    def required_pixel_size(self) -> tuple[int, int]:
        return (
            int(round(self.media_width_in * self.dpi)),
            int(round(self.media_height_in * self.dpi)),
        )


def geometry_from_book(book: dict[str, Any]) -> PageGeometry:
    layout = book["layout"]
    return PageGeometry(
        trim_width_in=float(layout["trim_width_in"]),
        trim_height_in=float(layout["trim_height_in"]),
        margin_in=float(layout["margin_in"]),
        bleed_in=float(layout["bleed_in"]),
        dpi=int(layout["dpi"]),
    )


def ordered_scenes(book: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(book["scenes"], key=lambda scene: scene["page_number"])
