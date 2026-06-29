"""单入口页面状态路由。"""

from __future__ import annotations

import streamlit as st

from .home import render_home
from .countdown import render_countdown
from .instruction import render_instruction
from .report import render_report
from .state import repair_route_state
from .task import render_task


def render_current_page() -> None:
    repair_route_state()
    page = st.session_state.page

    if page == "home":
        render_home()
    elif page == "countdown":
        render_countdown()
    elif page == "instruction":
        render_instruction()
    elif page == "task":
        render_task()
    else:
        render_report()
