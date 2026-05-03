# ZeuZ Web Timer App

A dependency-free browser timer app for REQ-121. It supports multiple simultaneous timers, stopwatch mode, countdown mode, labels, pause/resume, stop, individual reset, reset all, and millisecond-precision displays.

## Run locally

Open `index.html` in a modern browser or serve the folder with any static file server.

```bash
python -m http.server 8080 --directory Apps/Web/Timer_App
```

Then visit `http://localhost:8080`.

## Test

```bash
node Apps/Web/Timer_App/tests/timer-core.test.mjs
```
