# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Zeuz Node is a cross-platform test automation client that connects to Zeuz Server to receive and execute test cases. It supports Web (Selenium), Mobile (Appium), Desktop (PyAutoGUI), Database, REST/SOAP APIs, and Performance testing.

## Build & Development Commands

### Python (uv package manager)
```bash
uv sync                      # Install dependencies
uv run pytest tests/         # Run tests
uv run pytest tests/test_cases.py::test_name  # Run single test
uv run mypy Framework/       # Type checking
uv run ruff check Framework/ # Linting
uv run ruff format Framework/ # Format code
```

### AI Recorder Extension (React)
```bash
cd Apps/Web/AI_Recorder_2/
npm install
npm run dev    # Development
npm run build  # Production (TSC + Vite)
npm run lint   # ESLint
```

### Node Runner CLI (Go)
```bash
cd Apps/node_runner/
make all       # Build all platforms
make windows   # Windows only
make mac       # macOS only
make linux     # Linux only
```

### Running Zeuz Node
```bash
python node_cli.py --help    # Show available flags
python node_cli.py --login   # Authenticate with server
python node_cli.py --logout  # Clear credentials
```

## Architecture

### Execution Flow
```
Zeuz Server → long_poll_handler.py → adapter.py → MainDriverApi.py
                                                          ↓
                                                  sequential_actions.py
                                                          ↓
                                    ┌──────────────┬──────────────┐
                                    ↓              ↓              ↓
                              Selenium       Appium        Desktop
                          BuiltInFunctions BuiltInFunctions  ...
```

### Key Files
- `node_cli.py` - Entry point
- `Framework/MainDriverApi.py` - Test orchestration
- `Framework/Built_In_Automation/Sequential_Actions/sequential_actions.py` - Action dispatcher
- `Framework/Built_In_Automation/Shared_Resources/LocateElement.py` - Universal element location
- `Framework/Built_In_Automation/Shared_Resources/BuiltInFunctionSharedResources.py` - Shared variables
- `Framework/Utilities/CommonUtil.py` - Logging and exceptions
- `Framework/Utilities/decorators.py` - @logger, @deprecated decorators
- `Framework/Utilities/node_watchdog.py` - Restarts a node stuck inside a test case and reports that test case
- `Framework/Utilities/RequestFormatter.py` - Server session; logs in again by itself when the server drops it

### Module Structure
Each automation module follows this pattern:
```
Built_In_Automation/<Platform>/
├── BuiltInFunctions.py     # Action implementations
├── utils.py                # Platform-specific utilities
└── ...
```

Action declarations are in `Sequential_Actions/action_declarations/`:
- `info.py` - Master registry that loads all declarations
- `selenium.py`, `appium.py`, etc. - Module-specific action definitions

## Code Patterns

### Action Function Template
All actions must follow this pattern:
```python
@logger
def Action_Name(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        # 1. Parse parameters from step_data (list of 3-tuples)
        for left, mid, right in step_data:
            left = left.strip().lower()
            # Extract values...

        # 2. Get element if needed
        Element = LocateElement.Get_Element(step_data, driver)
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Element not found", 3)
            return "zeuz_failed"

        # 3. Perform action
        # ...

        CommonUtil.ExecLog(sModuleInfo, "Success", 1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
```

### Return Status Values
All actions must return one of:
- `"passed"` - Success
- `"zeuz_failed"` - Failure
- `"skipped"` - Skipped

### Step Data Format
Actions receive data as a list of 3-tuples:
```python
step_data = [
    ("id", "element parameter", "submit-btn"),
    ("use js", "optional parameter", "true"),
    ("click", "selenium action", "click"),
]
```

### Logging
```python
CommonUtil.ExecLog(sModuleInfo, "message", log_level)
# Levels: 0=Trace, 1=Info/Pass, 2=Warning, 3=Error, 4=Debug
```

### Shared Variables
```python
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr
sr.Set_Shared_Variables("key", value)
value = sr.Get_Shared_Variables("key")
sr.Test_Shared_Variables("key")  # Check if exists
```

