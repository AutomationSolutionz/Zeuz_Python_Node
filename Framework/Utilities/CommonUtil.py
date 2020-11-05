# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

import sys
import inspect
import os, os.path, threading
import ast
import json
import logging
from Framework.Utilities import ConfigModule
import datetime
from Framework.Utilities import FileUtilities as FL
import uuid
from Framework.Utilities import RequestFormatter
import subprocess
from pathlib import Path


# For TakeScreenShot()
from concurrent.futures import ThreadPoolExecutor
from PIL import Image  # Picture quality

try:
    from PIL import ImageGrab as ImageGrab_Mac_Win  # Screen capture for Mac and Windows
except:
    pass
try:
    import pyscreenshot as ImageGrab_Linux  # Screen capture for Linux/Unix
except:
    pass

# Import colorama for console color support
from colorama import init as colorama_init
from colorama import Fore, Back

# Initialize colorama for the current platform
colorama_init(autoreset=True)

MODULE_NAME = inspect.getmodulename(__file__)

# Get file path for temporary config file
# temp_config = os.path.join(os.path.join(FL.get_home_folder(), os.path.join('Desktop', os.path.join('AutomationLog',ConfigModule.get_config_value('Advanced Options','_file')))))


# temp_config = os.path.join(os.path.join (os.path.realpath(__file__).split("Framework")[0] , os.path.join ('AutomationLog',ConfigModule.get_config_value('Advanced Options', '_file'))))
temp_config = Path(
    os.path.join(os.path.abspath(__file__).split("Framework")[0])
    / Path("AutomationLog")
    / Path(
        ConfigModule.get_config_value(
            "Advanced Options",
            "_file",
            Path(os.path.abspath(__file__)).parent.parent / Path("settings.conf"),
        )
    )
)


passed_tag_list = [
    "Pass",
    "pass",
    "PASS",
    "PASSED",
    "Passed",
    "passed",
    "true",
    "TRUE",
    "True",
    "1",
    "Success",
    "success",
    "SUCCESS",
    True,
]
failed_tag_list = [
    "Fail",
    "fail",
    "FAIL",
    "Failed",
    "failed",
    "FAILED",
    "false",
    "False",
    "FALSE",
    "0",
    False,
]
skipped_tag_list = ["skip", "SKIP", "Skip", "skipped", "SKIPPED", "Skipped"]

all_logs = {}
all_logs_count = 0
all_logs_list = []
load_testing = False

# Holds the previously logged message (used for prevention of duplicate logs simultaneously)
previous_log_line = None


def to_unicode(obj, encoding="utf-8"):
    if isinstance(obj, str):
        if not isinstance(obj, str):
            obj = str(obj, encoding)
        return obj


def parse_value_into_object(val):
    """Parses the given value into a Python object: int, str, list, dict."""

    if not isinstance(val, str):
        return val

    try:
        val = ast.literal_eval(val)
    except:
        try:
            val = json.loads(val)
        except:
            try:
                val = ast.literal_eval(f'"{val}"')
            except:
                pass

    return val


def prettify(key, val):
    """Tries to pretty print the given value."""

    color = Fore.MAGENTA

    try:
        if type(val) == str:
            val = parse_value_into_object(val)

        print(color + "%s = %s" % (key, json.dumps(val, indent=2, sort_keys=True)))
    except:
        return print(color + "%s = %s" % (key, val))


def Add_Folder_To_Current_Test_Case_Log(src):
    try:
        # get the current test case locations
        dest_folder = ConfigModule.get_config_value(
            "sectionOne", "test_case_folder", temp_config
        )
        folder_name = [x for x in src.split("/") if x != ""][-1]
        if folder_name:
            des_path = os.path.join(dest_folder, folder_name)
            FL.copy_folder(src, des_path)
            return True
        else:
            return False

    except Exception as e:
        return Exception_Handler(sys.exc_info())


