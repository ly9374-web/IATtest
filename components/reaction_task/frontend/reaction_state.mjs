export const EVENT_VERSION = 1;
export const TRANSITION_MS = 300;

export class ReactionState {
  constructor({
    now = () => performance.now(),
    schedule = (callback, delay) => setTimeout(callback, delay),
  } = {}) {
    this.now = now;
    this.schedule = schedule;
    this.instanceId =
      globalThis.crypto?.randomUUID?.() ??
      `reaction-${Math.random().toString(36).slice(2)}`;
    this.sequence = 0;
    this.transitionToken = 0;
    this.trialId = null;
    this.stimulus = "";
    this.leftLabel = "";
    this.rightLabel = "";
    this.remainingCount = 0;
    this.blockTitle = "";
    this.blockInstruction = "";
    this.blockCount = 0;
    this.correctKey = "J";
    this.enabled = false;
    this.blockIntroOpen = true;
    this.externalTransitioning = false;
    this.phase = "blocked";
    this.trialStartMs = null;
    this.firstKey = null;
    this.firstCorrect = null;
    this.firstRtMs = null;
  }

  configure(args) {
    const nextTrialId = String(args.trial_id ?? "");
    const changed = nextTrialId !== this.trialId;
    const wasAccepting = this.canAccept();

    this.trialId = nextTrialId;
    this.stimulus = String(args.stimulus ?? "");
    this.leftLabel = String(args.left_label ?? "");
    this.rightLabel = String(args.right_label ?? "");
    this.remainingCount = Number(args.remaining_count ?? 0);
    this.blockTitle = String(args.block_title ?? "");
    this.blockInstruction = String(args.block_instruction ?? "");
    this.blockCount = Number(args.block_count ?? 0);
    this.correctKey = String(args.correct_key ?? "J").toUpperCase();
    this.enabled = Boolean(args.enabled);
    this.blockIntroOpen = Boolean(args.block_intro_open);
    this.externalTransitioning = Boolean(args.transitioning);

    if (changed) {
      this.resetTrial();
    } else if (
      !wasAccepting &&
      this.argsAllowInput() &&
      this.firstKey === null
    ) {
      this.phase = "ready";
      this.trialStartMs = this.now();
    } else if (!this.argsAllowInput() && this.firstKey === null) {
      this.phase = "blocked";
      this.trialStartMs = null;
    }
    return this.snapshot();
  }

  resetTrial() {
    this.transitionToken += 1;
    this.firstKey = null;
    this.firstCorrect = null;
    this.firstRtMs = null;
    if (this.argsAllowInput()) {
      this.phase = "ready";
      this.trialStartMs = this.now();
    } else {
      this.phase = "blocked";
      this.trialStartMs = null;
    }
  }

  canAccept() {
    return (
      this.argsAllowInput() &&
      (this.phase === "ready" || this.phase === "error")
    );
  }

  argsAllowInput() {
    return (
      this.enabled &&
      !this.blockIntroOpen &&
      !this.externalTransitioning
    );
  }

  handleKey(rawKey, { repeat = false } = {}) {
    const key = String(rawKey ?? "").toUpperCase();
    if (repeat || !["S", "J"].includes(key) || !this.canAccept()) {
      return [];
    }

    if (this.firstKey === null) {
      const now = this.now();
      this.firstKey = key;
      this.firstCorrect = key === this.correctKey;
      this.firstRtMs = Math.max(0, now - this.trialStartMs);
      if (this.firstCorrect) {
        this.beginCorrectTransition("first_correct");
      } else {
        this.phase = "error";
      }
      return [];
    }

    if (this.phase === "error" && key === this.correctKey) {
      this.beginCorrectTransition("correction");
    }
    return [];
  }

  beginCorrectTransition(reason) {
    this.phase = "correct";
    const token = ++this.transitionToken;
    this.schedule(() => {
      if (token !== this.transitionToken || this.phase !== "correct") return;
      this.phase = "transitioning";
      this.onEvent?.(
        this.makeEvent({
          type: "trial_complete",
          key: this.correctKey,
          isCorrect: this.firstCorrect,
          rtMs: this.firstRtMs,
          reason,
        }),
      );
      this.onStateChange?.(this.snapshot());
    }, TRANSITION_MS);
  }

  makeEvent({ type, key, isCorrect, rtMs, reason }) {
    this.sequence += 1;
    return {
      version: EVENT_VERSION,
      event_id: `${this.instanceId}:${this.trialId}:${this.sequence}`,
      type,
      trial_id: this.trialId,
      key,
      correct_key: this.correctKey,
      first_key: this.firstKey,
      is_correct: isCorrect,
      rt_ms: rtMs,
      reason,
      client_time_ms: this.now(),
    };
  }

  makeControlEvent(type) {
    this.sequence += 1;
    return {
      version: EVENT_VERSION,
      event_id: `${this.instanceId}:${this.trialId}:${this.sequence}`,
      type,
      trial_id: this.trialId,
      key: null,
      correct_key: null,
      first_key: null,
      is_correct: null,
      rt_ms: null,
      reason: type,
      client_time_ms: this.now(),
    };
  }

  snapshot() {
    return {
      phase: this.phase,
      stimulus: this.stimulus,
      leftLabel: this.leftLabel,
      rightLabel: this.rightLabel,
      remainingCount: this.remainingCount,
      blockTitle: this.blockTitle,
      blockInstruction: this.blockInstruction,
      blockCount: this.blockCount,
      elapsedMs:
        this.firstRtMs !== null
          ? this.firstRtMs
          : this.trialStartMs === null
          ? 0
          : Math.max(0, this.now() - this.trialStartMs),
      showError: this.phase === "error",
      highlightCorrect: this.phase === "correct",
      firstKey: this.firstKey,
      firstCorrect: this.firstCorrect,
      firstRtMs: this.firstRtMs,
    };
  }
}
