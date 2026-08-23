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