### Variable References in Test Data
Variables use `%|variable_name|%` syntax:
```python
"%|my_var|%"           # Basic reference
"%|my_list[0]|%"       # Index access
"%|user["name"]|%"     # Dictionary access
```

### Element Location
The unified `LocateElement.Get_Element()` supports:
- Selenium WebDriver
- Appium drivers
- Auto-detects driver type from string representation

Parameter types: `element parameter`, `parent parameter`, `child parameter`, `sibling parameter`, `unique parameter`

Selector modifiers:
- `*` prefix = partial match (contains)
- `**` prefix = case-insensitive partial match
- `|*|` separator = platform-specific (Android|iOS)

## Loop Handling

Loops are handled in `sequential_actions.py` with two main mechanisms:

### For Loop (`for_loop_action()`)
Iterates through data sets or shared variable lists:
```python
# Loop settings parameter format:
("for each_item in %|MyList|%", "loop action", "action to loop")
```

**Control options** (via `optional loop control`):
- **Exit Loop and Fail** - Terminate loop and fail test case
- **Exit Loop and Continue** - Terminate loop, continue test case
- **Continue to Next Iteration** - Skip current iteration

**Data structures** track pass/fail conditions per step:
```python
exit_loop_and_fail = {"pass": [[]], "fail": [[]], "cond": []}
exit_loop_and_cont = {"pass": [[]], "fail": [[]], "cond": []}
continue_next_iter = {"pass": [[]], "fail": [[]], "cond": []}
```

### While Loop (`While_Loop_Action()`)
Conditional looping based on dataset results:
```python
# Parameters:
max_no_of_loop     # Maximum iterations (via "repeat" setting)
loop_this_data_sets # Dataset indices to loop
# Operators: |==|, !=, <=, >=, >, <, |in|
```

**Exit conditions**:
- Pass/fail condition match on specified dataset
- Operator comparison between variables
- Max iteration count reached

### Loop Parameter Types
- `loop action` - Main loop designation
- `optional loop settings` - Loop configuration
- `optional loop condition` - Conditional expressions
- `optional loop control` - Pass/fail control directives

## Reporting System

### Report Structure
Reports are stored in `CommonUtil.all_logs_json` as a hierarchical JSON:
```
all_logs_json = [{
  "run_id": "<run_id>",
  "objective": "<test_objective>",
  "execution_detail": {"duration", "teststarttime", "status"},
  "test_cases": [{
    "testcase_no": "<tc_id>",
    "title": "<tc_name>",
    "execution_detail": {"status", "duration", "failreason"},
    "steps": [{
      "step_sequence": <seq>,
      "step_id": "<id>",
      "execution_detail": {"status", "duration", "stepstarttime", "stependtime"},
      "log": [{"status", "modulename", "details", "tstamp", "loglevel"}]
    }]
  }]
}]
```

### Key Reporting Functions

**`CommonUtil.CreateJsonReport()`** - Builds JSON report structure dynamically
- Extracts log_id components: `run_id|testcase_no|step_id|step_no`
- Updates test case and step entries in `all_logs_json`
- Appends log entries to step logs

**`MainDriverApi.upload_step_report()`** - Uploads individual step results
- POST to `/create_step_report/`
- 5 retry attempts with 4-second delays

**`MainDriverApi.upload_reports_and_zips()`** - Uploads complete report + artifacts
- POST to `/create_report_log_api/` (execution report)
- POST to `/save_log_and_attachment_api/` (ZIP files)
- Failed uploads saved to `failed_uploads/<run_id>/` for retry

### Test Case Result Calculation
`calculate_test_case_result()` aggregates step results (priority order):
1. `testcase_exit` flag if set
2. "BLOCKED" → Blocked
3. "CANCELLED" → Cancelled
4. "zeuz_failed" → Failed or Blocked (based on verify_point)
5. "WARNING" or "NOT RUN" → Failed
6. All "SKIPPED" → Skipped
7. "PASSED" → Passed
8. Default → Unknown

