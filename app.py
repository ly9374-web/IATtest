"""IAT Streamlit 应用入口。"""

import streamlit as st

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
    initialize_state()
    apply_global_styles()
    render_current_page()


if __name__ == "__main__":
    main()
