import os
import sys
import time
import inspect
import datetime
from selenium import webdriver
from Utilities import CommonUtil
from Utilities import LogAnalyzer
from ReCellSuite.prod import prod_ui
from Automation.Desktop.Linux import commandline
from Automation.Mobile.Android.ADB_Calls import adbOptions

'''Begin Constants'''
Passed = 'Passed'
Failed = 'Failed'
'''End Constants'''

local_run = False
log_path = None


def start_appium(command='appium'):

    # Right now, this function starts appium for linux through command line
    # The function first checks if the required environment variables have been set
    # If they have not been set, it first sets the environment variables, then starts appium through command line
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

    try:
        # checking if environment variables are set, if not, then set them
        env_vars = {'PATH': '', 'LD_LIBRARY_PATH': '', 'ANDROID_HOME': '', 'HOME': ''}
        not_set = False

        CommonUtil.ExecLog(sModuleInfo, "checking if appium environment variables have been set...")

        for var in env_vars.keys():
            CommonUtil.ExecLog(sModuleInfo, "checking ")
            env_value = os.getenv(var)

            if env_value:
                env_vars[var] = env_value

            elif not env_value:
                not_set = True

        if not_set:
            os.environ['PATH'] = env_vars['HOME'] + "/.linuxbrew/bin:" + env_vars['PATH']
            env_vars['PATH'] = env_vars['HOME'] + "/.linuxbrew/bin:" + env_vars['PATH']

            os.environ['LD_LIBRARY_PATH'] = env_vars['HOME'] + "/.linuxbrew/lib:" + env_vars['LD_LIBRARY_PATH']
            env_vars['LD_LIBRARY_PATH'] = env_vars['HOME'] + "/.linuxbrew/lib:" + env_vars['LD_LIBRARY_PATH']

            os.environ['ANDROID_HOME'] = "/home/asci/android-sdk-linux"
            env_vars['ANDROID_HOME'] = "/home/asci/android-sdk-linux"

            os.environ['PATH'] = env_vars['PATH'] + ":" + env_vars['ANDROID_HOME'] + "/tools:" + \
                env_vars['ANDROID_HOME'] + "/platform-tools"
            env_vars['PATH'] = env_vars['PATH'] + ":" + env_vars['ANDROID_HOME'] + "/tools:" + \
                env_vars['ANDROID_HOME'] + "/platform-tools"

        CommonUtil.ExecLog(sModuleInfo, "Killing appium with command: killall node. ", 1, local_run)
        commandline.run_cmd('killall node')
        time.sleep(2)

        # If log_path has been defined, that means that DSE launch has happened, as that sets logpath value
        if log_path:
            app_installed = False
            CommonUtil.ExecLog(sModuleInfo, "Checking if VerifyApplicationInstalledService has started in DSE log. ",
                                            "This is to ensure appium takes over only after ProD has been installed. ",
                               1, local_run)

            log_analyzer = LogAnalyzer.LogAnalyzer(log_path)
            dse_start = log_analyzer.find_start_time_of_dse()

            # Poll the dse log for 3 minutes to see if app has been installed if DSE is involved
            # If app has been installed, then break out of the while loop
            start_time = time.time()
            while time.time() - start_time < 180 and not app_installed:
                install_logs = log_analyzer.find_log_by_service('VerifyApplicationInstalledService')

                for logs in install_logs:

                    if 'time' in logs.keys():

                        try:
                            # See if time format is a datetime object.
                            # If it is, the try part will work without exceptions.
                            if logs['time'] > dse_start:
                                CommonUtil.ExecLog(sModuleInfo, "ProD app has been installed.", 1, local_run)
                                app_installed = True
                                # This is necessary because while loop only takes control when for loop is done
                                break

                        except:
                            # If time is not a datetime object, and a string. We will have an exception. So, now convert
                            # the time to datetime object, then compare.
                            dse_start = datetime.datetime.strptime(dse_start, '%Y-%m-%d %H:%M:%S')

                            if logs['time'] > dse_start:
                                CommonUtil.ExecLog(sModuleInfo, "ProD app has been installed.", 1, local_run)
                                app_installed = True
                                # This is necessary because while loop only takes control when for loop is done
                                break

        CommonUtil.ExecLog(sModuleInfo, "Starting appium with command: %s " % command, 1, local_run)
        appium_status = commandline.run_cmd(command)
        time.sleep(10)

        return appium_status

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " +
                        str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start appium: %s"% Error_Detail, 3, local_run)

        return Failed