### Artifact Directory Structure
```
<run_id>/<session_name>/<test_case>/
├── Log/                    # Browser console error logs
├── screenshots/            # Test screenshots
├── performance_report/     # Performance metrics
├── json_report/           # Step-level JSON reports
├── zeuz_download_folder/  # Downloaded files
└── attachments/           # Test case attachments
```

### JUnit Report
Generated via `reporting/junit_report.py` after test completion:
- Output: `<zip_dir>/junitreport.xml`
- Standard JUnit XML format with test suite and test case elements

## Node Watchdog

`action_timeout` only covers actions. `Framework/Utilities/node_watchdog.py` covers
everything else: it runs on its own thread and expects signs of progress while a
test case is running (every `CommonUtil.ExecLog` call is one).

- No progress for 20 minutes (or `action_timeout` + 5 minutes inside an action,
  whichever is longer) means the test case is stuck. The watchdog writes every
  thread's stack to `AutomationLog/watchdog/stall_*.txt` and the node restarts
  itself in place (`node_cli.on_test_case_stuck`). No restart in debug sessions
  or on Windows; the dump is still written.
- `AutomationLog/interrupted_test_case.json` names the test case that is running,
  with its last activity, refreshed every minute. If it is still there when the
  node starts (watchdog restart, `kill -9`, reboot), or a delivered test case
  ends without a result, `node_cli.report_interrupted_test_case` reports it to the
  server as Blocked with the reason, so its run can complete.
- Work that is legitimately silent for long must say so:
  `with node_watchdog.allow_quiet("what", seconds):` (`None` = no limit). Actions,
  report/log uploads and performance runs already do.
- `ZEUZ_NODE_WATCHDOG_SECONDS` changes the 20 minutes; `0` turns the watchdog off.
- On Linux, if the interpreter itself is frozen for 15 minutes (not even the
  watchdog thread runs), the process dumps its stacks to
  `AutomationLog/watchdog/interpreter_frozen.txt` and exits, so whatever
  supervises the node can start it again.

## Server Session

The node logs in once with its API key and then holds a cookie session that it
renews before the access token expires (`Framework/Utilities/RequestFormatter.py`).
The server keeps those sessions in Redis, so a server upgrade or a Redis flush
drops every node's session at once.

- Every request goes through `_send`: on a 401 it calls `relogin()` (login with
  the API key) and sends the request once more, with any uploaded files rewound.
  A failed renew (400/401/403) also falls back to `relogin()`.
- `relogin()` is thread-safe (one login for many threads that hit 401 together)
  and tries at most once per `RELOGIN_MIN_INTERVAL_SECONDS` (30), so a revoked API
  key, or an endpoint that answers 401 for another reason, cannot turn into a
  login on every request.
- Before this, a node whose session was lost answered every poll with
  `[deploy] Request Error, status code: 401 | reconnecting` forever and had to be
  restarted by hand. `node_cli.Login` also returned right after logging in when
  `session.bin` held a stale session, so a restarted node never started polling.
- Tests: `tests/test_request_relogin.py` runs the real module against a local
  server that behaves like zsvc (login, renew, a flush that forgets sessions).

## Adding New Modules

1. Create `Framework/Built_In_Automation/<Category>/<Module>/BuiltInFunctions.py`
2. Add action declarations in `Sequential_Actions/action_declarations/<module>.py`
3. Register in `action_declarations/info.py`
4. Add module loading in `sequential_actions.py:load_sa_modules()`

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for complete guide.

## Local Server

FastAPI server runs on port 18100+ (auto-increments if in use):
- `/api/v1/status` - Health check
- `/api/v1/connect` - Connection management
- `/api/v1/mobile` - Mobile UI dump

## Key Directories

- `~/.zeuz/` - User artifacts
- `~/.zeuz/zeuz_node_downloads/` - Driver/app downloads
- `AutomationLog/` - Test execution logs
- `AutomationLog/attachments/` - Captured files
