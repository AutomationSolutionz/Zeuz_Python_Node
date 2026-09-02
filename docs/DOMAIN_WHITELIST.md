# Domain Whitelist for Zeuz Node

Domain whitelist for organizations running Zeuz Node behind a firewall or proxy. Covers all
external network dependencies: package managers, browser downloads, driver binaries, cloud
services, and runtime APIs used by the framework and its sub-applications.

> **Source**: [Zeuz_Python_Node](https://github.com/AutomationSolutionz/Zeuz_Python_Node)
> repository analysis — `pyproject.toml`, `Apps/`, `Framework/install_handler/`, and
> runtime code in `Framework/Built_In_Automation/`.

---

## Table of Contents

- [Core Package Managers](#core-package-managers)
- [GitHub / Source Hosting](#github--source-hosting)
- [Go Module Proxy](#go-module-proxy)
- [Browser Downloads & WebDrivers](#browser-downloads--webdrivers)
- [Mobile Testing (Appium / Android / iOS)](#mobile-testing-appium--android--ios)
- [Google Cloud Platform](#google-cloud-platform)
- [Snowflake](#snowflake)
- [OCR Models (EasyOCR / PyTorch)](#ocr-models-easyocr--pytorch)
- [Temporary Email Services](#temporary-email-services)
- [Chrome Extension Downloads](#chrome-extension-downloads)
- [Security Testing Tools](#security-testing-tools)
- [mitmproxy](#mitmproxy)
- [Zeuz Server](#zeuz-server)
- [TLS / Certificate Validation](#tls--certificate-validation)
- [Consolidated List](#consolidated-list)

---

## Core Package Managers

### Python (uv / pip / PyPI)

| Domain | Purpose |
|--------|---------|
| `pypi.org` | Package index |
| `pypi.python.org` | Legacy package index |
| `files.pythonhosted.org` | Package file downloads |
| `python.org` | Python installer downloads |
| `astral.sh` | `uv` package manager website |

The `uv` binary itself is downloaded from GitHub releases (`github.com/astral-sh/uv`).

### Node.js / npm

| Domain | Purpose |
|--------|---------|
| `nodejs.org` | Node.js binary downloads (used by `nodejs_appium_installer.py`) |
| `registry.npmjs.org` | npm package registry (Appium server, AI Recorder 2 deps) |

**Note**: No Yarn domains needed. The project uses npm exclusively.

### Go Modules (node_runner)

| Domain | Purpose |
|--------|---------|
| `proxy.golang.org` | Go module proxy (default) |
| `sum.golang.org` | Go checksum database |
| `storage.googleapis.com` | Go module/binary storage |

The `Apps/node_runner/` Go app has no external dependencies currently (`go.mod` has zero
`require` directives), but Go tooling still contacts these for builds.

---

## GitHub / Source Hosting

| Domain | Purpose |
|--------|---------|
| `github.com` | Repo cloning, release downloads, `uv` binary, PyGetWindow fork, Arachni, WebDriverAgent |
| `api.github.com` | GitHub API (Arachni latest release lookup) |
| `raw.githubusercontent.com` | Raw file downloads (inspector.exe for Windows) |
| `codeload.github.com` | Archive downloads (PyGetWindow zip) |
| `objects.githubusercontent.com` | Release asset downloads |
| `github-releases.githubusercontent.com` | Release binary downloads (EasyOCR models, uv, etc.) |

Referenced repos:
- `AutomationSolutionz/PyGetWindow-0.0.5` — custom fork (zip source install)
- `AutomationSolutionz/Zeuz_Python_Node_Setup` — inspector.exe
- `AutomationSolutionz/InstallerHelperFiles` — poppler_win.zip
- `JaidedAI/EasyOCR` — OCR model weights
- `Arachni/arachni` — security scanner releases
- `appium/WebDriverAgent` — iOS WebDriver cloning
- `astral-sh/uv` — uv binary releases

---

## Browser Downloads & WebDrivers

### Selenium / WebDriver Manager

| Domain | Purpose |
|--------|---------|
| `googlechromelabs.github.io` | Chrome for Testing version JSON (last-known-good, known-good-versions) |
| `storage.googleapis.com` | ChromeDriver binary downloads |
| `edgedl.me.gvt1.com` | ChromeDriver alternative CDN |
| `msedgedriver.azureedge.net` | Edge WebDriver downloads |

WebDriver Manager also uses GitHub releases for GeckoDriver (covered by `github.com` above).

### Browser Installers (install_handler)

| Domain | Purpose |
|--------|---------|
| `go.microsoft.com` | Edge browser installer redirects |
| `download.mozilla.org` | Firefox installer downloads |

The `go.microsoft.com` URLs redirect to Microsoft CDN domains — you may also need:
- `msedge.sf.dl.delivery.mp.microsoft.com`
- `officecdn-microsoft-com.akamaized.net`

(Exact redirect targets vary by region.)

---

## Mobile Testing (Appium / Android / iOS)

### Android SDK & JDK

| Domain | Purpose |
|--------|---------|
| `dl.google.com` | Android SDK command-line tools |
| `download.oracle.com` | Oracle JDK 21 downloads |
| `api.adoptium.net` | Eclipse Temurin JDK API (alternative JDK source) |
| `github.com` | Adoptium release binary downloads (redirects to `objects.githubusercontent.com`) |

### iOS

| Domain | Purpose |
|--------|---------|
| `github.com` | WebDriverAgent cloning (`appium/WebDriverAgent`) |

### Appium Server

Appium is installed via npm — covered by `registry.npmjs.org` above. The Appium Python
client communicates only with the local Appium server instance.

---

## Google Cloud Platform

Required by `google-cloud-bigquery`, `google-cloud-bigquery-storage`, and
`google-cloud-storage` dependencies.

| Domain | Purpose |
|--------|---------|
| `storage.googleapis.com` | Cloud Storage API + general Google CDN |
| `bigquery.googleapis.com` | BigQuery API |
| `bigquerystorage.googleapis.com` | BigQuery Storage API |
| `oauth2.googleapis.com` | OAuth 2.0 token endpoint |
| `accounts.google.com` | Google account authentication |
| `www.googleapis.com` | Google API discovery + legacy endpoints |

---

## Snowflake

Required by `snowflake-connector-python`.

| Domain | Purpose |
|--------|---------|
| `*.snowflakecomputing.com` | Snowflake account endpoints |
| `ocsp.snowflakecomputing.com` | Snowflake OCSP certificate validation |

> **Recommendation**: Replace `*` with your organization's specific Snowflake account
> subdomain (e.g., `myorg.snowflakecomputing.com`) for tighter control.

---

## OCR Models (EasyOCR / PyTorch)

The bundled EasyOCR module downloads pre-trained models at runtime.

| Domain | Purpose |
|--------|---------|
| `github.com` | EasyOCR model releases (`JaidedAI/EasyOCR`) |
| `github-releases.githubusercontent.com` | Model zip file downloads |
| `download.pytorch.org` | PyTorch pre-trained ResNet weights (DBNet backbone) |

Models are downloaded on first use and cached locally in the model storage directory.

---

## Temporary Email Services

Used by the `utility.py` random/temporary email actions during test execution.

| Domain | Purpose |
|--------|---------|
| `www.1secmail.com` | 1secmail temporary email API |
| `www.developermail.com` | DeveloperMail temporary email API |

These are only needed if your test cases use the temporary email actions.

---

## Chrome Extension Downloads

Used by Selenium actions that install Chrome extensions during testing.

| Domain | Purpose |
|--------|---------|
| `clients2.google.com` | Chrome Web Store CRX download API |
| `www.crx4chrome.com` | Alternative CRX download source |

Only needed if test cases install Chrome extensions.

---

## Security Testing Tools

Used by the optional security testing module.

| Domain | Purpose |
|--------|---------|
| `api.github.com` | Arachni latest release lookup |
| `github.com` | Arachni binary download |

Nmap and Nikto are expected to be pre-installed locally (no download domains needed at
runtime). Strawberry Perl (`strawberryperl.com`) is referenced only in error messages
directing users to manual installation.

---

## mitmproxy

| Domain | Purpose |
|--------|---------|
| `snapshots.mitmproxy.org` | mitmproxy binary/snapshot downloads |

---

## Zeuz Server

Your organization's Zeuz Server instance. This is the primary runtime dependency — the node
polls it for test cases and uploads results.

| Domain | Purpose |
|--------|---------|
| `*.zeuz.ai` | Zeuz Server (replace with your org's server domain) |

> **Note**: Replace with your actual server domain. The node connects to endpoints like
> `/api/v1/`, `/create_step_report/`, `/create_report_log_api/`, etc.

---

## TLS / Certificate Validation

OCSP and CRL endpoints required for TLS certificate chain validation.

| Domain | Purpose |
|--------|---------|
| `ocsp.digicert.com` | DigiCert OCSP responder |
| `ocsp.sectigo.com` | Sectigo OCSP responder |
| `crl.sectigo.com` | Sectigo CRL distribution |
| `ocsp.pki.goog` | Google Trust Services OCSP |
| `crl.pki.goog` | Google Trust Services CRL |
| `ocsp.r2m01.amazontrust.com` | Amazon Trust OCSP (PyPI, npm) |

---

## Consolidated List

Flat list for firewall/proxy configuration. All entries are HTTPS (port 443) unless noted.

```
# ── Package Managers ──────────────────────────────────────────
pypi.org
pypi.python.org
files.pythonhosted.org
python.org
astral.sh
nodejs.org
registry.npmjs.org

# ── Go Module Proxy ──────────────────────────────────────────
proxy.golang.org
sum.golang.org

# ── GitHub ────────────────────────────────────────────────────
github.com
api.github.com
raw.githubusercontent.com
codeload.github.com
objects.githubusercontent.com
github-releases.githubusercontent.com

# ── Selenium / WebDrivers ────────────────────────────────────
googlechromelabs.github.io
storage.googleapis.com
edgedl.me.gvt1.com
msedgedriver.azureedge.net

# ── Browser Installers ───────────────────────────────────────
go.microsoft.com
download.mozilla.org

# ── Android SDK / JDK ────────────────────────────────────────
dl.google.com
download.oracle.com
api.adoptium.net

# ── Google Cloud Platform ─────────────────────────────────────
bigquery.googleapis.com
bigquerystorage.googleapis.com
oauth2.googleapis.com
accounts.google.com
www.googleapis.com

# ── Snowflake ─────────────────────────────────────────────────
*.snowflakecomputing.com

# ── OCR Models ────────────────────────────────────────────────
download.pytorch.org

# ── Temp Email (test runtime, optional) ───────────────────────
www.1secmail.com
www.developermail.com

# ── Chrome Extensions (test runtime, optional) ────────────────
clients2.google.com
www.crx4chrome.com

# ── mitmproxy ─────────────────────────────────────────────────
snapshots.mitmproxy.org

# ── Zeuz Server (replace with your domain) ────────────────────
*.zeuz.ai

# ── TLS / OCSP / CRL ─────────────────────────────────────────
ocsp.digicert.com
ocsp.sectigo.com
crl.sectigo.com
ocsp.pki.goog
crl.pki.goog
ocsp.r2m01.amazontrust.com
```

---

## Apps/ Sub-Application Analysis

| App | Type | External Dependencies |
|-----|------|----------------------|
| `Apps/Web/AI_Recorder_2/` | React (Vite + TypeScript) Chrome extension | npm packages only (antd, react, bootstrap, jquery) — all from `registry.npmjs.org` |
| `Apps/Web/aiplugin/` | Vanilla JS Chrome extension | No external downloads — static assets only |
| `Apps/node_runner/` | Go CLI (no external deps) | Zero `require` in `go.mod` — Go proxy needed only for toolchain |
| `Apps/lorust/` | Pre-built binaries | No runtime downloads — binaries are vendored |
| `Apps/desktop-recorder/` | Python script | No external downloads |
| `Apps/Authenticator/` | Utility | No external downloads |

No Electron dependency was found in any sub-application.

---

## Notes

1. **Conditional domains**: Temp email, Chrome extension, and security testing domains are
   only needed if your test cases use those features. Mark them as optional in your firewall
   rules if you want a minimal whitelist.

2. **Snowflake wildcard**: Scope `*.snowflakecomputing.com` to your specific account
   subdomain if your security policy requires it.

3. **Microsoft Edge redirects**: `go.microsoft.com` redirects through Microsoft CDN domains
   that vary by region. Monitor your proxy logs during first Edge installation to capture the
   exact CDN domains needed.

4. **PyTorch models**: `download.pytorch.org` is only needed on first EasyOCR use. Models
   are cached locally after download.

5. **Port requirements**: All domains use HTTPS (port 443). No HTTP-only (port 80)
   dependencies were found in the codebase.