def kill_appium(command="killall node"):

    # Right now, this function kills appium for linux through command line
    # First, it goes to prod script and kills the driver, then kills appium through command line
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

    try:
        CommonUtil.ExecLog(sModuleInfo, "checking if prod driver is running, if active, driver will be closed",
                           1, local_run)

        # close appium driver before killing appium server
        close_status = close_driver(prod_ui.driver)

        if close_status == Passed:
            # If the driver has been closed, set its value to none
            prod_ui.driver = None
            # If no driver is present, then the test language has to be none as well
            prod_ui.language = None
        else:
            CommonUtil.ExecLog(sModuleInfo, "could not check for prod driver successfully..."
                                            "closing appium server anyways...", 3, local_run)

        CommonUtil.ExecLog(sModuleInfo, "killing appium server with command: %s... " % command, 1, local_run)
        kill_status = commandline.run_cmd(command)

        return kill_status

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) +
                        ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "unable to kill appium server . Error: %s" % Error_Detail, 3, local_run)

        return Failed


def initialize_driver(local_port, desired_caps):

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

    try:
        CommonUtil.ExecLog(sModuleInfo, "initializing appium driver and launching app: %s..." %
                           desired_caps['app_package'], 1, local_run)

        # Initialize driver object to none. This will be returned if function passes
        driver = None
        # Maximum number of times the driver will try to initialize
        max_tries = 3
        # create dictionary object for driver

        # Give appium driver max_tries attempts to initialize
        for tries in range(0, max_tries):

            try:
                if not desired_caps['platformVersion']:
                    desired_caps['platformVersion'] = adbOptions.get_android_version()
                    CommonUtil.ExecLog(sModuleInfo, "platformVersion: %s" %
                                       desired_caps['platformVersion'], 1, local_run)
                    adbOptions.kill_adb_server()

                if not desired_caps['deviceName']:
                    desired_caps['deviceName'] = adbOptions.get_device_model()
                    CommonUtil.ExecLog(sModuleInfo, "platformName: %s" %
                                       desired_caps['platformName'], 1, local_run)
                    adbOptions.kill_adb_server()

                driver = webdriver.Remote(local_port, desired_caps)

                CommonUtil.ExecLog(sModuleInfo, "initialized appium driver, and launched app succesfully...",
                                   1, local_run)
                time.sleep(5)
                break

            except Exception, e:
                driver = None

                # Remember tries has values 0 to max_tries-1
                if tries == max_tries - 1:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
                        exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not initialize appium driver. %s" % Error_Detail, 3,
                                       local_run)
                    return Failed

                else:
                    CommonUtil.ExecLog(sModuleInfo, "could not initialize appium driver, retrying...", 1, local_run)

        return driver

    except Exception, e:

        driver = None
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not initialize appium driver. %s" % Error_Detail, 3, local_run)

        return Failed


def close_driver(driver):

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

    try:
        CommonUtil.ExecLog(sModuleInfo, "closing appium driver....", 1, local_run)

        if driver:
            driver.quit()
            CommonUtil.ExecLog(sModuleInfo, "closed appium driver successfully", 1, local_run)
        else:
            CommonUtil.ExecLog(sModuleInfo, "no appium driver to close....", 1, local_run)

        return Passed

    except Exception, e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "unable to close appium driver. Error: %s" % Error_Detail, 3, local_run)

        return Failed
