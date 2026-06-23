"""Streamlit 反应任务组件的 Python 封装与事件去重。"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any, Mapping

import streamlit.components.v1 as components

_FRONTEND_PATH = Path(__file__).resolve().parent / "frontend"
_component = components.declare_component(
    "iat_reaction_task",
    path=_FRONTEND_PATH,
)

EVENT_VERSION = 1
EVENT_TYPES = frozenset({"trial_complete", "block_start", "skip_block"})


@dataclass(frozen=True, slots=True)
class ReactionEvent:
    version: int
    event_id: str
    type: str
    trial_id: str
    key: str | None
    correct_key: str | None
    first_key: str | None
    is_correct: bool | None
    rt_ms: float | None
    reason: str
    client_time_ms: float

    @classmethod
    def from_value(
        cls,
        value: Mapping[str, Any] | None,
    ) -> ReactionEvent | None:
        if not value:
            return None
        try:
            version = int(value["version"])
            event_type = str(value["type"])
            raw_key = value.get("key")
            raw_correct_key = value.get("correct_key")
            raw_first_key = value.get("first_key")
            raw_rt = value.get("rt_ms")
            event = cls(
                version=version,
                event_id=str(value["event_id"]),
                type=event_type,
                trial_id=str(value["trial_id"]),
                key=None if raw_key is None else str(raw_key).upper(),
                correct_key=(
                    None
                    if raw_correct_key is None
                    else str(raw_correct_key).upper()
                ),
                first_key=(
                    None
                    if raw_first_key is None
                    else str(raw_first_key).upper()
                ),
                is_correct=value.get("is_correct"),
                rt_ms=None if raw_rt is None else float(raw_rt),
                reason=str(value["reason"]),
                client_time_ms=float(value["client_time_ms"]),
            )
        except (KeyError, TypeError, ValueError):
            return None

        if (
            event.version != EVENT_VERSION
            or event.type not in EVENT_TYPES
            or not event.event_id
            or not event.trial_id
        ):
            return None
        if event.type == "trial_complete":
            if (
                event.key not in {"S", "J"}
                or event.correct_key not in {"S", "J"}
                or event.first_key not in {"S", "J"}
                or not isinstance(event.is_correct, bool)
                or event.rt_ms is None
            ):
                return None
        elif any(
            item is not None
            for item in (
                event.key,
                event.correct_key,
                event.first_key,
                event.is_correct,
                event.rt_ms,
            )
        ):
            return None
        if event.rt_ms is not None and (
            not math.isfinite(event.rt_ms) or event.rt_ms < 0
        ):
            return None
        if not math.isfinite(event.client_time_ms):
            return None
        return event


def reaction_task(
    *,
    trial_id: str,
    stimulus: str,
    correct_key: str,
    left_label: str = "",
    right_label: str = "",
    remaining_count: int = 0,
    block_title: str = "",
    block_instruction: str = "",
    block_count: int = 0,
    enabled: bool = True,
    block_intro_open: bool = False,
    transitioning: bool = False,
    key: str | None = None,
) -> ReactionEvent | None:
    """渲染反应表面并返回最新浏览器事件。"""
    normalized_key = correct_key.upper()
    if normalized_key not in {"S", "J"}:
        raise ValueError("correct_key must be 'S' or 'J'")
    value = _component(
        trial_id=str(trial_id),
        stimulus=stimulus,
        correct_key=normalized_key,
        left_label=left_label,
        right_label=right_label,
        remaining_count=int(remaining_count),
        block_title=block_title,
        block_instruction=block_instruction,
        block_count=int(block_count),
        enabled=enabled,
        block_intro_open=block_intro_open,
        transitioning=transitioning,
        default=None,
        key=key or f"reaction_task_{trial_id}",
        tab_index=0,
    )
    return ReactionEvent.from_value(value)


def consume_new_event(
    event: ReactionEvent | None,
    last_event_id: str | None,
) -> tuple[ReactionEvent | None, str | None]:
    """返回尚未处理的事件及应保存的新 ID。"""
    if event is None or event.event_id == last_event_id:
        return None, last_event_id
    return event, event.event_id


__all__ = [
    "EVENT_TYPES",
    "EVENT_VERSION",
    "ReactionEvent",
    "consume_new_event",
    "reaction_task",
]
