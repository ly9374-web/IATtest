"""SwiftUI ReportView 的 Streamlit 版本。"""

from __future__ import annotations

from datetime import date
from html import escape
from textwrap import dedent

import streamlit as st

from iat_core.scoring import IATReport
from .charts import build_scatter_svg
from .state import reset_for_retest


def _html(source: str) -> None:
    st.markdown(dedent(source).strip(), unsafe_allow_html=True)


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


def _d_score_level(report: IATReport) -> str:
    absolute = abs(report.d_score)
    if absolute < 0.15:
        return "无明显"
    if absolute < 0.35:
        return "轻微"
    if absolute < 0.65:
        return "中"
    return "强"


def _attitude_label(concept: str, report: IATReport) -> str:
    level = _d_score_level(report)
    if level == "无明显":
        return f"对{concept}态度显著度：无明显"
    direction = "正面" if report.d_score > 0 else "负面"
    return f"对{concept}{direction}态度显著度：{level}"


def _slower_pair_text(concept: str, report: IATReport) -> str:
    compatible = report.compatible_mean_ms
    incompatible = report.incompatible_mean_ms
    if compatible == incompatible:
        return f"D_work: {report.d_score:.2f}，目标词汇与正面/负面词汇反应时无明显差异"

    slower_label = "负面词汇" if incompatible > compatible else "正面词汇"
    slower = max(compatible, incompatible)
    faster = min(compatible, incompatible)
    percent = 0 if slower <= 0 else round((slower - faster) / slower * 100)
    return (
        f"D_work: {report.d_score:.2f}，"
        f"{concept}与{slower_label}反应时变长（{percent}%）"
    )


def _overview_grid(concept: str, report: IATReport) -> str:
    rows = [
        (
            "内隐联想测试（IAT）",
            _slower_pair_text(concept, report),
            _attitude_label(concept, report),
        ),
        ("心率变异性（HRV）", "任务时增幅 28%，Delta HR (+12 至 +15)", "应激反应明显"),
        ("负向微表情", "总共负向微表情为13%", "情绪稳定性适中"),
        ("心率恢复性（HR）", "任务后降幅 18%，Delta HR (-10至-12)", "恢复较慢（p60）"),
        (
            "目标词匹配错误率",
            "与正面词匹配时错误率为7%，与负面词匹配时错误率为12%",
            "错误差异明显（p74）",
        ),
    ]
    header = (
        '<div class="iat-overview-cell head">指标类别</div>'
        '<div class="iat-overview-cell head">具体数据</div>'
        '<div class="iat-overview-cell head">偏离度评估</div>'
    )
    body = "".join(
        (
            f'<div class="iat-overview-cell">{escape(category)}</div>'
            f'<div class="iat-overview-cell">{escape(value)}</div>'
            f'<div class="iat-overview-cell eval">{escape(evaluation)}</div>'
        )
        for category, value, evaluation in rows
    )
    return f'<div class="iat-overview-grid">{header}{body}</div>'


def _heart_rate_svg() -> str:
    return dedent("""
    <svg class="iat-hr-chart" viewBox="0 0 920 260" role="img" aria-label="心率图">
        <rect x="0" y="0" width="920" height="260" fill="#fff" />
        <g class="grid">
            <path d="M72 26 H884 M72 64 H884 M72 102 H884 M72 140 H884 M72 178 H884 M72 216 H884" />
            <path d="M72 26 V216 M140 26 V216 M208 26 V216 M276 26 V216 M344 26 V216 M412 26 V216 M480 26 V216 M548 26 V216 M616 26 V216 M684 26 V216 M752 26 V216 M820 26 V216 M884 26 V216" />
        </g>
        <path class="axis" d="M72 26 V216 H884" />
        <polyline class="hr-line" points="72,170 122,169 172,170 222,169 272,168 322,166 372,155 422,146 472,128 522,108 572,88 622,64 672,54 722,62 772,70 822,82 884,96" />
        <g class="labels">
            <text x="38" y="221">20</text><text x="38" y="183">40</text><text x="38" y="145">60</text>
            <text x="38" y="107">80</text><text x="30" y="69">120</text><text x="30" y="31">140</text>
            <text x="72" y="242">00:00</text><text x="204" y="242">04:00</text><text x="340" y="242">08:00</text>
            <text x="476" y="242">12:00</text><text x="612" y="242">16:00</text><text x="748" y="242">20:00</text>
            <text x="862" y="242">24:00</text><text x="454" y="258">时间</text>
            <text transform="translate(24 136) rotate(-90)">心率（次/分）</text>
        </g>
    </svg>
    """).strip()


def _expression_chart() -> str:
    values = [28, 45, 32, 51, 37, 24, 41]
    bars = []
    for index, value in enumerate(values, start=1):
        x = 92 + (index - 1) * 116
        height = value * 2.55
        y = 200 - height
        bars.append(
            f'<rect x="{x}" y="{y:.1f}" width="46" height="{height:.1f}" />'
            f'<text x="{x + 23}" y="{y - 8:.1f}" text-anchor="middle">{value}</text>'
            f'<text x="{x + 23}" y="228" text-anchor="middle">轮次{index}</text>'
        )
    return (
        '<svg class="iat-expression-chart" viewBox="0 0 920 260" role="img" aria-label="负面表情">'
        '<rect x="0" y="0" width="920" height="260" fill="#fff" />'
        '<g class="grid"><path d="M72 20 H884 M72 56 H884 M72 92 H884 M72 128 H884 M72 164 H884 M72 200 H884" /></g>'
        '<path class="axis" d="M72 20 V200 H884" />'
        '<g class="bar-labels"><text x="40" y="205">0</text><text x="34" y="169">10</text><text x="34" y="133">20</text><text x="34" y="97">30</text><text x="34" y="61">40</text><text x="34" y="25">60</text><text transform="translate(26 118) rotate(-90)">次数</text></g>'
        '<g class="bars">'
        + "".join(bars)
        + "</g></svg>"
    )


