# Playwright action compatibility

Set the runtime shared variable `zeuz_browser_driver` to `playwright` to run existing `selenium action` rows with Playwright, or use `playwright action` directly. Without that value, Selenium routing is unchanged. `open electron app` and `accessibility test` remain Selenium-owned.

## Supported actions

The Playwright declaration set contains exactly these 55 Selenium-compatible actions:

`click`, `click and download`, `right click`, `double click`, `hover`, `keystroke keys`, `keystroke chars`, `text`, `validate full text`, `validate partial text`, `deselect all`, `select by visible text`, `deselect by visible text`, `select by value`, `deselect by value`, `select by index`, `deselect by index`, `open browser`, `open electron app`, `go to link`, `go to link v2`, `tear down browser`, `switch browser`, `get current url`, `navigate`, `handle alert`, `teardown`, `open new tab`, `close tab`, `upload file`, `drag and drop`, `get element info`, `scroll`, `scroll to element`, `scroll element to top`, `scroll to top`, `switch window`, `switch window or frame`, `switch window/tab`, `switch iframe`, `save attribute`, `save attribute values in list`, `extract table data`, `save web elements in list`, `take screenshot web`, `execute javascript`, `check uncheck all`, `check uncheck`, `multiple check uncheck`, `slider bar`, `resize window`, `change attribute value`, `capture network log`, `if element exists`, and `copy image into browser`.

Action values and supplemental rows retain their Selenium meanings. Common examples are `driver id`, `resolution`, `wait for element`, `wait time to page load`, `offset`, `use js`, `ignore case`, `variable`, `fullscreen`, `tab title`, `tab index`, `row`, `column`, `pixels`, `wait for download`, and `folder path`. Files, downloads, screenshots, saved elements, extracted values, URLs, dialog text, and network logs use the existing shared-variable contracts.

## Locator grammar

Locators accept exact attributes and text (`id`, `name`, `text`), partial matches (`*id`, `*text`), case-insensitive partial matches (`**id`, `**text`), `tag`, raw `css`/`css selector`, raw `xpath`, and positive or negative `index` rows. The relationship subfields are `parent parameter`, `child parameter`, `sibling parameter`, `preceding parameter`, and `following parameter`, including their numbered forms.

`wait`, `allow hidden`, `allow disable`, and `text filter` are optional rows. `save parameter` stores a locator; `get parameter` retrieves one. Locator roots may be saved elements, frames, nested elements, and open shadow roots using numbered `sr ... parameter` rows. Closed shadow roots are not accessible.

## Browser launch mapping

| ZeuZ browser | Playwright engine |
|---|---|
| Chrome / ChromeHeadless | Chromium, `channel="chrome"` |
| Microsoft Edge Chromium / EdgeChromiumHeadless | Chromium, `channel="msedge"` |
| FireFox / FirefoxHeadless | Bundled Firefox |
| Safari | Bundled WebKit |

Launch rows support raw browser arguments, page-load strategy, resolution/viewport, proxy, locale, user agent, permissions, HTTPS error handling, Firefox preferences, download behavior, and Chromium `debugger address` CDP attachment. Opera fails explicitly.

The viewport uses runtime `window_size_x` and `window_size_y` when both are set, otherwise it defaults to 1920×1080 to match Selenium's maximized/headless node behavior. An explicit `resolution` row takes precedence.

Unknown Selenium capabilities, Chrome version pinning, experimental options, and extension sideloading on branded Chrome/Edge are logged and ignored because they do not have a safe equivalent. The installer exposes bundled Firefox and WebKit; branded Chrome and Edge continue through their existing installers.

## Execute Python compatibility

Playwright-launched Chrome and Edge expose a Selenium CDP bridge as the existing `selenium_driver` shared/global variable. Existing `execute python code` rows such as `selenium_driver.execute_script(...)` therefore control the same browser without test-data changes. The bridge is selected with its Playwright driver ID and detached during Playwright teardown; it does not own or close the browser.

