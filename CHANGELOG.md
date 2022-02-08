# Changelog

# Version 14

### [14.10.1] [February 2, 2022]
- **[Fix]** REST API action - POST `multipart/form-data` send payload as `data`
  parameter instead of `files`.

### [14.10.0] [January 26, 2022]
- **[Add]** Add `http_response_headers` and `http_status_code` variables for
  REST API actions.
- **[Add]** Add `allow redirect` optional parameter to REST actions.
- **[Fix]** Internal: respect `print_variable` parameter.

### [14.9.1] [January 21, 2022]
- **[Add]** Session based requests (same session requests will utilize
  connection pooling, cookie sharing, etc.)
- **[Add]** Ability to specify a an environment variable `ZEUZ_NODE_CLIENT_CERT`
  which contains the location to the certificates directory or a default
  certificate directory in `ZeuZ Node > Framework > certificates` so that every
  API action will use these certificates to issue any kind of requests.

### [14.9.0] [January 21, 2022]
- **[Add]** Added **Python Expression** evaluation inside our `%||%` syntax
<br> Examples:
```%|os.name|% will return os name
%|os.environ["DB_PASS"]|% will return any env var value
%|[i.lower().strip() for i in list_var]|% its a list comprehension that will lower and strip every item in that list
%|sum([1,2,3,4])|% will return the sum of the list inside. similarly you can use any builtin fun() such as print(), len(), reversed(), min(), max()
%|list(filter(lambda x: (x % 13 == 0), my_list))|% will return a list of numbers divided by 13 
%|list(zip(list_a, list_b))|% will merge the lists into a parent list and return you a matrix
%|str(pathlib.Path("~/Desktop/file.txt").expanduser() if platform.system()=="Windows" else pathlib.Path("~/file.txt").expanduser())|% will retrun a file_path based on windows/linux/mac
```
- **[Deprecate]** Deprecated `%|random_string|%`, `%|random_number_in_range|%`, `%|pick_random_element|%`, `%|rest_response|%` variables
- **[Add]** Run-cancel will cancel the run on node
- **[Add]** Run-on-fail step has been implemented
-  **[Fix]** Browserstack bug is fixed
### [14.8.2] [December 31, 2021]
- **[Improve]** If browser is closed then teardown automatically and restart browser
- **[Improve]** Support for running apps simultaneously in same mobile

### [14.8.2] [December 31, 2021]
- **[Improve]** If browser is closed then teardown automatically and restart browser
- **[Improve]** Support for running apps simultaneously in same mobile

### [14.8.1] [December 23, 2021]
- **[Improve]** Web Drag and Drop action is combined into single action

### [14.8.0] [December 15, 2021]
- **[Add]** Windows Scroll to an Element and Swipe action are added
- **[Add]** Snapshot search and Image text search is added with parent support in Windows
- **[Add]** Added Check_uncheck action for windows
- **[Add]** Toggle pattern and selection item pattern is added into save_attribute action
- **[Add]** Added Chrome Electron App launch with required browser version
- **[Improve]** Save Attribute values is improved to scroll and extract data according to coordinates
- **[Improve]** Made time format cross-platform
- **[Improve]** direct access given number of levels in xml tree
- **[Improve]** Improved windows Launch app with maximize, setting custom size and location, wait, inspector open
- **[Improve]** Improved today variable with cross-platform feature
- **[Improve]** Server side system bug now will be handled in Node
- **[Add]** Extract Table data action is added for selenium
- **[Add]** Added multiple keystroke for selenium with + sign
- **[Fix]** WebDriver_installer fixed 

### [14.7.1] [December 6, 2021]
- **[Add]** Added appium custom swipe action and appium swipe to an element action.
- **[Change]** Autoscroll is set off by default.
### [14.7.0] [November 13, 2021]
- **[Add]** Added wait as an optional option in every action of appium and selenium. Example: (wait, optional option, 15)
- **[Add]** Also you can set a default wait from `element_wait` variable in settings.conf file
- **[Add]** Also you can change it in anywhere in a testcase with a save variable action changing `element_wait` variable
- **[Add]** Added auto_scroll_appium which will scroll automatically when an element is not found inside a scrollable page
- **[Add]** Zeuz_Snapshot app is added which will upload a snapshot in server global attachment
- **[Improve]** Improved Zeuz_Windows_Inspector with proper loop and pause
- **[Add]** Text write action is added
- **[Improve]** Upload log action is improved
- **[Change]** Settings.conf variables are changed
- **[Fix]** Appium teardown is fixed
- **[Add]** Desktop conditional if else action is added
- **[Fix]** Read Email and Delete Email actions are fixed

