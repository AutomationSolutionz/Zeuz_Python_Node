# ZeuZ Node Runner — Developer Guide

> This document covers everything about `Apps/node_runner/main.go`: what it does, why it exists, how it works internally, and how to build, test, and extend it.

---

## Table of Contents

1. [What Is This?](#1-what-is-this)
2. [End-User Perspective](#2-end-user-perspective)
3. [Architecture Overview](#3-architecture-overview)
4. [Versioning System](#4-versioning-system)
5. [CLI Flags Reference](#5-cli-flags-reference)
6. [Startup Flow (Step by Step)](#6-startup-flow-step-by-step)
7. [Key Design Decisions](#7-key-design-decisions)
8. [Code Walkthrough](#8-code-walkthrough)
9. [Directory Layout at Runtime](#9-directory-layout-at-runtime)
10. [Building](#10-building)
11. [Testing](#11-testing)
12. [Extending / Adding Features](#12-extending--adding-features)
13. [Known Limitations](#13-known-limitations)

---

## 1. What Is This?

`Apps/node_runner/` contains a small, self-contained **Go CLI binary** — the ZeuZ Node Runner. Users download this single binary and run it. The binary handles everything else:

- Downloads the ZeuZ Python Node source code from GitHub.
- Installs the [UV](https://github.com/astral-sh/uv) Python package manager.
- Installs all Python dependencies via `uv sync`.
- Launches `node_cli.py` (the actual test automation client).

It is intentionally a thin launcher. All real automation logic lives in the Python layer (`node_cli.py` and the `Framework/` directory). The Go binary exists purely to solve the bootstrapping problem: users should not need to install Python, pip, or any dependencies manually.

---

## 2. End-User Perspective

### First run

```
./ZeuZ_Node_linux
```

Output:
```
  ZeuZ Node v21.3.7
  Setting up ZeuZ Node...
  Fetching from: https://github.com/AutomationSolutionz/Zeuz_Python_Node/archive/refs/tags/v21.3.7.zip
  Downloading... 100%
  Extracting...
Resolved 453 packages in 1.08s
...
```

The binary downloads the matching Python source, installs all deps, and starts the node client. Subsequent runs are fast because the directory already exists.

### Everyday run (after setup)

```
./ZeuZ_Node_linux -- -k <api-key> -s https://myserver.com
```

Starts immediately — no download, just `uv sync` (fast, no-op if nothing changed) then `node_cli.py`.

### Finding out an update is available

```
  ZeuZ Node v21.3.7
╔════════════════════════════════════════════════════╗
║  Update available: v21.3.7 → v21.4.0               ║
║  Run with --update to upgrade                      ║
╚════════════════════════════════════════════════════╝
Resolved 453 packages in 1.08s
...
```

The banner appears automatically. Nothing is blocked, nothing is downloaded without the user asking.

### Upgrading

```
./ZeuZ_Node_linux --update
```

Output:
```
  ZeuZ Node v21.3.7
  Checking for updates...
  Updating v21.3.7 → v21.4.0
  Fetching from: https://github.com/.../refs/tags/v21.4.0.zip
  Downloading... 100%
  Extracting...
  Update complete (v21.4.0)
Resolved 453 packages in 1.08s
...
```

### Wiping and reinstalling from scratch

```
./ZeuZ_Node_linux --clean
```

Removes `ZeuZ_Node-v21.3.7/` and `~/.zeuz/` (drivers, downloads, artifacts), then immediately re-downloads everything.

---

## 3. Architecture Overview

```
User
  │
  ▼
ZeuZ_Node_linux  (this binary — Go)
  │
  ├─ Manages: ZeuZ_Node-v21.3.7/   (Python source — downloaded from GitHub)
  │               ├── node_cli.py
  │               ├── Framework/
  │               ├── pyproject.toml
  │               └── .venv/        (created by uv sync)
  │
  ├─ Manages: ~/.local/bin/uv       (UV package manager)
  │
  └─ Manages: ~/.zeuz/              (user artifacts: drivers, downloads)
                  ├── zeuz_node_downloads/  (chromedriver, geckodriver, jdk, etc.)
                  └── ...
```

The binary and the Python source directory live side-by-side:

```
~/Downloads/
├── ZeuZ_Node_linux          ← the binary
└── ZeuZ_Node-v21.3.7/       ← downloaded and managed by the binary
```

---

## 4. Versioning System

### Build-time version injection

The Makefile reads the version from `../../Framework/Version.txt` (e.g. `21.3.7`), prepends `v`, and injects it at compile time:

```makefile
VERSION = v$(shell grep -Eo "[0-9]+\.[0-9]+\.[0-9]+" ../../Framework/Version.txt)
LDFLAGS = -X main.version=$(VERSION)
```

This bakes `v21.3.7` into the binary. There is no version file to ship or parse at runtime.

### The `version` vs `targetVersion` split

| Variable | Type | Set by | Purpose |
|---|---|---|---|
| `version` | `string` | Linker flag at build time | The version this binary was built for. Never changed at runtime. |
| `targetVersion` | `string` | `runUpdate()` at runtime | Overrides `version` when `--update` downloads a newer release. Empty during all normal runs. |

**Rule:** All code that needs "the active version" must call `effectiveVersion()`. Never read `version` or `targetVersion` directly.

```go
func effectiveVersion() string {
    if targetVersion != "" {
        return targetVersion
    }
    return version
}
```

### Version → URL/directory mapping

| Condition | Download URL | Local directory |
|---|---|---|
| `--branch dev` | `.../refs/heads/dev.zip` | `ZeuZ_Node-dev/` |
| `version = v21.3.7` (release) | `.../refs/tags/v21.3.7.zip` | `ZeuZ_Node-v21.3.7/` |
| `version = dev` (local build) | `.../refs/heads/dev.zip` | `ZeuZ_Node-/` |
| After `--update` sets `targetVersion = v21.4.0` | `.../refs/tags/v21.4.0.zip` | `ZeuZ_Node-v21.4.0/` |

`getZeuZNodeURL()` and `getZeuZNodeDir()` implement this mapping. They must always agree — if one is modified, the other must be updated consistently.

---

## 5. CLI Flags Reference

### Important: flag separator

The binary's own flags must come **before** `--`. Everything after `--` is forwarded verbatim to `node_cli.py`.

```
./ZeuZ_Node_linux [binary-flags] -- [node_cli.py flags]
```

### Binary flags

| Flag | Type | Description |
|---|---|---|
| `--clean` | bool | Remove `ZeuZ_Node-<version>/` + `~/.zeuz/`, then re-download fresh. Use to recover a broken installation. |
| `--update` | bool | Fetch the latest tagged GitHub release, remove the current source directory, download and extract the new one. Headless-safe — no prompts. Exits 1 on failure. |
| `--branch <name>` | string | Download a specific Git branch instead of the tagged release. Useful for testing pre-release features. Incompatible with `--update`. |

### node_cli.py flags (passed after `--`)

| Short | Long | Description |
|---|---|---|
| `-s` | `--server` | Server address |
| `-k` | `--api_key` | API key |
| `-n` | `--node_id` | Custom node ID |
| `-m` | `--max_run_history` | Max run history |
| `-l` | `--logout` | Logout from server |
| `-d` | `--log_dir` | Log directory |
| `-gh` | `--gh_token` | GitHub token |
| `-spu` | `--stop_pip_auto_update` | Disable auto module updates |
| `-sbl` | `--show_browser_log` | Show browser logs |
| `-slg` | `--stop_live_log` | Stop live logging |
| `-cf` | `--chrome-fetch` | Days before fetching new Chrome (default 15) |
| `-cc` | `--chrome-cleanup` | Days before cleaning old Chrome (default 50) |
| `-gpk` | `--generate-private-key` | Generate RSA private key |
| `-apk` | `--add-private-key` | Add RSA private key |
| `-spk` | `--show-private-keys` | Show stored private keys |
| `-sh` | `--share` | Share RSA private keys |
| `-fe` | `--fetch` | Fetch shared keys |
| `-ild` | `--install-linux-deps` | Install Linux desktop automation deps |

### Examples

```bash
# Normal start
./ZeuZ_Node_linux

# Connect to a server
./ZeuZ_Node_linux -- -k 28be93cd-b708-4751-96ac-ef22e8b6d81e -s https://myserver.com

# Update to latest release
./ZeuZ_Node_linux --update

# Update then connect
./ZeuZ_Node_linux --update -- -k <api-key> -s https://myserver.com

# Wipe everything and reinstall
./ZeuZ_Node_linux --clean

# Wipe then connect
./ZeuZ_Node_linux --clean -- -k <api-key>

# Test a pre-release branch
./ZeuZ_Node_linux --branch feature-xyz
```

---

## 6. Startup Flow (Step by Step)

```
main()
  │
  1. flag.Parse()
  │   Parses --clean, --update, --branch from argv.
  │   Everything after -- becomes flag.Args() and is passed to node_cli.py.
  │
  2. Print version banner (green + bold)
  │
  3. Launch background goroutine → fetchLatestVersion() → updateCh
  │   Fires off a GitHub API call concurrently. Has a 5s timeout.
  │   The result is collected later at step 8 (non-blocking).
  │
  4. if --clean:
  │     os.RemoveAll(ZeuZ_Node-<version>/)
  │     os.RemoveAll(~/.zeuz/)
  │     print status, fall through (do NOT exit — continue to re-download)
  │
  5. if --update:
  │     fetchLatestVersion()
  │     if same version: print "Already up to date", return
  │     os.RemoveAll(old ZeuZ_Node-<version>/)
  │     targetVersion = latest                ← mutation happens here
  │     setupZeuzNode()                       ← downloads new version
  │     print "Update complete"
  │
  6. setupZeuzNode()
  │     if ZeuZ_Node-<effectiveVersion>/ exists and non-empty: return nil (no-op)
  │     otherwise: download ZIP from GitHub, extract, done
  │
  7. os.Chdir(ZeuZ_Node-<effectiveVersion>/)
  │   Re-evaluated AFTER step 5 in case targetVersion changed.
  │
  8. select { case <-updateCh: printUpdateBanner()   default: /* skip */ }
  │   Non-blocking. If check is still in flight or failed → silent.
  │   If newer version found → yellow banner, then continue.
  │
  9. updatePath() → installUV() → updatePath()
  │   Adds ~/.local/bin to PATH, installs UV if missing.
  │   Called twice: once before (find existing UV) and once after (find new UV).
  │
  10. runUVCommands(flag.Args())
        uv sync --link-mode=symlink       ← install/update Python deps
        uv run node_cli.py <user-args>    ← launch the Python client
```

### Why the goroutine is launched at step 3 (not later)

The version check is launched as early as possible so it runs concurrently with the slow parts (directory stat, potential download in `setupZeuzNode`). By the time we reach step 8, the check has usually already finished — we get the result "for free" with no added latency.

### Why `zeuzDir` is re-evaluated at step 7

`runUpdate()` may mutate `targetVersion` during step 5. After that mutation, `getZeuZNodeDir()` resolves to the new version's directory. If we used the `zeuzDir` captured before step 5, we would `chdir` into the old (now deleted) directory and crash.

---

## 7. Key Design Decisions

### Why Go, not a shell script?

- Single binary, zero runtime dependencies — users don't need bash, Python, or anything pre-installed.
- Cross-platform without OS-specific logic: the same source compiles to Windows .exe, macOS, and Linux ARM/x86.
- Go's `flag` package, `net/http`, and `archive/zip` handle everything needed without external deps.

### Why is there no interactive prompt for `--update`?

The binary is designed for **headless deployment on remote VMs**. Interactive prompts would block CI runners and unattended machines indefinitely. The update system is intentionally fire-and-forget: the banner informs, `--update` acts.

### Why does the background version check use a buffered channel?

```go
updateCh := make(chan string, 1)
```

The goroutine sends exactly one value. A buffered channel of size 1 means the send never blocks even if `main()` hits the `select`/`default` and moves on before the goroutine completes. Without the buffer, the goroutine would leak (blocked on send forever).

### Why is `downloadFile` atomic (temp file + rename)?

If the process is killed mid-download, a plain `os.Create(destPath)` would leave a partial file at `destPath`. Future runs would find it, think setup is done, and fail mysteriously. Writing to a temp file and renaming into place on success avoids this — a partial download never appears at the final path.

### Why does `unzip` strip the root directory?

GitHub archive downloads always contain a single top-level directory:

```
Zeuz_Python_Node-v21.3.7/
    node_cli.py
    Framework/
    ...
```

But we want the contents directly inside `ZeuZ_Node-v21.3.7/`. The stripping logic removes the first path component from every archive entry before extracting.

### Why is `updatePath` called twice?

```go
updatePath()   // 1st call: add ~/.local/bin so exec.LookPath finds an existing UV
installUV()    // installs UV to ~/.local/bin if not found
updatePath()   // 2nd call: ensure newly installed UV is now on PATH
```

On a machine where UV was just installed (first run), the first call adds `~/.local/bin` before the `LookPath` check. The second call is a safety net for platforms where the installer might modify PATH in a way that requires a re-read.

---

## 8. Code Walkthrough

### `effectiveVersion()`

The single source of truth for "which version are we working with right now". Always call this — never read `version` or `targetVersion` directly in business logic.

### `fetchLatestVersion()`

Calls `GET https://api.github.com/repos/AutomationSolutionz/Zeuz_Python_Node/releases/latest` with a 5-second timeout. Returns the `tag_name` field (e.g. `"v21.4.0"`). Special-cases HTTP 403 as `errRateLimited` so callers can show a specific message. All other errors are returned generically.

The `User-Agent` header is required — GitHub blocks unauthenticated requests without one.

### `runUpdate()`

The `--update` implementation. Critical ordering:

```go
oldDir := getZeuZNodeDir()   // resolves to OLD version (targetVersion still empty)
os.RemoveAll(oldDir)          // delete old directory
targetVersion = latest        // NOW mutate — from here on everything resolves to new version
setupZeuzNode()               // download + extract into NEW directory
```

If the mutation happened before `getZeuZNodeDir()`, we would delete the wrong (new) directory.

### `progressReader`

An `io.Reader` wrapper. `io.Copy` calls `Read()` in a loop; each call updates the on-screen counter with `\r` (carriage return without newline) to overwrite the same line. `io.EOF` signals the last chunk — we emit a `\n` to move the cursor down.

### `getZeuZNodeURL()` and `getZeuZNodeDir()`

Always modified together. They implement a 3-way priority:

1. `--branch` flag set → use branch (overrides everything)
2. `effectiveVersion()` is a real semver tag → use that tag
3. Otherwise → fall back to the `dev` branch

### Background update check in `main()`

```go
// Launch early, before any slow work
updateCh := make(chan string, 1)
go func() { ... updateCh <- latest }()

// ... slow setup work runs here ...

// Drain later, non-blocking
select {
case latest := <-updateCh:
    if latest != "" && latest != effectiveVersion() {
        printUpdateBanner(...)
    }
default:
    // still running or failed — no-op
}
```

The `select`/`default` pattern is the idiomatic Go way to do a non-blocking channel read. If the goroutine hasn't sent yet, `default` fires immediately and we continue.

---

## 9. Directory Layout at Runtime

```
<working-directory>/
├── ZeuZ_Node_linux              ← this binary (user placed it here)
├── ZeuZ_Node_linux_arm64        ← (optional, other arch)
└── ZeuZ_Node-v21.3.7/          ← downloaded and managed by the binary
    ├── node_cli.py              ← Python CLI entry point
    ├── Framework/               ← automation modules
    ├── pyproject.toml           ← Python project manifest (read by uv sync)
    ├── uv.lock                  ← pinned dependency versions
    └── .venv/                   ← virtualenv created by uv sync

~/.zeuz/                         ← user artifacts (never in the source dir)
├── zeuz_node_downloads/
│   ├── chromedriver/
│   ├── geckodriver/
│   ├── jdk/
│   └── android_sdk/
└── ...

~/.local/bin/
└── uv                           ← UV package manager binary
```

`--clean` removes `ZeuZ_Node-v21.3.7/` and `~/.zeuz/`. It does **not** remove the binary itself or `~/.local/bin/uv`.

---

## 10. Building

Requires: Go 1.23+, `make`, `x86_64-w64-mingw32-windres` (for Windows icon embedding).

```bash
cd Apps/node_runner

make init      # create build/ directory
make linux     # build/ZeuZ_Node_linux  +  build/ZeuZ_Node_linux_arm64
make windows   # build/ZeuZ_Node.exe   +  build/ZeuZ_Node_arm64.exe
make mac       # build/ZeuZ_Node_macos +  build/ZeuZ_Node_macos_amd64
make all       # all platforms + build/checksums.txt
make clean     # remove build/ directory
```

The version is read automatically from `../../Framework/Version.txt`. To override:

```bash
make linux VERSION=v99.0.0
```

To build a dev binary (no version injection, uses Go toolchain directly):

```bash
go build -o ZeuZ_Node_linux_dev main.go
```

---

## 11. Testing

### Setup

```bash
# Install Go if not present
sudo snap install go --classic

cd Apps/node_runner
make init && make linux
cd build
```

### Regression tests (existing features must still work)

```bash
# Normal startup
./ZeuZ_Node_linux -- --help
# Expected: green banner, then node_cli.py help output

# --clean still works
./ZeuZ_Node_linux --clean
# Expected: yellow "Removed ..." lines, green "Cleanup complete", then re-downloads

# --branch still works
./ZeuZ_Node_linux --branch dev -- --help
# Expected: downloads dev branch, runs normally

# Args pass-through still works
./ZeuZ_Node_linux -- -k fake-key -s https://example.com
# Expected: args forwarded to node_cli.py (connection error is fine, arg parsing must work)
```

### New feature tests

```bash
# --update when already up to date
./ZeuZ_Node_linux --update
# Expected: "Already up to date (v21.x.x)" in green

# --update downloads new version (simulate by removing the current dir)
rm -rf ZeuZ_Node-v21.x.x
./ZeuZ_Node_linux --update
# Expected: download progress, "Update complete"

# --update + --branch is blocked
./ZeuZ_Node_linux --update --branch dev
# Expected: "Warning: --update is not compatible with --branch", exit code 1
echo $?   # should print 1

# Dev build skips update
go build -o ZeuZ_Node_dev ../main.go   # no -ldflags, version = "dev"
./ZeuZ_Node_dev --update
# Expected: "Dev build — skipping update check"

# Download progress visible
rm -rf ZeuZ_Node-v21.x.x
./ZeuZ_Node_linux
# Expected: "\r  Downloading... 12%  ... 100%" during download
```

### Quick smoke test script

```bash
#!/bin/bash
set -e
BIN=./ZeuZ_Node_linux

echo "=== args pass-through ==="
$BIN -- --help 2>&1 | grep -q "node_cli parser" && echo "PASS" || echo "FAIL"

echo "=== --update + --branch blocked ==="
$BIN --update --branch dev 2>&1 | grep -q "not compatible" && echo "PASS" || echo "FAIL"

echo "=== exit code 1 on incompatible flags ==="
$BIN --update --branch dev 2>/dev/null; [ $? -eq 1 ] && echo "PASS" || echo "FAIL"
```

---

## 12. Extending / Adding Features

### Adding a new binary flag

1. Declare it in the `var` block alongside the existing flags:
   ```go
   myFlag = flag.Bool("my-flag", false, "Description shown in --help")
   ```
2. Handle it in `main()` after `flag.Parse()`, before `setupZeuzNode()`.
3. Document it in `UPDATE_PLAN.md` and this file.

### Adding a new node_cli.py flag

`node_cli.py` uses Python's `argparse`. Add it there — the binary automatically forwards all arguments after `--` without modification.

### Changing the GitHub repository source

Update the URL strings in `fetchLatestVersion()`, `getZeuZNodeURL()`. Both must point to the same repository.

### Adding color/terminal detection

Currently ANSI codes are emitted unconditionally. To disable them when output is piped (not a TTY):

```go
import "golang.org/x/term"

func isTerminal() bool {
    return term.IsTerminal(int(os.Stdout.Fd()))
}
```

Then gate the color constants on `isTerminal()`. This requires adding `golang.org/x/term` to `go.mod`.

### Adding a `--version` flag

```go
versionFlag = flag.Bool("version", false, "Print version and exit")
```

In `main()`:
```go
if *versionFlag {
    fmt.Println(version)
    os.Exit(0)
}
```

---

## 13. Known Limitations

### Partial download leaves broken state

If the process is killed after `os.RemoveAll(oldDir)` but before `setupZeuzNode()` finishes extracting, the installation directory is gone and the new one is incomplete. Recovery: run `--clean` or `--update` again.

### No rollback on failed `--update`

If `--update` removes the old directory then fails to download the new one (network error), the old version is gone. There is no automatic rollback. Recovery: run `--update` again (it will retry the download).

### `--clean` also removes user drivers

`~/.zeuz/` contains both user configuration and downloaded drivers (ChromeDriver, GeckoDriver, JDK, Android SDK). `--clean` removes all of it. On the next test run, all drivers will be re-downloaded automatically, but this can be time-consuming.

### Background update check may miss the banner on slow networks

The version check goroutine has a 5-second timeout. If the GitHub API is slow and `setupZeuzNode()` completes in under 5 seconds (normal case: directory already exists, so it's instant), the `select`/`default` fires before the goroutine responds and the banner is not shown. This is by design — startup must never block.

### ANSI color codes on Windows CMD

Windows Command Prompt does not support ANSI escape codes by default. The raw codes (`\033[32m`, etc.) will appear as literal characters. Windows Terminal and PowerShell 7+ do support them. A future fix: detect the terminal type and disable colors accordingly (see [Section 12](#12-extending--adding-features)).

### `--branch` + `--update` are mutually exclusive

This is enforced with an error, but the reason is worth understanding: `--branch` overrides the URL entirely, making `--update`'s version comparison meaningless (branch heads don't have semantic version tags). If you want to update a branch installation, use `--clean --branch <name>` instead.
