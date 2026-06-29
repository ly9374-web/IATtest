"""倒计时中间页。"""

from __future__ import annotations

import streamlit as st

from components.countdown_gate import (
    consume_new_countdown_event,
    countdown_gate,
)


COUNTDOWN_TITLES = {
    "start": "准备开始",
    "after_block_4": "短暂休息",
    "after_block_7": "正在生成报告",
}


def start_countdown(*, kind: str, next_page: str) -> None:
    st.session_state.countdown_sequence += 1
    st.session_state.countdown_kind = kind
    st.session_state.countdown_token = (
        f"{kind}:{st.session_state.countdown_sequence}"
    )
    st.session_state.countdown_next_page = next_page
    st.session_state.last_countdown_event_id = None
    st.session_state.page = "countdown"


def render_countdown() -> None:
    token = st.session_state.countdown_token
    kind = st.session_state.countdown_kind
    next_page = st.session_state.countdown_next_page
    st.markdown('<div class="iat-nav-title">IAT 测试</div>', unsafe_allow_html=True)
    with st.container(key="countdown_shell"):
        event = countdown_gate(
            token=token,
            title=COUNTDOWN_TITLES.get(kind, "准备继续"),
            duration_seconds=8,
            key="countdown_gate_main",
        )

    new_event, latest_id = consume_new_countdown_event(
        event,
        st.session_state.last_countdown_event_id,
    )
    if new_event is None:
        return
    st.session_state.last_countdown_event_id = latest_id
    if new_event.token != token:
        return
    st.session_state.countdown_token = ""
    st.session_state.countdown_kind = ""
    st.session_state.countdown_next_page = ""
    st.session_state.page = next_page
    st.rerun()
