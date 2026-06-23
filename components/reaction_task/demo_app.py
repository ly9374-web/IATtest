"""独立手动验证宿主，不属于正式 IAT 页面。"""

from __future__ import annotations

import streamlit as st

from components.reaction_task import consume_new_event, reaction_task

st.set_page_config(page_title="reaction_task demo", layout="centered")
st.title("reaction_task demo")

if "demo_trial" not in st.session_state:
    st.session_state.demo_trial = 1
if "demo_last_id" not in st.session_state:
    st.session_state.demo_last_id = None

intro_open = st.checkbox("Block 说明遮罩打开", value=False)
transitioning = st.checkbox("正在过渡", value=False)
correct_key = st.radio("正确键", ["S", "J"], horizontal=True, index=1)

event = reaction_task(
    trial_id=f"demo:{st.session_state.demo_trial}",
    stimulus="环保",
    correct_key=correct_key,
    left_label="中性词汇 + 正面词汇",
    right_label="环保 + 负面词汇",
    remaining_count=15,
    enabled=True,
    block_intro_open=intro_open,
    transitioning=transitioning,
    key="reaction_task_demo",
)
new_event, latest_id = consume_new_event(event, st.session_state.demo_last_id)
if new_event is not None:
    st.session_state.demo_last_id = latest_id
    st.json(
        {
            "event_id": new_event.event_id,
            "type": new_event.type,
            "trial_id": new_event.trial_id,
            "first_key": new_event.first_key,
            "is_correct": new_event.is_correct,
            "rt_ms": new_event.rt_ms,
            "reason": new_event.reason,
        }
    )

if st.button("切换试次"):
    st.session_state.demo_trial += 1
    st.rerun()