def Add_File_To_Current_Test_Case_Log(src):
    try:
        # get the current test case locations
        dest_folder = ConfigModule.get_config_value(
            "sectionOne", "test_case_folder", temp_config
        )
        file_name = [x for x in src.split("/") if x != ""][-1]
        if file_name:
            des_path = os.path.join(dest_folder, file_name)
            FL.copy_file(src, des_path)
            return True
        else:
            return False

    except Exception as e:
        return Exception_Handler(sys.exc_info())


def Exception_Handler(exec_info, temp_q=None, UserMessage=None):
    try:
        sModuleInfo_Local = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        exc_type, exc_obj, exc_tb = exec_info
        Error_Type = (
            (str(exc_type).replace("type ", ""))
            .replace("<", "")
            .replace(">", "")
            .replace(";", ":")
        )
        Error_Message = str(exc_obj)
        File_Name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Function_Name = os.path.split(exc_tb.tb_frame.f_code.co_name)[1]
        Line_Number = str(exc_tb.tb_lineno)
        Error_Detail = (
            "Error Type ~ %s: Error Message ~ %s: File Name ~ %s: Function Name ~ %s: Line ~ %s"
            % (Error_Type, Error_Message, File_Name, Function_Name, Line_Number)
        )
        sModuleInfo = Function_Name + ":" + File_Name
        ExecLog(sModuleInfo, "Following exception occurred: %s" % (Error_Detail), 3)
        TakeScreenShot(Function_Name + "~" + File_Name)
        if UserMessage != None:
            ExecLog(
                sModuleInfo, "Following error message is custom: %s" % (UserMessage), 3
            )
        if temp_q != None:
            temp_q.put("failed")

        return "failed"

    except Exception:
        exc_type_local, exc_obj_local, exc_tb_local = sys.exc_info()
        fname_local = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail_Local = (
            (str(exc_type_local).replace("type ", "Error Type: "))
            + ";"
            + "Error Message: "
            + str(exc_obj_local)
            + ";"
            + "File Name: "
            + fname_local
            + ";"
            + "Line: "
            + str(exc_tb_local.tb_lineno)
        )
        ExecLog(
            sModuleInfo_Local,
            "Following exception occurred: %s" % (Error_Detail_Local),
            3,
        )
        return "failed"


def Result_Analyzer(sTestStepReturnStatus, temp_q):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        if sTestStepReturnStatus in passed_tag_list:
            temp_q.put("passed")
            return "passed"
        elif sTestStepReturnStatus in failed_tag_list:
            temp_q.put("failed")
            return "failed"
        elif sTestStepReturnStatus in skipped_tag_list:
            temp_q.put("skipped")
            return "skipped"
        elif (
            sTestStepReturnStatus.lower() == "cancelled"
        ):  # Special use to stop a scheduled run without failing it
            temp_q.put("cancelled")
            return "cancelled"
        else:
            ExecLog(
                sModuleInfo,
                "Step return type unknown: %s. The last function did not return a valid type (passed/failed/etc)"
                % (sTestStepReturnStatus),
                3,
            )
            temp_q.put("failed")
            return "failed"

    except Exception as e:
        return Exception_Handler(sys.exc_info())


