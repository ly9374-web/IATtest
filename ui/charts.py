"""SwiftUI ScatterPlotView 的 SVG 对应实现。"""

from __future__ import annotations

from collections.abc import Sequence

import streamlit as st

from iat_core.models import ConditionType, ScatterPoint


def build_scatter_svg(
    points: Sequence[ScatterPoint],
    *,
    width: float = 800,
    height: float = 240,
) -> str:
    max_x = max(max((point.x for point in points), default=1), 1)
    min_x = min(min((point.x for point in points), default=0), 0)
    denominator = max_x - min_x if max_x != min_x else 1

    circles: list[str] = []
    for point in points:
        x_ratio = (point.x - min_x) / denominator
        x = 32 + x_ratio * (width - 40)
        y_base = (
            height * 0.35
            if point.condition is ConditionType.COMPATIBLE
            else height * 0.7
        )
        y = y_base + point.jitter * 12
        color = "#22a447" if point.condition is ConditionType.COMPATIBLE else "#ff3b30"
        circles.append(
            f'<circle cx="{x:.3f}" cy="{y:.3f}" r="3" fill="{color}" />'
        )

    return (
        '<div class="iat-scatter-chart" '
        f'data-point-count="{len(points)}">'
        f'<svg viewBox="0 0 {width:g} {height:g}" '
        'preserveAspectRatio="none" role="img" aria-label="散点图">'
        f'<path d="M 32 {height - 24:g} H {width - 8:g} '
        f'M 32 8 V {height - 24:g}" '
        'fill="none" stroke="rgba(128,128,128,0.75)" stroke-width="1" />'
        + "".join(circles)
        + "</svg></div>"
    )


def render_scatter_plot(points: Sequence[ScatterPoint]) -> None:
    st.html(build_scatter_svg(points))
