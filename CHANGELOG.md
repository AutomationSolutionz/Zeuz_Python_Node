# Changelog

## Version 13.7.x

### [13.7.0] [June 02, 2021] 
- **[Add]** Partial case-insensitive search for web and mobile is added as **attribute = attribute_value

## Version 13.6.x

### [13.6.4] [May 30, 2021] 
- **[Add]** Added new action for iframe switching in web
### [13.6.3] [May 27, 2021] 
- **[Fix]** Selenium "Enter text" action: on mac, `Command + a` must be used to select all text in a text field.
### [13.6.2] [May 18, 2021]
- **[Add]** "String" append to [List] is handled in "Save variable - number string list dictionary" action
### [13.6.1] [May 13, 2021]
- **[Change]** Str without first brackets are restricted to be converted into tuple
- **[Add]** New Replace string action added
### [13.6.0] [May 12, 2021] 
- **[Add]** For Loop and While Loop can now fail the step when exit condition is met. Also introduced "any" parameter

## Version 13.5.x

### [13.5.1] [May 12, 2021] 
- **[Improve]** Split action improved to convert json and non json objects to string then split
### [13.5.0] [Apr 27, 2021] 
- **[Improve]** Variable parsing improved for non json type objects

## Version 13.4.x

### [13.4.0] [Apr 21, 2021] 
- **[Add]** Appium new powerful "Scroll to an element" action is added
- **[Fix]** Appium device, teardown and Windows terminal closing issue fixed
- **[Add]** Appium seek progress bar action added

## Version 13.3.x

### [13.3.2] [Apr 15, 2021] 
- **[Remove]** Disabled `Rerun on fail` for now
### [13.3.1] [Apr 12, 2021] 
- **[Fix]** Fixed junit reporting issue where the objective was fetched from a missing key.
- **[Remove]** Removed `node_gui.py` which is redundant now and introduces buggy behavior.
### [13.3.0] [Apr 07, 2021]
- **[Add]** Added support for automating desktop web browser test cases on
mobile browsers.
- **[Fix]** Fixed a bug where node was checking if appium started up for 10
  seconds without any delay in between. This is unreliable and increases CPU
  load unnecessarily.
- **[Improve]** Improved 'For loop' to loop though selenium objects and perform 
  web actions on them

## Version 13.2.x

### [13.2.7] [Apr 07, 2021]
- **[Fix]** Bug fix of "Command separator" in run_command action
### [13.2.6] [Apr 07, 2021]
- **[Improve]** For loop improved for handling selenium elements
### [13.2.5] [Apr 06, 2021]
- **[Add]** Added a new line manually for write into text file
### [13.2.4] [Apr 05, 2021]
- **[Improve]** Run command upgraded
- **[Add]** change nth line of text document action added
### [13.2.3] [Apr 01, 2021]
- **[Fix]** Fixed the "Click and download" action issue
### [13.2.2] [Mar 30, 2021]
- **[Add]** YAML read and write action created
### [13.2.1] [Mar 29, 2021]
- **[Add]** sid and service name options were added for oracle user
### [13.2.0] [Mar 27, 2021]
- **[Add]** json report is added to zip file of report page for Performance action

## Version 13.1.x

### [13.1.0] [Mar 23, 2021]
- **[Add]** New improved for loop action is added with complex nested logics handling capabilities

## Version 13.0.x

### [13.0.0] [Jan 1, 2021]
- Implemented new well optimized ZeuZ Architecture which downloads all testcases at once before starting and upload
  report after all test cases are executed

<br><br><br><br><br>
## Version: 12.0.0

> NOTE: This is the old changelog format.

Release date: **July 16, 2020**

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