def ExecLog(
    sModuleInfo, sDetails, iLogLevel=1, _local_run="", sStatus="", force_write=False, variable=None
):
    # Do not log anything if load testing is going on and we're not forced to write logs
    if load_testing and not force_write:
        return

    # Read from settings file
    debug_mode = ConfigModule.get_config_value("RunDefinition", "debug_mode")

    # ";" is not supported for logging.  So replacing them
    sDetails = sDetails.replace(";", ":").replace("%22", "'")

    # Terminal output color
    line_color = ""

    # Convert logLevel from int to string for clarity
    if iLogLevel == 0:
        if debug_mode.lower() == "true":
            status = (
                "Debug"  # This is not displayed on the server log, just in the console
            )
        else:  # Do not display this log line anywhere
            return
    elif iLogLevel == 1:
        status = "Passed"
        line_color = Fore.GREEN
    elif iLogLevel == 2:
        status = "Warning"
        line_color = Fore.YELLOW
    elif iLogLevel == 3:
        status = "Error"
        line_color = Fore.RED
    elif iLogLevel == 4:
        status = "Console"
    elif iLogLevel == 5:
        status = "Info"
        iLogLevel = 1
        line_color = Fore.CYAN
    elif iLogLevel == 6:
        status = "BrowserConsole"
    else:
        print("*** Unknown log level - Set to Info ***")
        status = "Info"
        iLogLevel = 5
        line_color = Fore.CYAN

    if not sModuleInfo:
        sModuleInfo = ""
        info = ""
    else:
        info = f"{sModuleInfo}\t\n"

    # Display on console
    # Change the format for console, mainly leave out the status level
    if "saved variable" not in sDetails.lower():
        if status == "Console":
            msg = f"{info}{sDetails}" if sModuleInfo else sDetails
            print(line_color + msg)
        else:
            print(line_color + f"{status.upper()} - {info}{sDetails}")

    current_log_line = f"{status.upper()} - {sModuleInfo} - {sDetails}"

    global previous_log_line
    # Skip duplicate logs
    if previous_log_line and previous_log_line.strip() == current_log_line.strip():
        return

    # Set current log as the next previous log
    previous_log_line = current_log_line

    if iLogLevel > 0:
        if iLogLevel == 6:
            FWLogFolder = ConfigModule.get_config_value(
                "sectionOne", "log_folder", temp_config
            )
            if os.path.exists(FWLogFolder) == False:
                FL.CreateFolder(FWLogFolder)  # Create log directory if missing

            if FWLogFolder == "":
                BrowserConsoleLogFile = (
                    ConfigModule.get_config_value(
                        "sectionOne", "temp_run_file_path", temp_config
                    )
                    + os.sep
                    + "BrowserLog.log"
                )
            else:
                BrowserConsoleLogFile = FWLogFolder + os.sep + "BrowserLog.log"

            logger = logging.getLogger(__name__)

            browser_log_handler = None
            if os.name == "posix":
                try:
                    browser_log_handler = logging.FileHandler(BrowserConsoleLogFile)
                except:
                    pass
            elif os.name == "nt":
                browser_log_handler = logging.FileHandler(BrowserConsoleLogFile)

            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

            if browser_log_handler:
                browser_log_handler.setFormatter(formatter)
                logger.addHandler(browser_log_handler)
                logger.setLevel(logging.DEBUG)
                logger.info(sModuleInfo + " - " + sDetails + "" + sStatus)
                logger.removeHandler(browser_log_handler)
        else:
            # Except the browser logs
            global all_logs, all_logs_count, all_logs_list

            log_id = ConfigModule.get_config_value(
                "sectionOne", "sTestStepExecLogId", temp_config
            )

            if not log_id:
                return

            if variable:
                sDetails = "%s\nVariable value: %s" % (sDetails, variable["val"])

            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            all_logs[all_logs_count] = {
                "logid": log_id,
                "modulename": sModuleInfo,
                "details": sDetails,
                "status": status,
                "loglevel": iLogLevel,
                "tstamp": str(now),
            }
            if len(all_logs_list) >= 1:
                # start logging to the log file instead of logging to the server
                try:
                    # filepath = Path(ConfigModule.get_config_value('sectionOne', 'log_folder', temp_config)) / 'execution.log'
                    filepath = (
                        Path(
                            ConfigModule.get_config_value(
                                "sectionOne", "temp_run_file_path", temp_config
                            )
                        )
                        / "execution.log"
                    )
                    with open(filepath, "a+") as f:
                        print("[%s] %s" % (now, current_log_line), file=f)
                except FileNotFoundError:
                    pass

            # log warnings and errors
            if iLogLevel in (2, 3) or len(all_logs_list) < 1:
                # log to server in case of logs less than 2k
                all_logs_count += 1
                if all_logs_count > 2000:
                    all_logs_list.append(all_logs)
                    all_logs_count = 0
                    all_logs = {}


