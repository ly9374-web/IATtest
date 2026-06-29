"""Streamlit 会话状态的单一初始化入口。"""

from __future__ import annotations

import streamlit as st


DEFAULT_STATE: dict[str, object] = {
    "page": "home",
    "concept_text": "",
    "session": None,
    "task_progress": None,
    "last_reaction_event_id": None,
    "last_reaction_event": None,
}


def initialize_state() -> None:
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value
    repair_route_state()


def repair_route_state() -> None:
    """保证当前路由所依赖的数据完整。

    浏览器刷新会创建新的 Streamlit 会话并自然回到 home；若 rerun 或
    恢复状态时出现不完整的 task/report，则退回最近的完整页面。
    """
    valid_pages = {"home", "instruction", "task", "report"}
    if st.session_state.page not in valid_pages:
        st.session_state.page = "home"

    has_concept = bool(st.session_state.concept_text.strip())
    if st.session_state.page == "instruction" and not has_concept:
        st.session_state.page = "home"
        return

    if st.session_state.page == "task" and (
        st.session_state.session is None
        or st.session_state.task_progress is None
    ):
        st.session_state.page = "instruction" if has_concept else "home"
        return

    if st.session_state.page == "report":
        session = st.session_state.session
        if session is None:
            st.session_state.page = "instruction" if has_concept else "home"
        elif session.report is None:
            st.session_state.page = "task"


def reset_for_retest() -> None:
    """清除一次测试的全部运行状态。"""
    st.session_state.page = "home"
    st.session_state.concept_text = ""
    st.session_state.session = None
    st.session_state.task_progress = None
    st.session_state.last_reaction_event_id = None
    st.session_state.last_reaction_event = None
    st.session_state.pop("concept_input", None)