### [14.6.0] [October 31, 2021]
- **[Add]** Add support for specifying custom log directory. Usage:

  ```shell
  python node_cli.py -d /path/to/custom/dir
  python node_cli.py --log_dir /path/to/custom/dir
  ```
  
### [14.5.3] [October 28, 2021]
- **[Add]** size and location added into Save_attribute appium
- **[Improve]** Improved Windows inspector with parent sibling
- 
### [14.5.2] [October 19, 2021]
- **[Add]** Dictionary support is added in compare variable action

### [14.5.1] [October 18, 2021]
- **[Add]** key-value structure is added in excel_read action

### [14.5.0] [October 13, 2021]

- **[Improve]** Improved variable parsing by handling escape characters
- **[Change]** All internal APIs that communicate with Zeuz Server are now
  authenticated by API key. Only API key based login is going to work now.
- **[Add]** Desktop record and replay action! Record your mouse interactions
  with **Node > Apps > desktop-recorder > MouseModuleRecorder.py** and replay
  them with the `playback recorded events` action.
- **[Fix]** Switch Iframe and Slider bar bug is fixed
- **[Add]** Custom step duration action is added
- **[Add]** Read and save mail action is added
- **[Add]** Delete mail action is added
- **[Add]** Search and save text using regex action is added

### [14.4.0] [August 24, 2021]
- **[Fix]** Fixed variable parsing limitations
- **[Fix]** Fixed exact match bug and improved subset in compare_data action
- **[Add]**  All types of operators = ["|==|", "==", "|!=|", "|<=|", "|>=|", "|>|", "|<|", "|in|"] now can be used in For loop and While loop exit conditions. Example: 
`exit loop and continue, optional loop setting, if "start date" |in| %|row[0]|%`
- **[Add]** Added all python default methods in zeuz variable syntax. Example: 
`%|list_name.sort()|%`
`%|var_name.upper().strip().split(" ")|%`

### [14.3.1] [August 28, 2021]
- **[Add]** Parse port from database host url if specified in the form
  `127.0.0.1:8080` where the port is separated by a `:` symbol.

### [14.3.0] [August 19, 2021]
- **[Add]** Parent/Sibling/Index method added
- **[Add]** Partial and case-insensitive search added
- **[Add]** Element path method is added for searching an Element
- **[Add]** ZeuZ_Windows_Inspector.py app is added for generating path for an element
- **[Add]** Zeuz default variable "os_name" is added
- **[Add]** Wait for element to appear and disappear actions are added
- **[Add]** "Save attribute values in list" action added
- **[Fix]** All other desktop actions are fixed and improved
- **[Change]** If all actions are disabled pass the step anyway
- **[Change]** If internet goes down ZeuZ Node will now automatically handle the login when internet is up again

### [14.2.0] [July 10, 2021]
- **[Change]** Changed Report API to handle both server version

### [14.1.0] [June 29, 2021]
- **[Add]** [internal] Large sets will be uploaded in several sessions with maximum 25 testcases each

### [14.0.4] [June 20, 2021]
- **[Add]** [internal] Node_state.json is generated to communicate between nodes and node_manager

### [14.0.3] [June 20, 2021]
- **[Fix]** [internal] Node's main driver crashes/exceptions should not bubble
  up to top level.
- **[Fix]** jUnit report generation error.
- **[Add]** Add `-o`, `--once` flag for running only a single session and then
  quit node automatically. Useful for daemons, cron jobs & CI/CD.

### [14.0.0] [June 04, 2021]
- **[Change]** Changed attachment variable parsing
- **[Add]** Added file path option in execute python code action

# Version 13

### [13.7.0] [June 02, 2021] 
- **[Add]** Partial case-insensitive search for web and mobile is added as **attribute = attribute_value

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

### [13.5.1] [May 12, 2021] 
- **[Improve]** Split action improved to convert json and non json objects to string then split
### [13.5.0] [Apr 27, 2021] 
- **[Improve]** Variable parsing improved for non json type objects

### [13.4.0] [Apr 21, 2021] 
- **[Add]** Appium new powerful "Scroll to an element" action is added
- **[Fix]** Appium device, teardown and Windows terminal closing issue fixed
- **[Add]** Appium seek progress bar action added

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

### [13.1.0] [Mar 23, 2021]
- **[Add]** New improved for loop action is added with complex nested logics handling capabilities

### [13.0.0] [Jan 01, 2021]
- Implemented new well optimized ZeuZ Architecture which downloads all testcases at once before starting and upload
  report after all test cases are executed

---

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