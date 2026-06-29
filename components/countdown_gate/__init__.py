"""浏览器端 8 秒倒计时组件。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import streamlit.components.v1 as components

_FRONTEND_PATH = Path(__file__).resolve().parent / "frontend"
_component = components.declare_component(
    "iat_countdown_gate",
    path=_FRONTEND_PATH,
)


@dataclass(frozen=True, slots=True)
class CountdownEvent:
    event_id: str
    token: str
    type: str

    @classmethod
    def from_value(
        cls,
        value: Mapping[str, Any] | None,
    ) -> CountdownEvent | None:
        if not value:
            return None
        try:
            event = cls(
                event_id=str(value["event_id"]),
                token=str(value["token"]),
                type=str(value["type"]),
            )
        except (KeyError, TypeError, ValueError):
            return None
        if (
            not event.event_id
            or not event.token
            or event.type != "countdown_complete"
        ):
            return None
        return event


def countdown_gate(
    *,
    token: str,
    title: str,
    duration_seconds: int = 8,
    key: str | None = None,
) -> CountdownEvent | None:
    value = _component(
        token=token,
        title=title,
        duration_seconds=int(duration_seconds),
        default=None,
        key=key or f"countdown_gate_{token}",
    )
    return CountdownEvent.from_value(value)


def consume_new_countdown_event(
    event: CountdownEvent | None,
    last_event_id: str | None,
) -> tuple[CountdownEvent | None, str | None]:
    if event is None or event.event_id == last_event_id:
        return None, last_event_id
    return event, event.event_id


__all__ = [
    "CountdownEvent",
    "consume_new_countdown_event",
    "countdown_gate",
]