def FormatSeconds(sec):
    hours, remainder = divmod(sec, 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_formatted = "%d:%02d:%02d" % (hours, minutes, seconds)
    return duration_formatted


def get_all_logs():
    global all_logs_list, all_logs, all_logs_count

    if all_logs_count > 0:
        all_logs_list.append(all_logs)

    return all_logs_list


def clear_all_logs():
    global all_logs, all_logs_count, all_logs_list
    all_logs = {}
    all_logs_count = 0
    all_logs_list = []
    return True


def PhysicalAvailableMemory():
    try:
        import psutil
        return (int(str(psutil.virtual_memory().available))) / (1024 * 1024)

    except Exception as e:
        return 1


screen_capture_driver, screen_capture_type = (
    None,
    "none",
)  # Initialize global variables for TakeScreenShot()


def set_screenshot_vars(shared_variables):
    """ Save screen capture type and selenium/appium driver objects as global variables, so TakeScreenShot() can access them """
    # We can't import Shared Variables due to cyclic imports causing local runs to break, so this is the work around
    # Known issue: This function is called by Sequential_Actions(). Thus, Maindriver can't take screenshots until this is set
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    global screen_capture_driver, screen_capture_type

    try:
        if "screen_capture" in shared_variables:  # Type of screenshot (desktop/mobile)
            screen_capture_type = shared_variables["screen_capture"]
        if screen_capture_type == "mobile":  # Appium driver object
            if "device_id" in shared_variables:
                device_id = shared_variables[
                    "device_id"
                ]  # Name of currently selected mobile device
                appium_details = shared_variables[
                    "appium_details"
                ]  # All device details
                screen_capture_driver = appium_details[device_id][
                    "driver"
                ]  # Driver for selected device
        if screen_capture_type == "web":  # Selenium driver object
            if "selenium_driver" in shared_variables:
                screen_capture_driver = shared_variables["selenium_driver"]
    except:
        ExecLog(sModuleInfo, "Error setting screenshot variables", 3)


def TakeScreenShot(ImageName, local_run=False):
    """ Puts TakeScreenShot into a thread, so it doesn't block test case execution """

    try:
        t = threading.Thread(
            target=Thread_ScreenShot, args=(ImageName, local_run)
        )  # Create thread object
        t.daemon = True  # Run in background
        t.start()  # Start thread
    except:
        return Exception_Handler(sys.exc_info())


def Thread_ScreenShot(ImageName, local_run=False):
    """ Capture screen of mobile or desktop """
    # Do not include extension in ImageName, it will be added

    # Define variables
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    ExecLog(sModuleInfo, "Function start", 0)
    chars_to_remove = [
        "?",
        "*",
        '"',
        "<",
        ">",
        "|",
        "\\",
        "\/",
        ":",
    ]  # Symbols that can't be used in filename
    picture_quality = 20  # Quality of picture
    picture_size = 800, 600  # Size of image (for reduction in file size)

    # Read values from config file
    take_screenshot_settings = ConfigModule.get_config_value(
        "RunDefinition", "take_screenshot"
    )  # True/False to take screenshot from settings.conf
    local_run = ConfigModule.get_config_value(
        "RunDefinition", "local_run"
    )  # True/False to run only locally, in which case we do not take screenshot from settings.conf
    image_folder = ConfigModule.get_config_value(
        "sectionOne", "screen_capture_folder", temp_config
    )  # Get screen capture directory from temporary config file that is dynamically created
    if not os.path.exists(image_folder):
        os.mkdir(image_folder)

    # Decide if screenshot should be captured
    if (
        take_screenshot_settings.lower() == "false"
        or local_run.lower() == "true"
        or screen_capture_type == "none"
        or screen_capture_type == None
    ):
        ExecLog(
            sModuleInfo, "Skipping screenshot due to screenshot or local_run setting", 0
        )
        return
    print(
        "************* ImageName ****************: {}, type: {}".format(
            ImageName, type(ImageName)
        )
    )
    # Adjust filename and create full path (remove invalid characters, convert spaces to underscore, remove leading and trailing spaces)
    trans_table = str.maketrans(
        dict.fromkeys("".join(chars_to_remove))
    )  # python3 version of translate
    ImageName = os.path.join(
        image_folder,
        TimeStamp("utc")
        + "_"
        + (ImageName.translate(trans_table)).strip().replace(" ", "_")
        + ".png",
    )
    ExecLog(
        sModuleInfo,
        "Capturing screen on %s, with driver: %s, and saving to %s"
        % (str(screen_capture_type), str(screen_capture_driver), ImageName),
        0,
    )

    try:
        # Capture screenshot of desktop
        if screen_capture_type == "desktop":
            if sys.platform == "linux2":
                image = ImageGrab_Linux.grab()
                image.save(ImageName, format="PNG")  # Save to disk
            elif sys.platform == "win32" or sys.platform == "darwin":
                image = ImageGrab_Mac_Win.grab()
                image.save(ImageName, format="PNG")  # Save to disk

        # Exit if we don't have a driver yet (happens when Test Step is set to mobile/web, but we haven't setup the driver)
        elif screen_capture_driver == None and (
            screen_capture_type == "mobile" or screen_capture_type == "web"
        ):
            ExecLog(
                sModuleInfo,
                "Can't capture screen, driver not available for type: %s, or invalid driver: %s"
                % (str(screen_capture_type), str(screen_capture_driver)),
                1,
            )
            return

        # Capture screenshot of web browser
        elif screen_capture_type == "web":
            screen_capture_driver.get_screenshot_as_file(
                ImageName
            )  # Must be .png, otherwise an exception occurs

        # Capture screenshot of mobile
        elif screen_capture_type == "mobile":
            screen_capture_driver.save_screenshot(
                ImageName
            )  # Must be .png, otherwise an exception occurs
        else:
            ExecLog(
                sModuleInfo,
                "Unknown capture type: %s, or invalid driver: %s"
                % (str(screen_capture_type), str(screen_capture_driver)),
                3,
            )

        # Lower the picture quality
        if os.path.exists(ImageName):  # Make sure image was saved
            image = Image.open(ImageName)  # Re-open in standard format
            image.thumbnail(
                picture_size, Image.ANTIALIAS
            )  # Resize picture to lower file size
            image.save(
                ImageName, format="PNG", quality=picture_quality
            )  # Change quality to reduce file size
        else:
            ExecLog(
                sModuleInfo,
                "Error saving %s screenshot to %s" % (screen_capture_type, ImageName),
                3,
            )

    except:
        ExecLog(
            sModuleInfo,
            "Unable To Capture image.  Device Maybe Blocking Screen Capture.",
            1,
        )


def TimeStamp(format):
    """
    :param format: name of format ex: string , integer
    :return:
    ========= Instruction: ============
    Function Description:
    This function is used to create a Time Stamp.
    It will return current Day-Month-Date-Hour:Minute:Second-Year all in one string
    OR
    It will return current YearMonthDayHourMinuteSecond all in a integer.
    Parameter Description:
    - string: this returns a readable string for the current date and time format
        Example:
        TimeStamp = TimeStamp("string") = Fri-Jan-20-10:20:31-2012
    - integer: this returns a readable string for the current date and time format
        Example:
        TimeStamp = TimeStamp("integer") = 2012120102051
    ======= End of Instruction: =========
    """
    if format == "string":
        TimeStamp = datetime.datetime.now().ctime().replace(" ", "-").replace("--", "-")
    elif format == "integer":
        TimeStamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    elif format == "utc":
        TimeStamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")
    elif format == "utcstring":
        TimeStamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    else:
        TimeStamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

    return TimeStamp


def set_exit_mode(emode):
    """ Sets a value in the temp config file to tell sequential actions to exit, if set to true """
    # Set by the user via the GUI
    ConfigModule.add_config_value("sectionOne", "exit_script", str(emode), temp_config)


def check_offline():
    """ Checks the value set in the temp config file to tell sequential actions to exit, if set to true """
    # Set by the user via the GUI
    value = ConfigModule.get_config_value("sectionOne", "exit_script", temp_config)
    if value == "True":
        return True
    else:
        return False


class MachineInfo:
    def getLocalIP(self):
        """
        :return: get local address of machine
        """
        try:
            import socket

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("gmail.com", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip

        except Exception as e:
            return Exception_Handler(sys.exc_info())

    def getLocalUser(self):
        """
        :return: returns the local pc name
        """
        try:
            # node_id_file_path = os.path.join(FL.get_home_folder(), os.path.join('Desktop', 'node_id.conf'))

            # node_id_file_path = os.path.join (os.path.realpath(__file__).split("Framework")[0] , os.path.join ('node_id.conf'))
            node_id_file_path = Path(
                os.path.abspath(__file__).split("Framework")[0]
            ) / Path("node_id.conf")

            if os.path.isfile(node_id_file_path):
                unique_id = ConfigModule.get_config_value(
                    "UniqueID", "id", node_id_file_path
                )
                if unique_id == "":
                    ConfigModule.clean_config_file(node_id_file_path)
                    ConfigModule.add_section("UniqueID", node_id_file_path)
                    unique_id = uuid.uuid4()
                    unique_id = str(unique_id)[:10]
                    ConfigModule.add_config_value(
                        "UniqueID", "id", unique_id, node_id_file_path
                    )
                    machine_name = (
                        ConfigModule.get_config_value("Authentication", "username")
                        + "_"
                        + str(unique_id)
                    )
                    return machine_name[:100]
                machine_name = (
                    ConfigModule.get_config_value("Authentication", "username")
                    + "_"
                    + str(unique_id)
                )
            else:
                # create the file name
                f = open(node_id_file_path, "w")
                f.close()
                unique_id = uuid.uuid4()
                unique_id = str(unique_id)[:10]
                ConfigModule.add_section("UniqueID", node_id_file_path)
                ConfigModule.add_config_value(
                    "UniqueID", "id", unique_id, node_id_file_path
                )
                machine_name = (
                    ConfigModule.get_config_value("Authentication", "username")
                    + "_"
                    + str(unique_id)
                )
            return machine_name[:100]

        except Exception:
            ErrorMessage = "Unable to set create a Node key.  Please check class MachineInfo() in commonutil"
            return Exception_Handler(sys.exc_info(), None, ErrorMessage)

    def getUniqueId(self):
        """
        :return: returns the local pc unique ID
        """
        try:
            # node_id_file_path = os.path.join(FL.get_home_folder(), os.path.join('Desktop', 'node_id.conf'))
            # node_id_file_path = os.path.join (os.path.realpath(__file__).split("Framework")[0] , os.path.join ('node_id.conf'))
            node_id_file_path = Path(
                os.path.abspath(__file__).split("Framework")[0]
            ) / Path("node_id.conf")

            if os.path.isfile(node_id_file_path):
                unique_id = ConfigModule.get_config_value(
                    "UniqueID", "id", node_id_file_path
                )
                if unique_id == "":
                    ConfigModule.clean_config_file(node_id_file_path)
                    ConfigModule.add_section("UniqueID", node_id_file_path)
                    unique_id = uuid.uuid4()
                    unique_id = str(unique_id)[:10]
                    ConfigModule.add_config_value(
                        "UniqueID", "id", unique_id, node_id_file_path
                    )
                    machine_name = str(unique_id)
                    return machine_name[:100]
                machine_name = str(unique_id)
            else:
                # create the file name
                f = open(node_id_file_path, "w")
                f.close()
                unique_id = uuid.uuid4()
                unique_id = str(unique_id)[:10]
                ConfigModule.add_section("UniqueID", node_id_file_path)
                ConfigModule.add_config_value(
                    "UniqueID", "id", unique_id, node_id_file_path
                )
                machine_name = str(unique_id)
            return machine_name[:100]

        except Exception:
            ErrorMessage = "Unable to set create a Node key.  Please check class MachineInfo() in commonutil"
            return Exception_Handler(sys.exc_info(), None, ErrorMessage)
