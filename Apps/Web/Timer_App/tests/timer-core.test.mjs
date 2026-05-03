import assert from "node:assert/strict";
import {
  TIMER_MODES,
  TIMER_STATUSES,
  completeCountdownIfNeeded,
  createTimer,
  durationToMs,
  formatDuration,
  getCountdownProgress,
  getDisplayMs,
  pauseTimer,
  resetTimer,
  startTimer,
  stopTimer,
} from "../timer-core.mjs";

assert.equal(formatDuration(0), "00:00:00.000");
assert.equal(formatDuration(3_723_456), "01:02:03.456");
assert.equal(durationToMs(1, 2, 3), 3_723_000);
assert.equal(durationToMs(-1, 80, "bad"), 3_540_000);

const stopwatch = createTimer({ id: "sw", label: "  ", mode: TIMER_MODES.STOPWATCH, now: 1_000 });
assert.equal(stopwatch.label, "Stopwatch timer");
assert.equal(stopwatch.status, TIMER_STATUSES.STOPPED);

const runningStopwatch = startTimer(stopwatch, 2_000);
assert.equal(runningStopwatch.status, TIMER_STATUSES.RUNNING);
assert.equal(getDisplayMs(runningStopwatch, 3_250), 1_250);

const pausedStopwatch = pauseTimer(runningStopwatch, 4_000);
assert.equal(pausedStopwatch.status, TIMER_STATUSES.PAUSED);
assert.equal(pausedStopwatch.elapsedMs, 2_000);

const stoppedStopwatch = stopTimer(startTimer(pausedStopwatch, 5_000), 6_500);
assert.equal(stoppedStopwatch.status, TIMER_STATUSES.STOPPED);
assert.equal(stoppedStopwatch.elapsedMs, 3_500);

const stoppedPausedStopwatch = stopTimer(pausedStopwatch, 7_000);
assert.equal(stoppedPausedStopwatch.status, TIMER_STATUSES.STOPPED);
assert.equal(stoppedPausedStopwatch.elapsedMs, 2_000);

const countdown = createTimer({
  id: "cd",
  label: "Launch",
  mode: TIMER_MODES.COUNTDOWN,
  targetMs: 10_000,
  now: 1_000,
});
const runningCountdown = startTimer(countdown, 2_000);
assert.equal(getDisplayMs(runningCountdown, 5_000), 7_000);
assert.equal(getCountdownProgress(runningCountdown, 7_000), 50);

const completedCountdown = completeCountdownIfNeeded(runningCountdown, 12_000);
assert.equal(completedCountdown.completed, true);
assert.equal(completedCountdown.status, TIMER_STATUSES.STOPPED);
assert.equal(completedCountdown.elapsedMs, 10_000);
assert.equal(getDisplayMs(completedCountdown, 13_000), 0);

const resetCountdown = resetTimer(completedCountdown);
assert.equal(resetCountdown.completed, false);
assert.equal(resetCountdown.elapsedMs, 0);
assert.equal(resetCountdown.status, TIMER_STATUSES.STOPPED);

console.log("timer-core tests passed");
