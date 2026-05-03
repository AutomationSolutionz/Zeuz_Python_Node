export const TIMER_MODES = Object.freeze({
  STOPWATCH: "stopwatch",
  COUNTDOWN: "countdown",
});

export const TIMER_STATUSES = Object.freeze({
  STOPPED: "stopped",
  RUNNING: "running",
  PAUSED: "paused",
});

export function clampNumber(value, min, max) {
  const number = Number.parseInt(value, 10);

  if (Number.isNaN(number)) {
    return min;
  }

  return Math.min(Math.max(number, min), max);
}

export function durationToMs(hours = 0, minutes = 0, seconds = 0) {
  const safeHours = clampNumber(hours, 0, 99);
  const safeMinutes = clampNumber(minutes, 0, 59);
  const safeSeconds = clampNumber(seconds, 0, 59);

  return ((safeHours * 60 * 60) + (safeMinutes * 60) + safeSeconds) * 1000;
}

export function formatDuration(ms) {
  const safeMs = Math.max(0, Math.floor(ms));
  const milliseconds = safeMs % 1000;
  const totalSeconds = Math.floor(safeMs / 1000);
  const seconds = totalSeconds % 60;
  const totalMinutes = Math.floor(totalSeconds / 60);
  const minutes = totalMinutes % 60;
  const hours = Math.floor(totalMinutes / 60);

  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}.${String(milliseconds).padStart(3, "0")}`;
}

export function getElapsedMs(timer, now = Date.now()) {
  if (timer.status !== TIMER_STATUSES.RUNNING || timer.startedAt === null) {
    return timer.elapsedMs;
  }

  return timer.elapsedMs + Math.max(0, now - timer.startedAt);
}

export function getDisplayMs(timer, now = Date.now()) {
  const elapsedMs = getElapsedMs(timer, now);

  if (timer.mode === TIMER_MODES.COUNTDOWN) {
    return Math.max(0, timer.targetMs - elapsedMs);
  }

  return elapsedMs;
}

export function getCountdownProgress(timer, now = Date.now()) {
  if (timer.mode !== TIMER_MODES.COUNTDOWN || timer.targetMs <= 0) {
    return 0;
  }

  return Math.min(100, (getElapsedMs(timer, now) / timer.targetMs) * 100);
}

export function createTimer({ id, label, mode, targetMs = 0, now = Date.now() }) {
  const safeMode = mode === TIMER_MODES.COUNTDOWN ? TIMER_MODES.COUNTDOWN : TIMER_MODES.STOPWATCH;
  const fallbackLabel = safeMode === TIMER_MODES.COUNTDOWN ? "Countdown timer" : "Stopwatch timer";

  return {
    id,
    label: label?.trim() || fallbackLabel,
    mode: safeMode,
    targetMs: safeMode === TIMER_MODES.COUNTDOWN ? Math.max(1000, targetMs) : 0,
    elapsedMs: 0,
    startedAt: null,
    status: TIMER_STATUSES.STOPPED,
    completed: false,
    createdAt: now,
  };
}

export function startTimer(timer, now = Date.now()) {
  if (timer.status === TIMER_STATUSES.RUNNING) {
    return timer;
  }

  return {
    ...timer,
    status: TIMER_STATUSES.RUNNING,
    startedAt: now,
    completed: false,
    elapsedMs: timer.completed && timer.mode === TIMER_MODES.COUNTDOWN ? 0 : timer.elapsedMs,
  };
}

export function pauseTimer(timer, now = Date.now()) {
  if (timer.status !== TIMER_STATUSES.RUNNING) {
    return timer;
  }

  return {
    ...timer,
    status: TIMER_STATUSES.PAUSED,
    startedAt: null,
    elapsedMs: getElapsedMs(timer, now),
  };
}

export function stopTimer(timer, now = Date.now()) {
  if (timer.status !== TIMER_STATUSES.RUNNING) {
    return {
      ...timer,
      status: TIMER_STATUSES.STOPPED,
      startedAt: null,
    };
  }

  return {
    ...timer,
    status: TIMER_STATUSES.STOPPED,
    startedAt: null,
    elapsedMs: getElapsedMs(timer, now),
  };
}

export function resetTimer(timer) {
  return {
    ...timer,
    status: TIMER_STATUSES.STOPPED,
    startedAt: null,
    elapsedMs: 0,
    completed: false,
  };
}

export function completeCountdownIfNeeded(timer, now = Date.now()) {
  if (timer.mode !== TIMER_MODES.COUNTDOWN || timer.status !== TIMER_STATUSES.RUNNING) {
    return timer;
  }

  if (getElapsedMs(timer, now) < timer.targetMs) {
    return timer;
  }

  return {
    ...timer,
    status: TIMER_STATUSES.STOPPED,
    startedAt: null,
    elapsedMs: timer.targetMs,
    completed: true,
  };
}
