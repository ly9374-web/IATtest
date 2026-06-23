from __future__ import annotations

import unittest

from iat_core import IATSession, TaskProgress, block_instruction_text


class TaskProgressTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = IATSession.create(
            concept="环保",
            is_precise_mode=True,
            seed=20260622,
            subject_id="task-flow",
        )
        self.progress = TaskProgress()

    def test_correct_response_records_then_advances(self) -> None:
        self.progress.confirm_block_intro()
        trial = self.progress.current_trial(self.session)
        recorded = self.progress.process_reaction_event(
            self.session,
            event_type="trial_complete",
            event_trial_id="0:0",
            first_key=trial.correct_key,
            is_correct=True,
            rt_ms=425.5,
        )
        self.assertTrue(recorded.recorded)
        response = self.session.response_for(0, 0)
        assert response is not None
        self.assertEqual(response.first_key, trial.correct_key)
        self.assertTrue(response.is_correct)
        self.assertEqual(response.rt_ms, 425.5)
        self.assertTrue(recorded.advanced)
        self.assertFalse(recorded.finished)
        self.assertEqual(self.progress.trial_index, 1)
        self.assertFalse(self.progress.show_block_intro)

    def test_first_error_is_preserved_after_correction_advance(self) -> None:
        self.progress.confirm_block_intro()
        trial = self.progress.current_trial(self.session)
        wrong_key = "J" if trial.correct_key == "S" else "S"
        recorded = self.progress.process_reaction_event(
            self.session,
            event_type="trial_complete",
            event_trial_id="0:0",
            first_key=wrong_key,
            is_correct=False,
            rt_ms=310,
        )
        self.assertTrue(recorded.recorded)

        self.assertTrue(recorded.advanced)
        response = self.session.response_for(0, 0)
        assert response is not None
        self.assertEqual(response.first_key, wrong_key)
        self.assertFalse(response.is_correct)
        self.assertEqual(response.rt_ms, 310)

    def test_stale_and_duplicate_events_are_ignored(self) -> None:
        stale = self.progress.process_reaction_event(
            self.session,
            event_type="trial_complete",
            event_trial_id="6:14",
            first_key="S",
            is_correct=True,
            rt_ms=100,
        )
        self.assertFalse(stale.accepted)

        trial = self.progress.current_trial(self.session)
        first = self.progress.process_reaction_event(
            self.session,
            event_type="trial_complete",
            event_trial_id="0:0",
            first_key=trial.correct_key,
            is_correct=True,
            rt_ms=500,
        )
        duplicate = self.progress.process_reaction_event(
            self.session,
            event_type="trial_complete",
            event_trial_id="0:0",
            first_key=trial.correct_key,
            is_correct=True,
            rt_ms=900,
        )
        self.assertTrue(first.accepted)
        self.assertFalse(duplicate.accepted)
        response = self.session.response_for(0, 0)
        assert response is not None
        self.assertEqual(response.rt_ms, 500)

    def test_block_boundary_opens_next_intro(self) -> None:
        self.progress.block_index = 0
        self.progress.trial_index = 7
        self.progress.show_block_intro = False
        trial = self.progress.current_trial(self.session)
        self.progress.record_first_response(
            self.session,
            first_key=trial.correct_key,
            is_correct=True,
            rt_ms=500,
        )
        finished = self.progress.advance(self.session)
        self.assertFalse(finished)
        self.assertEqual(self.progress.block_index, 1)
        self.assertEqual(self.progress.trial_index, 0)
        self.assertTrue(self.progress.show_block_intro)

    def test_skip_fills_remaining_trials_with_swift_defaults(self) -> None:
        self.progress.trial_index = 3
        finished = self.progress.skip_current_block(self.session)
        self.assertFalse(finished)
        for index in range(3, 8):
            response = self.session.response_for(0, index)
            trial = self.session.blocks[0].trials[index]
            assert response is not None
            self.assertEqual(response.first_key, trial.correct_key)
            self.assertTrue(response.is_correct)
            self.assertEqual(response.rt_ms, 800)
        self.assertEqual(self.progress.block_index, 1)
        self.assertEqual(self.progress.trial_index, 0)
        self.assertTrue(self.progress.show_block_intro)

    def test_skipping_all_blocks_finishes_and_generates_report(self) -> None:
        finished = False
        for _ in range(7):
            finished = self.progress.skip_current_block(self.session)
        self.assertTrue(finished)
        self.assertIsNotNone(self.session.report)

    def test_normal_final_trial_finishes_and_generates_report(self) -> None:
        self.progress.block_index = 6
        self.progress.trial_index = 14
        self.progress.show_block_intro = False
        trial = self.progress.current_trial(self.session)
        self.progress.record_first_response(
            self.session,
            first_key=trial.correct_key,
            is_correct=True,
            rt_ms=700,
        )
        self.assertTrue(self.progress.advance(self.session))
        self.assertIsNotNone(self.session.report)


class BlockInstructionTests(unittest.TestCase):
    def test_all_seven_instruction_texts(self) -> None:
        session = IATSession.create(
            concept="环保",
            is_precise_mode=True,
            seed=1,
            subject_id="instructions",
        )
        self.assertEqual(
            [block_instruction_text(block, "环保") for block in session.blocks],
            [
                "中性词汇按 S，环保 按 J",
                "正面词汇按 S，负面词汇按 J",
                "中性词汇和正面词汇按 S，环保 和负面词汇按 J",
                "中性词汇和正面词汇按 S，环保 和负面词汇按 J",
                "环保 按 S，中性词汇按 J",
                "环保 和正面词汇按 S，中性词汇和负面词汇按 J",
                "环保 和正面词汇按 S，中性词汇和负面词汇按 J",
            ],
        )


if __name__ == "__main__":
    unittest.main()
