"""SwiftUI ReportView 的 Streamlit 版本。"""

from __future__ import annotations

from html import escape

import streamlit as st

from components.clipboard_export import clipboard_export
from iat_core.scoring import IATReport
from .charts import render_scatter_plot
from .state import reset_for_retest


def d_score_display_text(report: IATReport, is_precise_mode: bool) -> str:
    if not is_precise_mode:
        return report.d_score_string

    absolute = abs(report.d_score)
    if absolute < 0.15:
        label = "无明显偏好"
    elif absolute < 0.35:
        label = "轻微偏好"
    elif absolute < 0.65:
        label = "中等偏好"
    else:
        label = "强偏好"
    return f"|D|：{absolute:.2f} ({label})"


def _section_title(title: str) -> None:
    st.markdown(
        f'<div class="iat-report-section-title">{escape(title)}</div>',
        unsafe_allow_html=True,
    )


def _stat_row(title: str, value: str) -> None:
    st.markdown(
        (
            '<div class="iat-stat-row">'
            f'<span>{escape(title)}</span>'
            f'<strong>{escape(value)}</strong>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_report() -> None:
    session = st.session_state.session
    report = session.report
    if report is None:
        st.session_state.page = "task"
        st.rerun()

    st.markdown('<div class="iat-nav-title">报告</div>', unsafe_allow_html=True)
    with st.container(key="report_shell"):
        with st.container(key="report_interpretation"):
            _section_title("结果解释")
            st.markdown(
                (
                    '<div class="iat-report-interpretation">'
                    f"{escape(report.interpretation_text)}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                (
                    '<div class="iat-report-secondary">'
                    "兼容正式首此眼动错误概率："
                    f"{escape(report.compatible_first_error_rate_string)}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                (
                    '<div class="iat-report-secondary">'
                    "不兼容正式首此眼动错误概率："
                    f"{escape(report.incompatible_first_error_rate_string)}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        with st.container(key="report_statistics"):
            _section_title("统计数据")
            _stat_row("兼容表情变化度", "待定")
            _stat_row("不兼容表情变化度", "待定")
            _stat_row("兼容正确率", report.compatible_accuracy_string)
            _stat_row("不兼容正确率", report.incompatible_accuracy_string)
            _stat_row(
                f"当 {session.concept} 与正面词汇配对时你的反应速度/错误率",
                report.compatible_summary_string,
            )
            _stat_row(
                f"当 {session.concept} 与负面词汇配对时你的反应速度/错误率",
                report.incompatible_summary_string,
            )
            _stat_row(
                "D 值",
                d_score_display_text(report, session.is_precise_mode),
            )

        with st.container(key="report_scatter"):
            _section_title("散点图")
            render_scatter_plot(report.scatter_points)

        with st.container(key="report_export"):
            _section_title("导出")
            clipboard_export(
                csv_text=report.csv_text,
                json_text=report.json_text,
            )

    with st.container(key="report_retest_container"):
        if st.button("重新测试", key="report_retest", type="primary"):
            reset_for_retest()
            st.rerun()
