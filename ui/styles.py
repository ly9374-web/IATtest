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

        .st-key-home_start_container {
            width: 160px;
            margin: 0 auto;
        }

        .st-key-home_start_container .stButton {
            width: 160px;
        }

        .st-key-home_start_container button {
            width: 160px !important;
            padding: 0 !important;
        }

        .st-key-home_start_container button {
            height: 48px !important;
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
            width: min(100%, 1180px);
            margin: 0 auto;
            padding: 54px 48px 42px;
            background: #ffffff;
            color: #20242a;
        }

        .iat-safety-header {
            display: flex;
            justify-content: space-between;
            gap: 32px;
        }

        .iat-safety-header h1 {
            margin: 0;
            font-size: 42px;
            line-height: 1.12;
            font-weight: 500;
            letter-spacing: 0;
        }

        .iat-safety-header p {
            margin: 22px 0 0;
            color: #737985;
            font-size: 19px;
        }

        .iat-report-meta {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 12px;
            color: #6f7480;
            font-size: 16px;
            white-space: nowrap;
        }

        .iat-report-meta span {
            padding: 8px 16px;
            border-radius: 3px;
            background: #e0e2e6;
            color: #5b606a;
            font-weight: 600;
        }

        .iat-report-rule {
            height: 1px;
            background: #c8ccd6;
            margin: 36px 0 36px;
        }

        .iat-risk-banner {
            display: flex;
            align-items: flex-start;
            gap: 18px;
            padding: 28px 28px;
            background: #ffd9d6;
            border-radius: 4px;
            color: #a30012;
        }

        .iat-risk-icon {
            font-size: 30px;
            line-height: 1;
            margin-top: 4px;
        }

        .iat-risk-banner h2 {
            margin: 0 0 12px;
            font-size: 24px;
            font-weight: 500;
        }

        .iat-risk-banner p {
            margin: 0;
            font-size: 19px;
            font-weight: 500;
        }

        .iat-worker-card {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 34px 72px;
            margin-top: 34px;
            padding: 34px 28px 30px;
            border: 1px solid #bfc5d3;
            border-radius: 4px;
            background: #fafbfe;
        }

        .iat-worker-card div {
            min-width: 0;
        }

        .iat-worker-card .wide {
            grid-column: 1 / -1;
        }

        .iat-worker-card span {
            display: block;
            color: #7b808b;
            font-size: 15px;
            font-weight: 500;
        }

        .iat-worker-card strong {
            display: block;
            margin-top: 12px;
            font-size: 20px;
            line-height: 1.35;
            font-weight: 500;
        }

        .iat-overview {
            margin-top: 46px;
        }

        .iat-overview h2,
        .iat-analysis h2 {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 0 0 24px;
            font-size: 28px;
            line-height: 1.2;
            font-weight: 500;
        }

        .iat-overview h2 span,
        .iat-analysis h2 span {
            color: #727884;
            font-size: 24px;
        }

        .iat-overview-grid {
            display: grid;
            grid-template-columns: 22% 54% 24%;
            width: 100%;
            font-size: 16px;
        }

        .iat-overview-cell {
            padding: 18px 10px;
            border-bottom: 1px solid #dcdfe6;
            line-height: 1.4;
            min-width: 0;
        }

        .iat-overview-cell.head {
            padding-top: 0;
            padding-bottom: 14px;
            border-bottom-color: #cdd2dc;
            color: #7b808b;
            font-size: 15px;
            font-weight: 500;
        }

        .iat-overview-cell.eval {
            color: #4f5561;
        }

        .iat-chart-section {
            margin-top: 34px;
            position: relative;
        }

        .iat-chart-section h3 {
            margin: 0 0 12px;
            font-size: 16px;
            font-weight: 700;
        }

        .iat-real-scatter {
            padding: 0 28px;
        }

        .iat-real-scatter .iat-scatter-chart {
            width: 100%;
            height: 240px;
        }

        .iat-real-scatter .iat-scatter-chart svg {
            display: block;
            width: 100%;
            height: 240px;
        }

        .iat-chart-tab {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 90px;
            height: 28px;
            margin-left: 10px;
            border: 1px solid #d6d9e0;
            border-radius: 6px;
            color: #1f242b;
            background: #ffffff;
            font-weight: 700;
            font-size: 15px;
        }

        .iat-chart-tab.blue {
            margin-left: 14px;
            padding: 0 18px;
            border-radius: 0;
            border-color: #2f76ef;
            background: #2f76ef;
            color: #ffffff;
        }

        .iat-hr-chart,
        .iat-expression-chart {
            display: block;
            width: 100%;
            height: auto;
            margin-top: 8px;
            border: 1px solid rgba(221, 224, 231, 0.9);
        }

        .iat-hr-chart {
            border: 0;
        }

        .iat-hr-chart .grid path,
        .iat-expression-chart .grid path {
            fill: none;
            stroke: #d9dde5;
            stroke-width: 1;
            stroke-dasharray: 4 4;
        }

        .iat-hr-chart .axis,
        .iat-expression-chart .axis {
            fill: none;
            stroke: #6d7178;
            stroke-width: 2;
        }

        .iat-hr-chart .hr-line {
            fill: none;
            stroke: #2c73ff;
            stroke-width: 2.5;
        }

        .iat-hr-chart text,
        .iat-expression-chart text {
            fill: #2c3037;
            font-size: 13px;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
                         "Segoe UI", sans-serif;
        }

        .iat-expression-chart .bars rect {
            fill: #2d73ea;
        }

        .iat-expression-chart .bars text {
            font-size: 15px;
            font-weight: 600;
        }

        .iat-analysis {
            margin-top: 44px;
        }

        .iat-analysis-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 34px 28px;
        }

        .iat-analysis-card {
            border: 1px solid #c5cad5;
            border-radius: 4px;
            padding: 26px 28px 24px;
            min-height: 218px;
        }

        .iat-analysis-card.danger {
            border: 2px solid #d92828;
        }

        .iat-analysis-card.warning {
            border-color: #6f2a04;
            box-shadow: inset 4px 0 0 #6f2a04;
        }

        .iat-analysis-card.compact {
            min-height: 170px;
        }

        .iat-analysis-card .card-head {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 22px;
        }

        .iat-analysis-card h3 {
            margin: 0;
            font-size: 24px;
            font-weight: 500;
        }

        .iat-analysis-card .card-head span {
            padding: 6px 12px;
            border-radius: 3px;
            background: #e1e3e7;
            color: #555b66;
            font-size: 14px;
            white-space: nowrap;
        }

        .iat-analysis-card.danger .card-head span {
            background: #ffdede;
            color: #cf1f1f;
        }

        .iat-analysis-card.warning .card-head span {
            background: #743000;
            color: #ffcda7;
        }

        .iat-analysis-card p {
            margin: 0;
            font-size: 16px;
            line-height: 1.55;
        }

        .iat-analysis-card .eyebrow {
            color: #818690;
            margin-bottom: 8px;
        }

        .iat-analysis-card .eyebrow.warn {
            color: #a12020;
        }

        .iat-analysis-card .card-rule {
            height: 1px;
            margin: 24px 0 20px;
            background: #dedfe5;
        }

        .iat-safety-footer {
            margin-top: 56px;
            padding-top: 28px;
            border-top: 1px solid #d8dce5;
            text-align: center;
            color: #888e99;
        }

        .iat-safety-footer p {
            margin: 0;
            font-size: 15px;
        }

        .iat-safety-footer small {
            display: none;
        }

        .st-key-report_retest_container {
            width: 120px;
            margin: 16px auto 32px;
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
