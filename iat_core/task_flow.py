"""与 UI 无关的 IAT 答题流程控制器。"""

from __future__ import annotations

from dataclasses import dataclass

from .models import IATBlock, IATTrial
from .session import IATSession


@dataclass(frozen=True, slots=True)
class TaskEventOutcome:
    accepted: bool
    recorded: bool = False
    advanced: bool = False
    finished: bool = False


@dataclass(slots=True)
class TaskProgress:
    block_index: int = 0
    trial_index: int = 0
    show_block_intro: bool = True

    def current_block(self, session: IATSession) -> IATBlock:
        return session.blocks[self.block_index]

    def current_trial(self, session: IATSession) -> IATTrial:
        return self.current_block(session).trials[self.trial_index]

    @property
    def trial_id(self) -> str:
        return f"{self.block_index}:{self.trial_index}"

    def remaining_count(self, session: IATSession) -> int:
        return len(self.current_block(session).trials) - self.trial_index

    def confirm_block_intro(self) -> None:
        self.show_block_intro = False

    def record_first_response(
        self,
        session: IATSession,
        *,
        first_key: str,
        is_correct: bool,
        rt_ms: float,
    ) -> None:
        session.record_response(
            block_index=self.block_index,
            trial_index=self.trial_index,
            first_key=first_key,
            is_correct=is_correct,
            rt_ms=rt_ms,
        )

    def advance(self, session: IATSession) -> bool:
        """推进一题；完成全部 Block 时生成报告并返回 True。"""
        block = self.current_block(session)
        if self.trial_index + 1 < len(block.trials):
            self.trial_index += 1
            return False

        if self.block_index + 1 < len(session.blocks):
            self.block_index += 1
            self.trial_index = 0
            self.show_block_intro = True
            return False

        session.finalize()
        return True

    def skip_current_block(self, session: IATSession) -> bool:
        """按 Swift 基线以正确键、正确、800ms 填充当前 Block 剩余题。"""
        block = self.current_block(session)
        for index in range(self.trial_index, len(block.trials)):
            trial = block.trials[index]
            session.record_response(
                block_index=self.block_index,
                trial_index=index,
                first_key=trial.correct_key,
                is_correct=True,
                rt_ms=800,
            )

        if self.block_index + 1 < len(session.blocks):
            self.block_index += 1
            self.trial_index = 0
            self.show_block_intro = True
            return False

        session.finalize()
        return True

    def process_reaction_event(
        self,
        session: IATSession,
        *,
        event_type: str,
        event_trial_id: str,
        first_key: str,
        is_correct: bool,
        rt_ms: float | None,
    ) -> TaskEventOutcome:
        """校验并处理来自浏览器组件的领域事件。"""
        if event_trial_id != self.trial_id:
            return TaskEventOutcome(accepted=False)

        if event_type == "trial_complete":
            if rt_ms is None:
                return TaskEventOutcome(accepted=False)
            response = session.response_for(
                self.block_index,
                self.trial_index,
            )
            if response is None or response.first_key is not None:
                return TaskEventOutcome(accepted=False)
            self.record_first_response(
                session,
                first_key=first_key,
                is_correct=is_correct,
                rt_ms=rt_ms,
            )
            finished = self.advance(session)
            return TaskEventOutcome(
                accepted=True,
                recorded=True,
                advanced=True,
                finished=finished,
            )

        return TaskEventOutcome(accepted=False)


def block_instruction_text(block: IATBlock, concept: str) -> str:
    if block.id == 1:
        return f"其他按 S，{concept} 按 J"
    if block.id == 2:
        return "正面按 S，负面按 J"
    if block.id in {3, 4}:
        return f"其他和正面按 S，{concept} 和负面按 J"
    if block.id == 5:
        return f"{concept} 按 S，其他按 J"
    if block.id in {6, 7}:
        return f"{concept} 和正面按 S，其他和负面按 J"
    return (
        f"当出现 {block.left_label} 时按 “S”，"
        f"当出现 {block.right_label} 时按 “J”。"
    )
