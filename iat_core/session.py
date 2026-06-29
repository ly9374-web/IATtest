"""IAT 会话创建与反应记录。"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .block_factory import IATBlockFactory, SeededRandomNumberGenerator
from .constants import DEFAULT_LINK_NEGATIVE, DEFAULT_LINK_POSITIVE
from .models import IATBlock, TrialResponse
from .stimuli import StimulusBank

if TYPE_CHECKING:
    from .scoring import IATReport


@dataclass(slots=True)
class IATSession:
    subject_id: str
    concept: str
    seed: int
    order_condition: int
    position_condition: int
    is_precise_mode: bool
    link_positive: str
    link_negative: str
    blocks: tuple[IATBlock, ...]
    responses: list[TrialResponse]
    report: IATReport | None = None
    _response_lookup: dict[tuple[int, int], TrialResponse] = field(
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        self._response_lookup = {
            (response.block_index, response.trial_index): response
            for response in self.responses
        }

    @classmethod
    def create(
        cls,
        concept: str,
        is_precise_mode: bool,
        *,
        seed: int | None = None,
        subject_id: str | None = None,
    ) -> IATSession:
        """创建会话。

        ``seed`` 与 ``subject_id`` 仅作为可测试性注入点；省略时分别对应
        Swift 的当前 Unix 毫秒和 UUID。
        """
        resolved_seed = (
            int(time.time() * 1000) if seed is None else seed
        ) & ((1 << 64) - 1)
        rng = SeededRandomNumberGenerator(resolved_seed)
        order_condition = 1 if rng.random_bool() else 2
        position_condition = 1 if rng.random_bool() else 2

        stimuli = StimulusBank.create(concept)
        blocks = IATBlockFactory.make_blocks(
            stimuli=stimuli,
            order_condition=order_condition,
            position_condition=position_condition,
            rng=rng,
        )
        responses = [
            TrialResponse(block_index=block_index, trial_index=trial_index)
            for block_index, block in enumerate(blocks)
            for trial_index in range(len(block.trials))
        ]
        return cls(
            subject_id=subject_id or str(uuid.uuid4()),
            concept=concept,
            seed=resolved_seed,
            order_condition=order_condition,
            position_condition=position_condition,
            is_precise_mode=is_precise_mode,
            link_positive=DEFAULT_LINK_POSITIVE,
            link_negative=DEFAULT_LINK_NEGATIVE,
            blocks=blocks,
            responses=responses,
        )

    def record_response(
        self,
        block_index: int,
        trial_index: int,
        first_key: str,
        is_correct: bool,
        rt_ms: float,
    ) -> None:
        response = self._response_lookup.get((block_index, trial_index))
        if response is None:
            return
        response.first_key = first_key
        response.is_correct = is_correct
        response.rt_ms = rt_ms

    def response_for(
        self,
        block_index: int,
        trial_index: int,
    ) -> TrialResponse | None:
        return self._response_lookup.get((block_index, trial_index))

    def finalize(self) -> None:
        from .scoring import IATReport

        self.report = IATReport.generate(
            subject_id=self.subject_id,
            concept=self.concept,
            link_positive=self.link_positive,
            link_negative=self.link_negative,
            seed=self.seed,
            order_condition=self.order_condition,
            position_condition=self.position_condition,
            blocks=self.blocks,
            responses=self.responses,
        )