This bridge is unavailable for Firefox and WebKit because Selenium's debugger attachment is Chromium-only. Commands that ChromeDriver itself does not support for debugger-attached sessions remain unsupported.

## Network capture: Firefox/WebKit memory retention and OOM

**Known limitation:** long-running Firefox or WebKit (Safari) sessions that use
`capture network log` can retain network objects between tests, particularly with
`zeuz_auto_teardown=False` and `include response body=true`. The Chromium capture
fix does not eliminate this risk in Firefox/WebKit.

### Symptoms and cause

Watch for Python/Playwright-driver memory growing across tests, eventual
out-of-memory (OOM) kills, or a run abruptly stopping without a Python traceback.
On Linux, an OOM-related systemd scope shutdown can also remove the tmux pane or
session even though the VM never rebooted. These symptoms alone do not prove
network retention; inspect kernel logs for `Out of memory`, `Killed process`, and
the system journal for `oom-kill`. The process chosen for the kill is not
necessarily the only large memory consumer.

Playwright's event-based network API creates live `Request`/`Response` objects
that can remain referenced inside its connection/dispatcher registries. Reading
response bodies can additionally cache data in the Playwright driver. Clearing
ZeuZ's `state["network"]`, deleting the saved output variable, or calling Python
`gc.collect()` does not release objects still referenced by Playwright. Removing
listeners stops future reporting but does not dispose of previously reported
objects. Reloading the page is not equivalent to closing it.

The original retention was reproduced on Chromium with Playwright **1.62.0**;
the Firefox/WebKit fallback retains the same kind of event-based capture. A
Firefox/WebKit OOM was **not separately reproduced** during that investigation.
Recheck retention behavior when changing Playwright versions. See Playwright's
[request-history lifetime documentation](https://playwright.dev/python/docs/api/class-page#page-requests).

### Current implementation and safe mitigations

- **Chrome/Edge/Chromium:** capture uses a temporary CDP session through
  Playwright's `context.new_cdp_session()`. It collects plain network details and
  retrieves bodies without creating Playwright request/response history. Stop
  disables tracking and detaches the session. This does not use Selenium to
  capture traffic and does not close the browser or clear login state.
- **Firefox/WebKit:** CDP is unavailable. Capture therefore uses native
  Playwright response events, subscribed only between start and stop. Test-end
  cleanup also removes unfinished captures, including after failures, regardless
  of `zeuz_auto_teardown`. This limits capture lifetime, but does not guarantee
  release of the internal request/response history.
- If session reuse is unnecessary, use `zeuz_auto_teardown=on`. Otherwise, close
  and recreate the page/context or explicitly tear down the browser at suitable
  test boundaries, accounting for lost page state and any required login.
  Avoid capturing traffic or response bodies that the tests do not need.
- More RAM/swap provides headroom, not a retention fix. Do not substitute
  `page.requests()` for complete capture without changing the action contract:
  its bounded recent-request history can omit earlier requests from a test.

### Where to investigate

In [Playwright/BuiltInFunctions.py](../Framework/Built_In_Automation/Web/Playwright/BuiltInFunctions.py),
start with `_capture_network_page` (Firefox/WebKit fallback),
`_capture_network_target` (Chromium CDP), `capture_network_log`, and
`_stop_network_capture`. `cleanup_network_captures` is called on the action worker
from the `run_test_case` finalizer in [MainDriverApi.py](../Framework/MainDriverApi.py).

The regression test
`test_cdp_capture_reuses_browser_without_retaining_network_objects` in
[test_playwright_compat.py](../tests/test_playwright_compat.py) checks repeated
Chromium captures, iframe traffic, retained object counts, and preserved session
state. It is not a Firefox/WebKit memory regression test. For those engines,
compare repeated captures on one long-lived page with page/context teardown;
check object retention as well as RSS, since freeing objects need not immediately
return allocated memory to the OS.
