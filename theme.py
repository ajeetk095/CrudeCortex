"""Shared UI helpers and theme constants for the GWP1 research platform."""
import base64
import streamlit as st


def inject_css() -> None:
    """Global colourful theme (called once from app.py)."""
    from core.ui_components import inject_css as _css
    _css()

ORANGE = "#E8842C"
NAVY = "#1A2733"
BLUE = "#1F6FB2"
GREEN = "#2E7D32"
RED = "#C62828"
GRAY = "#6B7280"
BG = "#F4F1EC"

MARKDOWN_BADGE = (
    "<span style='background:{bg};color:white;padding:2px 10px;"
    "border-radius:10px;font-size:0.75em;font-weight:600'>{text}</span>"
)


def freshness_badge(kind: str) -> str:
    colors = {"LIVE": GREEN, "DELAYED": ORANGE, "MONTHLY": BLUE,
              "QUARTERLY": BLUE, "ESTIMATE": ORANGE, "FORECAST": "#7B1FA2",
              "STALE": RED, "UNAVAILABLE": GRAY}
    return MARKDOWN_BADGE.format(bg=colors.get(kind, GRAY), text=kind)


def img_tag(png_bytes: bytes, w: int = 640) -> str:
    b64 = base64.b64encode(png_bytes).decode()
    return (f"<img src='data:image/png;base64,{b64}' style='width:100%;"
            f"max-width:{w}px;border-radius:10px;'/>")
