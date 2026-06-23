"""Streamlit 会话状态的单一初始化入口。"""

from __future__ import annotations

import streamlit as st

from iat_core.models import CustomPreset, CustomWordConfig
from iat_core.preset_store import CustomPresetStore


DEFAULT_STATE: dict[str, object] = {
    "page": "home",
    "concept_text": "",
    "custom_dialog_open": False,
    "custom_positive_text": "",
    "custom_negative_text": "",
    "custom_yy_text": "",
    "custom_zz_text": "",
    "preset_history_open": False,
    "selected_preset_id": None,
    "pending_custom_config": None,
    "session": None,
    "task_progress": None,
    "last_reaction_event_id": None,
    "last_reaction_event": None,
}


def initialize_state(store: CustomPresetStore) -> None:
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "presets" not in st.session_state:
        st.session_state.presets = store.load()
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
        st.session_state.pending_custom_config = None
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


def parse_words(text: str) -> tuple[str, ...]:
    normalized = text
    for separator in (",", "，", ";", "\n", " ", "/", "／"):
        normalized = normalized.replace(separator, "\0")
    return tuple(word.strip() for word in normalized.split("\0") if word.strip())


def resolved_custom_config() -> CustomWordConfig | None:
    positives = parse_words(st.session_state.custom_positive_text)
    negatives = parse_words(st.session_state.custom_negative_text)
    yy_text = st.session_state.custom_yy_text.strip()
    zz_text = st.session_state.custom_zz_text.strip()
    if not positives and not negatives and not yy_text and not zz_text:
        return None
    return CustomWordConfig(
        positives=positives,
        negatives=negatives,
        yy_text=yy_text,
        zz_text=zz_text,
    )


def presets() -> list[CustomPreset]:
    return st.session_state.presets


def reset_for_retest() -> None:
    """清除一次测试的全部运行状态，同时保留已保存预设。"""
    st.session_state.page = "home"
    st.session_state.concept_text = ""
    st.session_state.pending_custom_config = None
    st.session_state.session = None
    st.session_state.task_progress = None
    st.session_state.last_reaction_event_id = None
    st.session_state.last_reaction_event = None
    st.session_state.custom_dialog_open = False
    st.session_state.preset_history_open = False
    st.session_state.selected_preset_id = None
    st.session_state.custom_positive_text = ""
    st.session_state.custom_negative_text = ""
    st.session_state.custom_yy_text = ""
    st.session_state.custom_zz_text = ""
    st.session_state.pop("concept_input", None)
