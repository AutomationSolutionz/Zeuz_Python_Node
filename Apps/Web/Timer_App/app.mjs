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
} from "./timer-core.mjs";

const form = document.querySelector("#timer-form");
const timerGrid = document.querySelector("#timer-grid");
const template = document.querySelector("#timer-card-template");
const modeInputs = [...document.querySelectorAll("input[name='timer-mode']")];
const countdownFields = document.querySelector("#countdown-fields");
const resetAllButton = document.querySelector("#reset-all");
const runningCount = document.querySelector("#running-count");
const totalCount = document.querySelector("#total-count");
const emptyHelper = document.querySelector("#empty-helper");
const completionToast = document.querySelector("#completion-toast");

let toastTimeout = null;

function createId() {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID();
  }

  return `timer-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

let timers = [
  createTimer({
    id: createId(),
    label: "Focus sprint",
    mode: TIMER_MODES.STOPWATCH,
    now: Date.now(),
  }),
  createTimer({
    id: createId(),
    label: "Tea break",
    mode: TIMER_MODES.COUNTDOWN,
    targetMs: durationToMs(0, 5, 0),
    now: Date.now(),
  }),
];

function getSelectedMode() {
  return modeInputs.find((input) => input.checked)?.value || TIMER_MODES.STOPWATCH;
}

function syncCountdownVisibility() {
  const isCountdown = getSelectedMode() === TIMER_MODES.COUNTDOWN;
  countdownFields.style.display = isCountdown ? "grid" : "none";
}

function showCompletionToast(label) {
  completionToast.textContent = `${label} is complete.`;
  completionToast.hidden = false;
  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    completionToast.hidden = true;
  }, 4000);
}

function updateStats() {
  runningCount.textContent = String(timers.filter((timer) => timer.status === TIMER_STATUSES.RUNNING).length);
  totalCount.textContent = String(timers.length);
  resetAllButton.disabled = timers.length === 0;
  emptyHelper.textContent = timers.length === 0
    ? "No timers yet. Create a stopwatch or countdown to begin."
    : "Start with one timer, then add more to run them at the same time.";
}

function getStatusText(timer) {
  if (timer.completed) {
    return "Countdown complete";
  }

  if (timer.status === TIMER_STATUSES.RUNNING) {
    return timer.mode === TIMER_MODES.COUNTDOWN ? "Counting down" : "Stopwatch running";
  }

  if (timer.status === TIMER_STATUSES.PAUSED) {
    return "Paused and ready to resume";
  }

  return "Stopped";
}

function getPrimaryButtonText(timer) {
  if (timer.status === TIMER_STATUSES.RUNNING) {
    return "Pause";
  }

  if (timer.status === TIMER_STATUSES.PAUSED) {
    return "Resume";
  }

  return timer.completed ? "Restart" : "Start";
}

function renderTimers(now = Date.now()) {
  timerGrid.replaceChildren();

  if (timers.length === 0) {
    const emptyState = document.createElement("p");
    emptyState.className = "empty-state";
    emptyState.textContent = "Create your first timer to see it here.";
    timerGrid.append(emptyState);
    updateStats();
    return;
  }

  timers.forEach((timer) => {
    const card = template.content.firstElementChild.cloneNode(true);
    const displayMs = getDisplayMs(timer, now);
    const progress = getCountdownProgress(timer, now);

    card.dataset.timerId = timer.id;
    card.classList.toggle("is-complete", timer.completed);
    card.querySelector(".timer-card__label").textContent = timer.label;
    card.querySelector(".timer-card__meta").textContent = timer.mode === TIMER_MODES.COUNTDOWN
      ? `Countdown · ${formatDuration(timer.targetMs)}`
      : "Stopwatch · counts up";
    card.querySelector(".timer-display").textContent = formatDuration(displayMs);
    card.querySelector(".progress-track span").style.width = timer.mode === TIMER_MODES.COUNTDOWN ? `${progress}%` : "100%";
    card.querySelector(".timer-status").textContent = getStatusText(timer);

    const primaryButton = card.querySelector(".start-pause");
    primaryButton.textContent = getPrimaryButtonText(timer);
    primaryButton.classList.toggle("is-primary", timer.status !== TIMER_STATUSES.RUNNING);

    card.querySelector(".stop-timer").disabled = timer.status !== TIMER_STATUSES.RUNNING;
    timerGrid.append(card);
  });

  updateStats();
}

function updateTimers(updater) {
  timers = timers.map(updater);
  renderTimers();
}

function addTimer(event) {
  event.preventDefault();

  const mode = getSelectedMode();
  const timer = createTimer({
    id: createId(),
    label: document.querySelector("#timer-label").value,
    mode,
    targetMs: durationToMs(
      document.querySelector("#countdown-hours").value,
      document.querySelector("#countdown-minutes").value,
      document.querySelector("#countdown-seconds").value,
    ),
  });

  timers = [timer, ...timers];
  form.reset();
  document.querySelector("input[value='stopwatch']").checked = true;
  syncCountdownVisibility();
  renderTimers();
}

function handleTimerAction(event) {
  const button = event.target.closest("button");
  const card = event.target.closest(".timer-card");

  if (!button || !card) {
    return;
  }

  const timerId = card.dataset.timerId;
  const now = Date.now();

  if (button.classList.contains("delete-timer")) {
    timers = timers.filter((timer) => timer.id !== timerId);
    renderTimers();
    return;
  }

  updateTimers((timer) => {
    if (timer.id !== timerId) {
      return timer;
    }

    if (button.classList.contains("start-pause")) {
      return timer.status === TIMER_STATUSES.RUNNING ? pauseTimer(timer, now) : startTimer(timer, now);
    }

    if (button.classList.contains("stop-timer")) {
      return stopTimer(timer, now);
    }

    if (button.classList.contains("reset-timer")) {
      return resetTimer(timer);
    }

    return timer;
  });
}

function resetAllTimers() {
  timers = timers.map(resetTimer);
  renderTimers();
}

function tick(now = Date.now()) {
  const completedLabels = [];

  timers = timers.map((timer) => {
    const nextTimer = completeCountdownIfNeeded(timer, now);

    if (nextTimer !== timer && nextTimer.completed) {
      completedLabels.push(nextTimer.label);
    }

    return nextTimer;
  });

  renderTimers(now);

  if (completedLabels.length > 0) {
    showCompletionToast(completedLabels.at(-1));
  }

  if (completedLabels.length > 0 && "Notification" in window && Notification.permission === "granted") {
    new Notification("Timer complete", { body: "A countdown timer has finished." });
  }

  requestAnimationFrame(() => tick());
}

form.addEventListener("submit", addTimer);
timerGrid.addEventListener("click", handleTimerAction);
resetAllButton.addEventListener("click", resetAllTimers);
modeInputs.forEach((input) => input.addEventListener("change", syncCountdownVisibility));

syncCountdownVisibility();
renderTimers();
requestAnimationFrame(() => tick());
