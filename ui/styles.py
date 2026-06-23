"""全局 CSS、尺寸 token 和 SwiftUI 外观映射。"""

from __future__ import annotations

import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --iat-font-size: 18px;
            --iat-secondary: rgba(49, 51, 63, 0.62);
            --iat-blue: #0a84ff;
            --iat-border: rgba(49, 51, 63, 0.22);
        }

        html, body, [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] button,
        [data-testid="stAppViewContainer"] input,
        [data-testid="stAppViewContainer"] textarea {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
                         "Segoe UI", sans-serif;
            font-size: var(--iat-font-size);
        }

        #MainMenu, footer, header,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="manage-app-button"] {
            display: none !important;
        }

        [data-testid="stAppViewContainer"] > .main {
            background: #ffffff;
        }

        .block-container {
            max-width: none !important;
            padding: 0 32px 32px !important;
        }

        .iat-nav-title {
            height: 52px;
            display: flex;
            align-items: center;
            font-size: 20px;
            font-weight: 600;
            border-bottom: 1px solid rgba(49, 51, 63, 0.12);
            margin: 0 -32px;
            padding: 0 24px;
        }

        .iat-task-block-title {
            font-weight: 400;
        }

        .st-key-home_shell {
            width: min(100%, 760px);
            margin: 0 auto;
            padding-top: 32px;
            text-align: center;
        }

        .iat-home-title {
            font-size: 34px;
            line-height: 41px;
            font-weight: 600;
            margin: 0;
        }

        .iat-spacer-44 {
            height: 44px;
        }

        .iat-spacer-6 {
            height: 6px;
        }

        .st-key-home_input {
            width: 380px;
            max-width: 100%;
            margin: 0 auto;
        }

        .st-key-home_input [data-testid="stTextInput"] {
            margin: 0;
        }

        .st-key-home_input input {
            min-height: 38px;
            border-radius: 6px;
        }

        .st-key-home_start_container,
        .st-key-home_custom_container {
            width: 160px;
            margin: 0 auto;
        }

        .st-key-home_start_container .stButton,
        .st-key-home_custom_container .stButton {
            width: 160px;
        }

        .st-key-home_start_container button,
        .st-key-home_custom_container button {
            width: 160px !important;
            padding: 0 !important;
        }

        .st-key-home_start_container button {
            height: 48px !important;
        }

        .st-key-home_custom_container button {
            height: 44px !important;
        }

        .iat-home-hints {
            color: var(--iat-secondary);
            font-size: 18px;
            line-height: 22px;
        }

        .st-key-instruction_nav {
            height: 52px;
            margin: 0 -32px;
            padding: 0 24px;
            border-bottom: 1px solid rgba(49, 51, 63, 0.12);
            position: relative;
            z-index: 3;
            background: inherit;
        }

        .st-key-instruction_nav [data-testid="stHorizontalBlock"] {
            height: 52px;
            gap: 0;
        }

        .st-key-instruction_nav button {
            width: 42px !important;
            min-height: 40px !important;
            padding: 0 !important;
            font-size: 34px !important;
            line-height: 34px !important;
        }

        .iat-instruction-nav-title {
            text-align: center;
            font-size: 20px;
            font-weight: 600;
        }

        .iat-vertical-guide {
            position: fixed;
            top: 52px;
            bottom: 0;
            width: 0;
            border-left: 1px dashed rgba(49, 51, 63, 0.6);
            pointer-events: none;
            z-index: 1;
        }

        .iat-guide-left {
            left: 35%;
        }

        .iat-guide-right {
            left: 65%;
        }

        .st-key-instruction_shell {
            width: min(100%, 560px);
            margin: 0 auto;
            padding-top: 32px;
            position: relative;
            z-index: 2;
        }

        .iat-instruction-text {
            width: 100%;
            max-width: 560px;
            text-align: left;
            font-size: 18px;
            line-height: 1.45;
        }

        .iat-instruction-spacer-24 {
            height: 24px;
        }

        .st-key-instruction_confirm_container {
            width: 160px;
            margin: 0 auto;
        }

        .st-key-instruction_confirm_container .stButton {
            width: 160px;
        }

        .st-key-instruction_confirm_container button {
            width: 160px !important;
            height: 48px !important;
            padding: 0 !important;
        }

        .st-key-task_component {
            margin: 0 -8px;
            position: relative;
            z-index: 2;
        }

        .st-key-task_component iframe {
            display: block;
            width: 100% !important;
            border: 0 !important;
        }

        .st-key-report_shell {
            margin: 0 -32px;
            padding: 24px;
        }

        .st-key-report_interpretation,
        .st-key-report_statistics,
        .st-key-report_scatter {
            margin-bottom: 20px;
        }

        .iat-report-section-title {
            font-size: 18px;
            line-height: 22px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .iat-report-interpretation {
            color: #22a447;
            font-size: 21px;
            line-height: 26px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .iat-report-secondary {
            color: var(--iat-secondary);
            font-size: 18px;
            line-height: 22px;
            margin-bottom: 8px;
        }

        .iat-stat-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 24px;
            min-height: 30px;
            font-size: 18px;
            line-height: 1.35;
        }

        .iat-stat-row span {
            min-width: 0;
        }

        .iat-stat-row strong {
            flex: 0 0 auto;
            text-align: right;
            font-weight: 600;
        }

        .iat-scatter-chart {
            width: 100%;
            height: 240px;
        }

        .iat-scatter-chart svg {
            display: block;
            width: 100%;
            height: 240px;
        }

        .st-key-report_export iframe {
            display: block;
            width: 100% !important;
            border: 0 !important;
        }

        .st-key-report_retest_container {
            width: 120px;
            margin: 20px 0 0 auto;
        }

        .st-key-report_retest_container .stButton {
            width: 120px;
        }

        .st-key-report_retest_container button {
            width: 120px !important;
            height: 44px;
        }

        [data-testid="stDialog"] [data-testid="stDialogHeader"] {
            display: none !important;
        }

        [data-testid="stDialog"] div[role="dialog"] {
            width: 568px !important;
            min-width: 520px !important;
            max-width: calc(100vw - 32px) !important;
            border-radius: 12px;
        }

        [data-testid="stDialog"] div[role="dialog"] > div {
            padding: 24px !important;
        }

        .st-key-dialog_close_container .stButton {
            width: 36px;
        }

        .st-key-dialog_close_container button {
            width: 36px !important;
            min-height: 32px !important;
            border: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            padding: 0 !important;
        }

        .iat-dialog-title {
            text-align: center;
            font-size: 24px;
            line-height: 29px;
            font-weight: 600;
        }

        .iat-dialog-spacer-16 {
            height: 16px;
        }

        .iat-dialog-spacer-12 {
            height: 12px;
        }

        [data-testid="stDialog"] textarea {
            min-height: 68px !important;
            resize: vertical;
        }

        .st-key-history_list {
            max-height: 220px;
        }

        [class*="st-key-history_name_"] button {
            border: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            text-align: left !important;
        }

        .st-key-dialog_actions button {
            min-height: 38px;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --iat-secondary: rgba(250, 250, 250, 0.58);
                --iat-border: rgba(250, 250, 250, 0.2);
            }
            [data-testid="stAppViewContainer"] > .main {
                background: #0e1117;
            }
            .iat-vertical-guide {
                border-left-color: rgba(250, 250, 250, 0.6);
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
