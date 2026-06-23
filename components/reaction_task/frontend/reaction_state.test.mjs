import assert from "node:assert/strict";
import test from "node:test";

import { ReactionState, TRANSITION_MS } from "./reaction_state.mjs";

function harness() {
  let time = 1000;
  const scheduled = [];
  const state = new ReactionState({
    now: () => time,
    schedule: (callback, delay) => scheduled.push({ callback, delay }),
  });
  const emitted = [];
  state.onEvent = (event) => emitted.push(event);
  return {
    state,
    emitted,
    scheduled,
    setTime: (value) => {
      time = value;
    },
  };
}

test("blocked states reject S/J and repeat events", () => {
  const h = harness();
  h.state.configure({
    trial_id: "0:0",
    stimulus: "环保",
    correct_key: "J",
    enabled: true,
    block_intro_open: true,
    transitioning: false,
  });
  assert.deepEqual(h.state.handleKey("J"), []);
  assert.deepEqual(h.state.handleKey("J", { repeat: true }), []);
  assert.equal(h.state.snapshot().firstKey, null);
});

test("closing the block intro starts the timer", () => {
  const h = harness();
  h.state.configure({
    trial_id: "0:0",
    stimulus: "环保",
    correct_key: "J",
    enabled: true,
    block_intro_open: true,
    transitioning: false,
  });
  h.setTime(1500);
  h.state.configure({
    trial_id: "0:0",
    stimulus: "环保",
    correct_key: "J",
    enabled: true,
    block_intro_open: false,
    transitioning: false,
  });
  h.setTime(1725);
  assert.deepEqual(h.state.handleKey("J"), []);
  assert.equal(h.state.snapshot().firstRtMs, 225);
  h.scheduled[0].callback();
  assert.equal(h.emitted[0].rt_ms, 225);
});

test("external transitioning blocks keys until it ends", () => {
  const h = harness();
  h.state.configure({
    trial_id: "0:0",
    stimulus: "环保",
    correct_key: "J",
    enabled: true,
    block_intro_open: false,
    transitioning: true,
  });
  assert.deepEqual(h.state.handleKey("J"), []);

  h.setTime(1800);
  h.state.configure({
    trial_id: "0:0",
    stimulus: "环保",
    correct_key: "J",
    enabled: true,
    block_intro_open: false,
    transitioning: false,
  });
  h.setTime(2000);
  assert.deepEqual(h.state.handleKey("J"), []);
  assert.equal(h.state.snapshot().firstRtMs, 200);
});

test("first correct records RT once, turns green, then advances at 300ms", () => {
  const h = harness();
  h.state.configure({
    trial_id: "0:0",
    stimulus: "环保",
    correct_key: "J",
    enabled: true,
    block_intro_open: false,
    transitioning: false,
  });
  h.setTime(1432.25);
  assert.deepEqual(h.state.handleKey("j"), []);
  assert.equal(h.emitted.length, 0);
  assert.equal(h.state.snapshot().firstCorrect, true);
  assert.equal(h.state.snapshot().firstRtMs, 432.25);
  assert.equal(h.state.snapshot().highlightCorrect, true);
  assert.equal(h.scheduled[0].delay, TRANSITION_MS);

  h.setTime(1732.25);
  h.scheduled[0].callback();
  assert.equal(h.emitted.length, 1);
  assert.equal(h.emitted[0].type, "trial_complete");
  assert.equal(h.emitted[0].reason, "first_correct");
  assert.equal(h.emitted[0].rt_ms, 432.25);
  assert.deepEqual(h.state.handleKey("J"), []);
});

test("first error is immutable and only the correct correction advances", () => {
  const h = harness();
  h.state.configure({
    trial_id: "0:1",
    stimulus: "桌子",
    correct_key: "S",
    enabled: true,
    block_intro_open: false,
    transitioning: false,
  });
  h.setTime(1250);
  assert.deepEqual(h.state.handleKey("J"), []);
  assert.equal(h.emitted.length, 0);
  assert.equal(h.state.snapshot().firstCorrect, false);
  assert.equal(h.state.snapshot().firstRtMs, 250);
  assert.equal(h.state.snapshot().showError, true);

  h.setTime(1400);
  assert.deepEqual(h.state.handleKey("J"), []);
  assert.equal(h.scheduled.length, 0);
  assert.equal(h.state.snapshot().firstKey, "J");
  assert.equal(h.state.snapshot().firstRtMs, 250);

  assert.deepEqual(h.state.handleKey("S"), []);
  assert.equal(h.state.snapshot().highlightCorrect, true);
  assert.equal(h.scheduled[0].delay, TRANSITION_MS);
  h.scheduled[0].callback();
  assert.equal(h.emitted[0].type, "trial_complete");
  assert.equal(h.emitted[0].reason, "correction");
  assert.equal(h.emitted[0].first_key, "J");
  assert.equal(h.emitted[0].is_correct, false);
  assert.equal(h.emitted[0].rt_ms, 250);
});

test("changing trial id resets first key and restarts timing", () => {
  const h = harness();
  h.state.configure({
    trial_id: "0:0",
    stimulus: "环保",
    correct_key: "J",
    enabled: true,
    block_intro_open: false,
    transitioning: false,
  });
  h.setTime(1100);
  h.state.handleKey("J");

  h.setTime(2000);
  h.state.configure({
    trial_id: "0:1",
    stimulus: "桌子",
    correct_key: "S",
    enabled: true,
    block_intro_open: false,
    transitioning: false,
  });
  h.setTime(2350);
  assert.deepEqual(h.state.handleKey("S"), []);
  assert.equal(h.state.snapshot().firstRtMs, 350);
  h.scheduled[1].callback();
  assert.equal(h.emitted[0].rt_ms, 350);
  assert.equal(h.emitted[0].first_key, "S");
});

test("event ids are unique", () => {
  const h = harness();
  h.state.configure({
    trial_id: "0:0",
    stimulus: "环保",
    correct_key: "J",
    enabled: true,
    block_intro_open: false,
    transitioning: false,
  });
  const first = h.state.makeControlEvent("block_start");
  const second = h.state.makeControlEvent("skip_block");
  assert.notEqual(first.event_id, second.event_id);
  assert.equal(first.key, null);
  assert.equal(second.rt_ms, null);
});
