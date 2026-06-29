"""SwiftUI TaskView 的 Streamlit 版本。"""

from __future__ import annotations

import streamlit as st

from components.reaction_task import consume_new_event, reaction_task
from iat_core.task_flow import block_instruction_text
from .countdown import start_countdown


def _after_block_transition(
    *,
    completed_block_id: int,
    finished: bool,
) -> None:
    st.session_state.last_reaction_event = None
    if finished:
        start_countdown(kind="after_block_7", next_page="report")
    elif completed_block_id == 4:
        start_countdown(kind="after_block_4", next_page="task")
    st.rerun()


def render_task() -> None:
    session = st.session_state.session
    progress = st.session_state.task_progress
    block = progress.current_block(session)
    trial = progress.current_trial(session)

    st.markdown(
        (
            '<div class="iat-nav-title iat-task-block-title">'
            f"{block.title}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    with st.container(key="task_component"):
        event = reaction_task(
            trial_id=progress.trial_id,
            stimulus=trial.stimulus,
            correct_key=trial.correct_key,
            left_label=block.left_label,
            right_label=block.right_label,
            remaining_count=progress.remaining_count(session),
            block_title=block.title,
            block_instruction=block_instruction_text(block, session.concept),
            block_count=len(block.trials),
            concept=session.concept,
            enabled=True,
            block_intro_open=progress.show_block_intro,
            transitioning=False,
            key="reaction_task_main",
        )
    new_event, latest_id = consume_new_event(
        event,
        st.session_state.last_reaction_event_id,
    )
    if new_event is not None:
        st.session_state.last_reaction_event_id = latest_id
        st.session_state.last_reaction_event = new_event
        if new_event.type == "block_start":
            progress.confirm_block_intro()
            st.rerun()
        if new_event.type == "skip_block":
            completed_block_id = block.id
            finished = progress.skip_current_block(session)
            _after_block_transition(
                completed_block_id=completed_block_id,
                finished=finished,
            )
        if (
            new_event.first_key is None
            or new_event.is_correct is None
        ):
            return
        outcome = progress.process_reaction_event(
            session,
            event_type=new_event.type,
            event_trial_id=new_event.trial_id,
            first_key=new_event.first_key,
            is_correct=new_event.is_correct,
            rt_ms=new_event.rt_ms,
        )
        if outcome.advanced:
            _after_block_transition(
                completed_block_id=block.id,
                finished=outcome.finished,
            )
