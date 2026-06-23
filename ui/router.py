"""单入口页面状态路由。"""

from __future__ import annotations

import streamlit as st

from iat_core.preset_store import CustomPresetStore
from .home import render_home
from .instruction import render_instruction
from .report import render_report
from .state import repair_route_state
from .task import render_task


def render_current_page(store: CustomPresetStore) -> None:
    repair_route_state()
    page = st.session_state.page

    if page == "home":
        render_home(store)
    elif page == "instruction":
        render_instruction()
    elif page == "task":
        render_task()
    else:
        render_report()
