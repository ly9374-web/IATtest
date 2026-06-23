"""SwiftUI HomeView 的 Streamlit 对应实现。"""

from __future__ import annotations

import streamlit as st

from iat_core.preset_store import CustomPresetStore
from .custom_dialog import render_custom_dialog
from .state import resolved_custom_config


def _sync_concept_text() -> None:
    st.session_state.concept_text = st.session_state.concept_input


def _spacer(size: int) -> None:
    st.markdown(
        f'<div class="iat-spacer-{size}"></div>',
        unsafe_allow_html=True,
    )


def render_home(store: CustomPresetStore) -> None:
    st.markdown('<div class="iat-nav-title">IAT 测试</div>', unsafe_allow_html=True)
    with st.container(key="home_shell"):
        st.markdown(
            '<h1 class="iat-home-title">你要测试态度的概念</h1>',
            unsafe_allow_html=True,
        )
        _spacer(44)

        with st.container(key="home_input"):
            if "concept_input" not in st.session_state:
                st.session_state.concept_input = st.session_state.concept_text
            st.text_input(
                "测试目标",
                placeholder="输入测试目标（例如：环保）",
                key="concept_input",
                on_change=_sync_concept_text,
                label_visibility="collapsed",
            )
        _spacer(44)

        with st.container(key="home_start_container"):
            start_clicked = st.button(
                "开始",
                key="home_start",
                type="primary",
                disabled=not st.session_state.concept_text.strip(),
            )
        if start_clicked:
            st.session_state.pending_custom_config = resolved_custom_config()
            st.session_state.page = "instruction"
            st.rerun()

        _spacer(44)
        with st.container(key="home_custom_container"):
            if st.button("自定义", key="home_custom"):
                st.session_state.custom_dialog_open = True
                st.rerun()

        _spacer(44)
        st.markdown(
            """
            <div class="iat-home-hints">
                <div>测试会记录反应时与正确率</div>
                <div class="iat-spacer-6"></div>
                <div>请使用键盘按键作答</div>
                <div class="iat-spacer-6"></div>
                <div>建议在安静环境完成</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.custom_dialog_open:
        render_custom_dialog(store)
