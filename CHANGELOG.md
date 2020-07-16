# Changelog


## Version: 12.00

Release date: **16th July, 2020**

- [NEW] Webdriver auto updater script (double click to run the script and it'll
  automatically download all the available drivers and place them in PATH properly)
- [NEW] Python module auto installer (will install missing modules automatically)
- [NEW] Zeuz CLI (Inside "Zeuz Node > Apps > zeuz-cli" folder)
  for CLI based deployment (useful in CI/CD)
- [NEW] Limit log upload to 2k (except for Warning and Errors).
  If more than 2k logs, write to local log file. (paired with server-side changes,
  we got reports of Test Automation run speed up from 8-9 hours to ~1 hours)
- [NEW] Allow re-installation of android apk
- [NEW] [ACTION] Read from excel (read from single cell, multiple cell, rows, columns)
- [NEW] [ACTION] Screenshot for Mobile (Appium)
- [NEW] [ACTION] Screenshot for Web (with full page screenshot)
- [NEW] [ACTION] "Mouse click"
- [UPD] [ACTION] Improve file download action and allow headers
- [UPD] [ACTION] Desktop Automation log improvements
- [FIX] [ACTION] "If element exists" action fix and improvements
- [FIX] [ACTION] Remove irrelevant warnings for old style loop/conditional action
- [FIX] "Upload log on fail" option not working in Node
- [FIX] Path related fixes
- [REMOVED] Detect foreground app in android
