"""报告 CSV/JSON 剪贴板组件。"""

from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components

_component = components.declare_component(
    "iat_clipboard_export",
    path=Path(__file__).resolve().parent / "frontend",
)


def clipboard_export(*, csv_text: str, json_text: str) -> None:
    _component(
        csv_text=csv_text,
        json_text=json_text,
        default=None,
        key="report_clipboard_export",
        tab_index=0,
    )


__all__ = ["clipboard_export"]

