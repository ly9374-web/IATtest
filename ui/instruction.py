"""SwiftUI InstructionView 的 Streamlit 对应实现。"""

from __future__ import annotations

import streamlit as st

from iat_core.session import IATSession
from iat_core.task_flow import TaskProgress

INSTRUCTION_TEXT = (
    "这是一个反应时分类任务。\n"
    "屏幕上方左右会显示两个分类标签。\n"
    "当刺激属于左侧标签时按 ‘S’，属于右侧标签时按 ‘J’。\n"
    "请尽量又快又准。按错会提示错误，需要改正后才能进入下一题。"
)


def _return_home() -> None:
    st.session_state.page = "home"
    st.session_state.session = None
    st.session_state.task_progress = None
    st.rerun()


def _start_session() -> None:
    # 会话只在确认时创建并一次性写入，避免 task 页面看到半初始化状态。
    session = IATSession.create(
        concept=st.session_state.concept_text,
        is_precise_mode=True,
    )
    st.session_state.session = session
    st.session_state.task_progress = TaskProgress()
    st.session_state.last_reaction_event_id = None
    st.session_state.last_reaction_event = None
    st.session_state.page = "task"
    st.rerun()


def render_instruction() -> None:
    with st.container(key="instruction_nav"):
        back_column, title_column, balance_column = st.columns(
            [1, 8, 1],
            vertical_alignment="center",
        )
        with back_column:
            if st.button(
                "‹",
                key="instruction_back",
                help="返回首页",
                type="tertiary",
            ):
                _return_home()
        with title_column:
            st.markdown(
                '<div class="iat-instruction-nav-title">总说明</div>',
                unsafe_allow_html=True,
            )
        with balance_column:
            st.empty()

    st.markdown(
        """
        <div class="iat-vertical-guide iat-guide-left"></div>
        <div class="iat-vertical-guide iat-guide-right"></div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="instruction_shell"):
        st.markdown(
            (
                '<div class="iat-instruction-text">'
                + INSTRUCTION_TEXT.replace("\n", "<br>")
                + "</div>"
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="iat-instruction-spacer-24"></div>',
            unsafe_allow_html=True,
        )
        with st.container(key="instruction_confirm_container"):
            if st.button(
                "确定",
                key="instruction_confirm",
                type="primary",
                shortcut="Enter",
            ):
                _start_session()
