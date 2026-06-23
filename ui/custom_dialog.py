"""自定义词库弹窗。"""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from iat_core.models import CustomPreset
from iat_core.preset_store import CustomPresetStore


def _close_dialog() -> None:
    st.session_state.custom_dialog_open = False
    st.rerun()


def _select_preset(preset: CustomPreset) -> None:
    st.session_state.custom_positive_text = preset.positive_text
    st.session_state.custom_negative_text = preset.negative_text
    st.session_state.custom_yy_text = preset.yy_text
    st.session_state.custom_zz_text = preset.zz_text
    st.session_state.selected_preset_id = preset.id


def _delete_preset(preset: CustomPreset, store: CustomPresetStore) -> None:
    st.session_state.presets = [
        item for item in st.session_state.presets if item.id != preset.id
    ]
    if st.session_state.selected_preset_id == preset.id:
        st.session_state.selected_preset_id = None
    store.save(st.session_state.presets)
    st.rerun()


def _save_preset(store: CustomPresetStore) -> None:
    selected_id = st.session_state.selected_preset_id
    updated = list(st.session_state.presets)
    match = next(
        (item for item in updated if item.id == selected_id),
        None,
    )
    if match is not None:
        match.positive_text = st.session_state.custom_positive_text
        match.negative_text = st.session_state.custom_negative_text
        match.updated_at = datetime.now(timezone.utc).isoformat()
    else:
        preset = CustomPreset.create(
            positive_text=st.session_state.custom_positive_text,
            negative_text=st.session_state.custom_negative_text,
            yy_text=st.session_state.custom_yy_text.strip(),
            zz_text=st.session_state.custom_zz_text.strip(),
        )
        updated.insert(0, preset)
        st.session_state.selected_preset_id = preset.id

    st.session_state.presets = updated
    store.save(updated)
    st.session_state.custom_dialog_open = False
    st.rerun()


@st.dialog("自定义", width="small")
def render_custom_dialog(store: CustomPresetStore) -> None:
    with st.container(key="dialog_close_container"):
        if st.button("✕", key="dialog_close", help="关闭"):
            _close_dialog()

    st.markdown(
        '<div class="iat-dialog-title">自定义</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="iat-dialog-spacer-16"></div>', unsafe_allow_html=True)

    st.text_area(
        "正面词汇",
        placeholder="正面词汇（输入正面词汇匹配词）",
        key="custom_positive_text",
        label_visibility="collapsed",
    )
    st.markdown('<div class="iat-dialog-spacer-12"></div>', unsafe_allow_html=True)
    st.text_area(
        "负面词汇",
        placeholder="负面词汇（输入负面词汇匹配词）",
        key="custom_negative_text",
        label_visibility="collapsed",
    )
    st.markdown('<div class="iat-dialog-spacer-12"></div>', unsafe_allow_html=True)

    yy_column, zz_column = st.columns(2, gap="small")
    is_selected = st.session_state.selected_preset_id is not None
    with yy_column:
        st.text_input(
            "yy",
            placeholder="yy（正面词汇更快）",
            key="custom_yy_text",
            disabled=is_selected,
            label_visibility="collapsed",
        )
    with zz_column:
        st.text_input(
            "zz",
            placeholder="zz（负面词汇更快）",
            key="custom_zz_text",
            disabled=is_selected,
            label_visibility="collapsed",
        )

    if st.session_state.preset_history_open:
        st.markdown('<div class="iat-dialog-spacer-16"></div>', unsafe_allow_html=True)
        with st.container(height=220, border=True, key="history_list"):
            for preset in st.session_state.presets:
                name_column, delete_column = st.columns([8, 1], gap="small")
                with name_column:
                    with st.container(key=f"history_name_{preset.id}"):
                        st.button(
                            preset.display_name,
                            key=f"select_preset_{preset.id}",
                            use_container_width=True,
                            on_click=_select_preset,
                            args=(preset,),
                        )
                with delete_column:
                    if st.button(
                        "✕",
                        key=f"delete_preset_{preset.id}",
                        help="删除",
                    ):
                        _delete_preset(preset, store)

    st.markdown('<div class="iat-dialog-spacer-16"></div>', unsafe_allow_html=True)
    with st.container(key="dialog_actions"):
        history_column, confirm_column, save_column = st.columns(3, gap="medium")
        with history_column:
            if st.button("历史", key="toggle_history", use_container_width=True):
                st.session_state.preset_history_open = (
                    not st.session_state.preset_history_open
                )
                st.rerun()
        with confirm_column:
            if st.button(
                "确定",
                key="confirm_preset",
                type="primary",
                use_container_width=True,
            ):
                _save_preset(store)
        with save_column:
            if st.button("保存", key="save_preset", use_container_width=True):
                _save_preset(store)
