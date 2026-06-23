"""IAT Streamlit 应用入口。"""

import streamlit as st

from iat_core.preset_store import CustomPresetStore
from ui.router import render_current_page
from ui.state import initialize_state
from ui.styles import apply_global_styles


def main() -> None:
    st.set_page_config(
        page_title="IAT 测试",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    store = CustomPresetStore()
    initialize_state(store)
    apply_global_styles()
    render_current_page(store)


if __name__ == "__main__":
    main()