def _analysis_cards() -> str:
    cards = [
        (
            "情绪稳定性",
            "轻度波动",
            "行为分析",
            "情绪波动处于可观察范围内，存在一定负性反应，但不直接等同于长期情绪稳定性问题。",
            "建议进行常规班前状态确认，并关注近期睡眠、压力和工作沟通情况。",
            "neutral",
        ),
        (
            "抗压能力",
            "偏弱",
            "行为分析",
            "存在明显心率应激反应，且测试后恢复偏慢，说明其在压力情境下可能难以快速调节压力负荷。",
            "禁止其单独执行高压或突发性任务，建议优先安排搭档作业，并关注近期休息与连续作业情况。",
            "danger",
        ),
        (
            "性格与心态倾向",
            "不单独判定为高风险",
            "行为分析",
            "当前测试结果提示该人员对工作存在较明显负向自动联结，但不能直接解释为主观抵触、不服从管理或违规倾向。",
            "建议结合面谈了解实际心态，重点关注近期工作压力、班组关系和排班情况。",
            "neutral",
        ),
        (
            "职业倦怠风险",
            "较明显",
            "行为分析",
            "数据模式提示存在一定工作负向联结，并伴随目标词匹配表现差异。该结果更适合解释为职业倦怠或近期压力负荷相关风险，不宜直接解释为主观消极或故意抵触。",
            "需尽快介入调整排班或安排阶段性休整，建议关注连续作业时长、夜班、睡眠和近期工作负荷。",
            "warning",
        ),
        (
            "人际关系",
            "较明显",
            "行为分析",
            "人际关系中等",
            "存在一定人际适应或沟通关注信号，建议结合日常协作表现观察",
            "warning compact",
        ),
    ]
    return "".join(
        (
            f'<article class="iat-analysis-card {escape(tone)}">'
            f'<div class="card-head"><h3>{escape(title)}</h3><span>{escape(badge)}</span></div>'
            f'<p class="eyebrow">{escape(eyebrow)}</p>'
            f'<p>{escape(body)}</p>'
            '<div class="card-rule"></div>'
            '<p class="eyebrow warn">建议</p>'
            f'<p>{escape(advice)}</p>'
            "</article>"
        )
        for title, badge, eyebrow, body, advice, tone in cards
    )


def render_report() -> None:
    session = st.session_state.session
    report = session.report
    if report is None:
        st.session_state.page = "task"
        st.rerun()

    with st.container(key="report_shell"):
        report_date = "2026-06-23"
        today = date.today().isoformat()
        _html(
            f"""
            <div class="iat-safety-header">
                <div>
                    <h1>作业人员心理安全辅助评估报告</h1>
                    <p>基于 IAT、心率、HRV 与表情行为数据的综合辅助评估</p>
                </div>
                <div class="iat-report-meta">
                    <strong>日期: {escape(report_date)}</strong>
                    <span>内部安全管理参考</span>
                </div>
            </div>
            """
        )
        _html('<div class="iat-report-rule"></div>')
        _html(
            """
            <section class="iat-risk-banner">
                <div class="iat-risk-icon">▲</div>
                <div>
                    <h2>综合风险提示</h2>
                    <p>关注抗压能力与职业倦怠，暂不建议单独安排突发高压作业。</p>
                </div>
            </section>
            """
        )
        _html(
            f"""
            <section class="iat-worker-card">
                <div><span>员工编号</span><strong>A0231</strong></div>
                <div><span>岗位</span><strong>设备检修</strong></div>
                <div><span>评估日期</span><strong>{escape(report_date)}</strong></div>
                <div class="wide"><span>评估方法</span><strong>工作 IAT + 心率 + HRV + 表情分析综合数据采集</strong></div>
            </section>
            """
        )
        _html(
            f"""
            <section class="iat-overview">
                <h2><span>▦</span>核心数据概览</h2>
                {_overview_grid(session.concept, report)}
            </section>
            """
        )
        _html(
            f"""
            <section class="iat-chart-section iat-real-scatter">
                <h3>散点图</h3>
                {build_scatter_svg(report.scatter_points)}
            </section>
            """
        )
        _html(
            f"""
            <section class="iat-chart-section">
                <div class="iat-chart-tab">心率</div>
                {_heart_rate_svg()}
            </section>
            """
        )
        _html(
            f"""
            <section class="iat-chart-section">
                <div class="iat-chart-tab blue">负面表情</div>
                {_expression_chart()}
            </section>
            """
        )
        _html(
            f"""
            <section class="iat-analysis">
                <h2><span>◔</span>维度详情分析</h2>
                <div class="iat-analysis-grid">{_analysis_cards()}</div>
            </section>
            """
        )
        _html(
            f"""
            <div class="iat-safety-footer">
                <p>—— 工业心理安全数据中心 自动生成 ——</p>
                <small>生成日期: {escape(today)}</small>
            </div>
            """
        )

    with st.container(key="report_retest_container"):
        if st.button("重新测试", key="report_retest", type="primary"):
            reset_for_retest()
            st.rerun()
