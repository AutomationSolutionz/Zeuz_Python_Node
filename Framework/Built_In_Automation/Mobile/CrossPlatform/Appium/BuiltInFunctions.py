
# Android environment
from appium import webdriver
import os, sys, time, inspect, json
from Framework.Utilities import CommonUtil, FileUtilities
from Framework.Built_In_Automation.Mobile.Android.adb_calls import adbOptions
from appium.webdriver.common.touch_action import TouchAction
#from Built_In_Automation.Mobile.CrossPlatform.Appium import clickinteraction as ci
#from Built_In_Automation.Mobile.CrossPlatform.Appium import textinteraction as ti

#from selenium import webdriver as webdriverSelenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dropbox.files import Dimensions



PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


global driver
#driver = None

global WebDriver_Wait 
WebDriver_Wait = 20

global APPIUM_DRIVER_LIST
APPIUM_DRIVER_LIST = {}


def getDriversList():
    return APPIUM_DRIVER_LIST


def getDriver(index):
    try:
        return APPIUM_DRIVER_LIST[index]
    except Exception, e:
        return False


def addDriver(position, driver, port):
    try:
        APPIUM_DRIVER_LIST.update({position: {'driver':driver, 'port': port}})
        return True
    except Exception, e:
        return False


def start_selenium_hub(file_location = os.path.join(FileUtilities.get_home_folder(), os.path.join('Desktop', 'selenium-server-standalone-2.43.1.jar'))):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting Selenium Hub", 1)
        console_run("java -jar %s -role hub" % file_location)
        CommonUtil.ExecLog(sModuleInfo, "Selenium Hub Command given", 1)
        return True
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to Start Selenium Hub: Error:%s" % (Error_Detail), 3)
        return False

def console_run(run_command):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        os.system("gnome-terminal --working-directory %s -e 'bash -c \"%s ;exec bash\"'" % (FileUtilities.get_home_folder(),run_command))
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to run command", 3)
        return False


def init_config_for_device(port_to_connect, device_index, hub_address='127.0.0.1', hub_port=4444, base_location = os.path.join(FileUtilities.get_home_folder(), os.path.join('Desktop', 'appiumConfig')), **kwargs):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        dictJson={
            "configuration":
                {
                    "nodeTimeout": 120,
                    "port": port_to_connect,
                    "hubPort": hub_port,
                    "proxy": "org.openqa.grid.selenium.proxy.DefaultRemoteProxy",
                    "url": "http://%s:%d/wd/hub"%(hub_address,port_to_connect),
                    "hub": "%s:%d/grid/register"%(hub_address, hub_port),
                    "hubHost": "%s"%(hub_address),
                    "nodePolling": 2000,
                    "registerCycle": 10000,
                    "register": True,
                    "cleanUpCycle": 2000,
                    "timeout": 30000,
                    "maxSession": 1
                }
        }
        dictJson.update({'capabilities':[kwargs]})
        if not os.path.exists(base_location):
            FileUtilities.CreateFolder(base_location)
        file_location = os.path.join(base_location, 'nodeConfig%d.json'%device_index)
        with open(file_location, 'w') as txtfile:
            json.dump(dictJson, txtfile)
        #start appium instance
        set_appium_specific_variable()
        start_appium_instances(port_to_connect, file_location)
        return True
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to initiate appium instance for device:%d"%device_index, 3)
        return False


def set_appium_specific_variable():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        env_vars = {'PATH': '', 'LD_LIBRARY_PATH': '', 'ANDROID_HOME': '', 'HOME': ''}
        not_set = False

        for var in env_vars.keys():
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

            os.environ['ANDROID_HOME'] = os.path.join(FileUtilities.get_home_folder(), "android-sdk-linux")
            env_vars['ANDROID_HOME'] = os.path.join(FileUtilities.get_home_folder(), "android-sdk-linux")

            os.environ['PATH'] = env_vars['PATH'] + ":" + env_vars['ANDROID_HOME'] + "/tools:" + \
                                 env_vars['ANDROID_HOME'] + "/platform-tools"
            env_vars['PATH'] = env_vars['PATH'] + ":" + env_vars['ANDROID_HOME'] + "/tools:" + \
                               env_vars['ANDROID_HOME'] + "/platform-tools"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set appium variable", 3)
        return False

def start_appium_instances(port_to_connect, file_location, hub_address = '127.0.0.1' ):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        run_command = "appium -a %s -p %d --nodeconfig %s" % (hub_address, port_to_connect, file_location)
        console_run(run_command)
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start appium instance at port :%d"%port_to_connect, 3)
        return False


def launch(package_name,activity_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        global driver
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        CommonUtil.ExecLog(sModuleInfo,"Trying to launch the app...",1)
        
        if 'driver' not in globals():
            # appium driver not initiated.
            outcome = launch_and_start_driver(package_name, activity_name)
            if outcome == "passed":
                CommonUtil.ExecLog(sModuleInfo,"App is launched",1)
                return "passed"
            elif outcome == "failed":
                CommonUtil.ExecLog(sModuleInfo, "App is not launched", 3)
                return "failed"
        else:
            #driver already initiated.
            CommonUtil.ExecLog(sModuleInfo,"App is launched already.",1)
            return "passed"
            """outcome = open()
            if outcome == "passed":
                CommonUtil.ExecLog(sModuleInfo,"App is launched",1)
                return outcome
            elif outcome == "failed":
                CommonUtil.ExecLog(sModuleInfo, "App is not launched", 3)
                return outcome"""
    
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start WebDriver. %s"%Error_Detail, 3)
        return "failed"


def launch_and_start_driver(package_name, activity_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to launch the app...",1)
        desired_caps = {}
        desired_caps['platformName'] = 'Android'
        df = adbOptions.get_android_version()
        #df = "4.4.2"
        CommonUtil.ExecLog(sModuleInfo,df,1)
        #adbOptions.kill_adb_server()
        desired_caps['platformVersion'] = df
        df = adbOptions.get_device_model()
        #df = "Android"
        CommonUtil.ExecLog(sModuleInfo,df,1)
        #adbOptions.kill_adb_server()

        desired_caps['deviceName'] = df
        desired_caps['appPackage'] = package_name
        desired_caps['appActivity'] = activity_name
        #desired_caps['appPackage'] = 'com.assetscience.androidprodiagnostics'
        #desired_caps['appActivity'] = 'com.assetscience.recell.device.android.prodiagnostics.MainActivity'
        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        wait(10)
        global driver
        #deletelater = WebDriverWait(driver, WebDriver_Wait)
        #print deletelater
        CommonUtil.ExecLog(sModuleInfo,"Launched the app successfully.",1)
        wait(3)
        return "passed"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start WebDriver. %s"%Error_Detail, 3)
        return "failed"
        
        
def close():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to close the app",1)
        driver.close_app()
        CommonUtil.ExecLog(sModuleInfo,"Closed the app successfully",1)
        driver.quit()
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to close the driver. %s"%Error_Detail, 3)
        return "failed"
    
    
def install(app_location, app_package, app_activity):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        CommonUtil.ExecLog(sModuleInfo,"Trying to install the app...",1)
        
        if 'driver' in globals():
            #driver initiated
            """if driver.is_app_installed(app_package):
                CommonUtil.ExecLog(sModuleInfo,"App is already installed.",1)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"App is not installed. Now installing...",1)"""
            outcome = load(app_location)
            if outcome == "passed":
                CommonUtil.ExecLog(sModuleInfo,"App is installed.",1)
                return "passed"
            elif outcome == "failed":
                CommonUtil.ExecLog(sModuleInfo, "Failed to install the app.", 3)
                return "failed"
        
        else:
            #driver not initiated
            try:
                #It will try to launch the app as if its already installed
                outcome = launch_and_start_driver(app_package, app_activity)
                if outcome == "passed":
                    CommonUtil.ExecLog(sModuleInfo,"App is installed already.",1)
                    return "passed"
                elif outcome == "failed":
                    CommonUtil.ExecLog(sModuleInfo, "App is not installed. Now trying to install and launch again...", 3)
                    answer = install_and_start_driver(app_location)
                    if answer == "passed":
                        CommonUtil.ExecLog(sModuleInfo,"App is installed",1)
                        return "passed"
                    elif answer == "failed":
                        CommonUtil.ExecLog(sModuleInfo, "Failed to install the app.", 3)
                        return "failed"
                    
            except:
                answer = install_and_start_driver(app_location)
                if answer == "passed":
                    CommonUtil.ExecLog(sModuleInfo,"App is installed.",1)
                    return "passed"
                elif answer == "failed":
                    CommonUtil.ExecLog(sModuleInfo, "Failed to install the app.", 3)
                    return "failed"
                    

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start WebDriver. %s"%Error_Detail, 3)
        return "failed"


def install_and_start_driver(app_location):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to install and then launch the app...",1)
        desired_caps = {}
        desired_caps['platformName'] = 'Android'
        df = adbOptions.get_android_version()
        CommonUtil.ExecLog(sModuleInfo,df,1)
        #adbOptions.kill_adb_server()
        desired_caps['platformVersion'] = df
        df = adbOptions.get_device_model()
        CommonUtil.ExecLog(sModuleInfo,df,1)
        #adbOptions.kill_adb_server()
        desired_caps['deviceName'] = df
        desired_caps['app'] = PATH(app_location)
        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        global driver
        CommonUtil.ExecLog(sModuleInfo,"Installed and launched the app successfully.",1)
        time.sleep(10)
        driver.implicitly_wait(5)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start WebDriver. %s"%Error_Detail, 3)
        return "failed"


def open():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to open the app",1)
        driver.launch_app()
        CommonUtil.ExecLog(sModuleInfo,"Opened the app successfully",1)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to open the app. %s"%Error_Detail, 3)
        return "failed"
    
    
def load(app_location):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to load the app..",1)
        #driver.install_app(app_location)
        adbOptions.install_app(app_location)
        CommonUtil.ExecLog(sModuleInfo,"Loaded the app successfully",1)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to load the app. %s"%Error_Detail, 3)
        return "failed"
    

def reset():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to reset the app...",1)
        driver.reset()
        wait(5)
        CommonUtil.ExecLog(sModuleInfo,"App is reset successfully",1)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to reset the app. %s"%Error_Detail, 3)
        return "failed"
    
    
def go_back():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to go back...",1)
        driver.back()
        CommonUtil.ExecLog(sModuleInfo,"Went back successfully",1)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go back. %s"%Error_Detail, 3)
        return "failed"

    
def wait(_time):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Starting waiting for %s seconds.."%_time,1)
        driver.implicitly_wait(_time)
        time.sleep(_time)
        CommonUtil.ExecLog(sModuleInfo,"Waited successfully",1)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to wait. %s"%Error_Detail, 3)
        return "failed"

    
def remove(app_package):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to remove app with package name %s..."%app_package,1)
        #if driver.is_app_installed(app_package):
            #CommonUtil.ExecLog(sModuleInfo,"App is installed. Now removing...",1)
        try:
            driver.remove_app(app_package)
            CommonUtil.ExecLog(sModuleInfo,"App is removed successfully.",1)
            return "passed"
        except:
            CommonUtil.ExecLog(sModuleInfo, "Unable to remove the app", 3)
            return "failed"
        """else:   
            CommonUtil.ExecLog(sModuleInfo,"App is not found.",3)
            return "failed" """
        
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to wait. %s"%Error_Detail, 3)
        return "failed"


def launch_ios_app():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to launch the app...",1)
        PATH = lambda p: os.path.abspath(
            os.path.join(os.path.dirname(__file__), p)
        )
        desired_caps = {}
        desired_caps['platformName'] = 'iOS'
        desired_caps['platformVersion'] = '7.1.2'
        desired_caps['deviceName'] = 'iPhone 4s'
        desired_caps['app'] = PATH('/Users/user/Documents/workspace/asut/pro-diagnostics-1.28.2.ipa')
        desired_caps['udid'] = '848b6a392f627ff995862ed57ec1f03530deb2b8'
        desired_caps['bundleId'] = 'com.assetscience.canada.prodiagnostics'
        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        global driver
        CommonUtil.ExecLog(sModuleInfo,"Launched the app successfully.",1)
        wait(10)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start WebDriver. %s"%Error_Detail, 3)
        return "failed"


#################################Generic functions###################################

def Get_Element(element_parameter, element_value, reference_parameter=False, reference_value=False,
                reference_is_parent_or_child=False, get_all_unvalidated_elements=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting locating element...", 1)
        #all_elements = Get_All_Elements(element_parameter,element_value)
        element = Get_Single_Element(element_parameter, element_value)
        if ((element == []) or (element == "failed")):
            CommonUtil.ExecLog(sModuleInfo, "Could not get the element with the given parameters and values. Please provide accurate data set(s) information.", 3)
            return "failed"
        #element = Element_Validation(element)
        return element
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find your element.  Error: %s" % (Error_Detail), 3)
        return "failed"


def Click_Element(element_parameter, element_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to click on element...", 1)
        if element_parameter == "name":
            result = click_element_by_name(driver, element_value)
        elif element_parameter == "id":
            result = click_element_by_id(driver, element_value)
        elif element_parameter == "accessibility_id":
            result = click_element_by_accessibility_id(driver, element_value)
        elif element_parameter == "class_name":
            result = click_element_by_class_name(driver, element_value)
        elif element_parameter == "xpath":
            result = click_element_by_xpath(driver, element_value)
        elif element_parameter == "android_uiautomator_text":
            result = click_element_by_android_uiautomator_text(driver, element_value)
        elif element_parameter == "android_uiautomator_description":
            result = click_element_by_android_uiautomator_description(driver, element_value)
        elif element_parameter == "ios_uiautomation":
            result = click_element_by_ios_uiautomation(driver, element_value)
        else:
            try:
                CommonUtil.ExecLog(sModuleInfo,
                                   "Trying to click on element with parameter - %s and value - %s ..." % (element_parameter, element_value),
                                   1)
                elem = driver.find_element_by_xpath("//*[@%s='%s']" % (element_parameter, element_value))
                if elem.is_enabled():
                    elem.click()
                    CommonUtil.ExecLog(sModuleInfo, "Clicked on element successfully", 1)
                    return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to click. The element is disabled.", 3)
                    return "failed"
            except Exception, e:
                CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
                    exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
                CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s" % Error_Detail, 3)
                return "failed"

        if result == "passed":
            CommonUtil.ExecLog(sModuleInfo, "Clicked on element successfully", 1)
            return "passed"
        elif result == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to click. The element is disabled.", 3)
            return "failed"

        """element_data = Validate_Step_Data(step_data)
        elem = Get_Element(element_data[0], element_data[1])
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo, "Clicked on element successfully", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to click. The element is disabled.", 3)
            return "failed" """
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s" % Error_Detail, 3)
        return "failed"


# Method to enter texts in a text box; step data passed on by the user
def Set_Text(element_parameter, element_value, text_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Inside Enter Text In Text Box function", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to set text in the textbox...", 1)
        if element_parameter == "name":
            result = set_text_by_name(driver, element_value, text_value)
        elif element_parameter == "id":
            result = set_text_by_id(driver, element_value, text_value)
        elif element_parameter == "accessibility_id":
            result = set_text_by_accessibility_id(driver, element_value, text_value)
        elif element_parameter == "class_name":
            result = set_text_by_class_name(driver, element_value, text_value)
        elif element_parameter == "xpath":
            result = set_text_by_xpath(driver, element_value, text_value)
        elif element_parameter == "android_uiautomator_text":
            result = set_text_by_android_uiautomator_text(driver, element_value, text_value)
        elif element_parameter == "android_uiautomator_description":
            result = set_text_by_android_uiautomator_description(driver, element_value, text_value)
        elif element_parameter == "ios_uiautomation":
            result = set_text_by_ios_uiautomation(driver, element_value, text_value)
        else:
            elem = driver.find_element_by_xpath("//*[@%s='%s']" % (element_parameter, element_value))
            elem.click()
            elem.send_keys(text_value)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Entered text on element successfully", 1)
            return "passed"

        if result == "passed":
            CommonUtil.ExecLog(sModuleInfo, "Entered text successfully", 1)
            return "passed"
        elif result == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to enter text.", 3)
            return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not set text.  Error: %s" % (Error_Detail), 3)
        return "failed"


# Method to enter text in a text box and press enter to search of something
def Set_Text_Enter(element_parameter, element_value, text_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Inside Enter Text In Text Box function", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to set text in the textbox...", 1)

        #elem = driver.find_element_by_xpath("//*[@%s='%s']" % (element_parameter, element_value))
        elem = Get_Single_Element(element_parameter, element_value)
        elem.click()
        elem.send_keys(text_value + "\n")
        CommonUtil.ExecLog(sModuleInfo, "Entered text on element successfully", 1)
        return "passed"
        CommonUtil.ExecLog(sModuleInfo, "Entered and searched text successfully", 1)

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not set text and search.  Error: %s" % (Error_Detail), 3)
        return "failed"

# Method to enter texts in a text box; step data passed on by the user
def Enter_Text_In_Text_Box(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Inside Enter Text In Text Box function", 1)
    try:
        # If there are no two separate data-sets, or if the first data-set is not between 1 to 3 items, or if the second data-set doesn't have only 1 item
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):  # or (len(step_data[1]) != 1)):
            CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
            return "failed"
        else:
            element_step_data = step_data[0][0:len(step_data[0]) - 1:1]
            returned_step_data_list = Validate_Step_Data(element_step_data)
            # returned_step_data_list = Validate_Step_Data(step_data[0])
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1],
                                          returned_step_data_list[2], returned_step_data_list[3],
                                          returned_step_data_list[4])
                    text_value = step_data[0][len(step_data[0]) - 1][2]
                    # text_value = step[1][0][2]
                    # text_value=step_data[1][0][1]
                    Element.click()
                    Element.clear()
                    Element.set_value(text_value)
                    Element.click()
                    CommonUtil.TakeScreenShot(sModuleInfo)
                    CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s" % text_value,
                                       1)
                    return "passed"
                except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = (
                    (str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
                        exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo,
                                       "Could not select/click your element.  Error: %s" % (Error_Detail), 3)
                    return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find your element.  Error: %s" % (Error_Detail), 3)
        return "failed"



    # Method to get the elements based on type - more methods may be added in the future
    # Called by: Get_Elements
def Get_Single_Element(parameter, value, parent=False):
    # http://selenium-python.readthedocs.io/locating-elements.html
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        All_Elements = []
        if parent == False:
            if parameter == "name":
                All_Elements = driver.find_element_by_name(value)
            elif parameter == "id":
                All_Elements = driver.find_element_by_id(value)
            elif parameter == "accessibility_id":
                All_Elements = driver.find_element_by_accessibility_id(value)
            elif parameter == "class_name":
                All_Elements = driver.find_element_by_class_name(value)
            elif parameter == "xpath":
                #All_Elements = driver.find_element_by_xpath(value)
                All_Elements == driver.find_element_by_xpath("//*[@%s='%s']" % (parameter, value))
            elif parameter == "android_uiautomator_text":
                All_Elements == driver.find_element_by_android_uiautomator('new UiSelector().text(' + value + ')')
            elif parameter == "android_uiautomator_description":
                All_Elements == driver.find_element_by_android_uiautomator(
                    'new UiSelector().description(' + value + ')')
            elif parameter == "ios_uiautomation":
                All_Elements == driver.find_element_by_ios_uiautomation('.elements()[0]')
            else:
                All_Elements == driver.find_element_by_xpath("//*[@%s='%s']"%(parameter, value))

        elif parent == True:
            if parameter == "name":
                All_Elements = driver.find_element_by_xpath("//*[@text='%s']" % value)
            elif parameter == "id":
                All_Elements = driver.find_element_by_id(value)
            elif parameter == "accessibility_id":
                All_Elements = driver.find_element_by_accessibility_id(value)
            elif parameter == "class_name":
                All_Elements = driver.find_element_by_class_name(value)
            elif parameter == "xpath":
                #All_Elements = driver.find_element_by_xpath(value)
                All_Elements == driver.find_element_by_xpath("//*[@%s='%s']" % (parameter, value))
            elif parameter == "android_uiautomator_text":
                All_Elements == driver.find_element_by_android_uiautomator('new UiSelector().text(' + value + ')')
            elif parameter == "android_uiautomator_description":
                All_Elements == driver.find_element_by_android_uiautomator(
                    'new UiSelector().description(' + value + ')')
            elif parameter == "ios_uiautomation":
                All_Elements == driver.find_element_by_ios_uiautomation('.elements()[0]')
            else:
                All_Elements == driver.find_element_by_xpath("//*[@%s='%s']"%(parameter,value))

        return All_Elements
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to get the element.  Error: %s" % (Error_Detail), 3)
        return "failed"


# Method to get the elements based on type - more methods may be added in the future
# Called by: Get_Elements
def Get_All_Elements(parameter, value, parent=False):
    # http://selenium-python.readthedocs.io/locating-elements.html
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        All_Elements = []
        if parent == False:
            if parameter == "name":
                All_Elements = driver.find_elements_by_name(value)
            elif parameter == "id":
                All_Elements = driver.find_elements_by_id(value)
            elif parameter == "accessibility_id":
                All_Elements = driver.find_elements_by_accessibility_id(value)
            elif parameter == "class_name":
                All_Elements = driver.find_elements_by_class_name(value)
            elif parameter == "xpath":
                All_Elements = driver.find_elements_by_xpath(value)
            elif parameter == "android_uiautomator_text":
                All_Elements == driver.find_elements_by_android_uiautomator('new UiSelector().text('+value+')')
            elif parameter == "android_uiautomator_description":
                All_Elements == driver.find_elements_by_android_uiautomator('new UiSelector().description('+value+')')
        elif parent == True:
            if parameter == "name":
                All_Elements = driver.find_elements_by_name(value)
            elif parameter == "id":
                All_Elements = driver.find_elements_by_id(value)
            elif parameter == "accessibility_id":
                All_Elements = driver.find_elements_by_accessibility_id(value)
            elif parameter == "class_name":
                All_Elements = driver.find_elements_by_class_name(value)
            elif parameter == "xpath":
                All_Elements = driver.find_elements_by_xpath(value)
            elif parameter == "android_uiautomator_text":
                All_Elements == driver.find_elements_by_android_uiautomator('new UiSelector().text('+value+')')
            elif parameter == "android_uiautomator_description":
                All_Elements == driver.find_elements_by_android_uiautomator('new UiSelector().description('+value+')')

        return All_Elements
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to get the element.  Error: %s" % (Error_Detail), 3)
        return "failed"


#Validation of step data passed on by the user
def Validate_Step_Data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Validate_Step_Data", 1)
    try:    
        if (len(step_data)==1):
            element_parameter = step_data[0][0]
            element_value = step_data[0][2]
            reference_parameter = False
            reference_value = False    
            reference_is_parent_or_child = False
#         elif (len(step_data)==2):
#             for each in step_data:
#                 if each[1]=="element parameter 1 of 2":
#                     element_parameter = each[0]
#                     element_value = each[2]
#                 elif each[1]=="element parameter 2 of 2":
#                     reference_parameter = each[0]
#                     reference_value = each[2]
#             reference_is_parent_or_child = False
        elif (len(step_data)==3):
            for each in step_data:
                if each[1]=="element parameter":
                    element_parameter = each[0]
                    element_value = each[2]
                elif each[1]=="reference parameter":
                    reference_parameter = each[0]
                    reference_value = each[2]
                elif each[1]=="relation type":
                    reference_is_parent_or_child = each[2]
        else:
            CommonUtil.ExecLog(sModuleInfo, "Data set incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        validated_data = (element_parameter, element_value, reference_parameter, reference_value, reference_is_parent_or_child)
        return validated_data
    except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()        
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
            CommonUtil.ExecLog(sModuleInfo, "Could not find the new page element requested.  Error: %s"%(Error_Detail), 3)
            return "failed"


def Element_Validation(All_Elements_Found):#, index):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        #index = int(index)
        return_element = []
        all_visible_elements = []
        all_invisible_elements = []
        if All_Elements_Found == []:
            CommonUtil.ExecLog(sModuleInfo, "Could not find your element by given parameters and values", 3)
            return "failed"
        elif len(All_Elements_Found) == 1:
            for each_elem in All_Elements_Found:
                #Case 1: Found only one invisible element - pass with warning
                if each_elem.is_displayed() == False:
                    return_element.append(each_elem)
                    CommonUtil.ExecLog(sModuleInfo, "Found one invisible element by given parameters and values", 2)
                #Case 2: Found only one visible element - pass
                elif each_elem.is_displayed() == True:
                    return_element.append(each_elem)
                    CommonUtil.ExecLog(sModuleInfo, "Found one visible element by given parameters and values", 1)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Could not find element by given parameters and values", 3)
                    return "failed"
            return return_element[0]

        elif len(All_Elements_Found) > 1:
            CommonUtil.ExecLog(sModuleInfo, "Found more than one element by given parameters and values, validating visible and invisible elements. Total number of elements found: %s"%(len(All_Elements_Found)), 2)
            for each_elem in All_Elements_Found:
                if each_elem.is_displayed() == True:
                    all_visible_elements.append(each_elem)
                else:
                    all_invisible_elements.append(each_elem)
            #sequential logic - if at least one is_displayed() elements, show that, else allow invisible elements
            if len(all_visible_elements) > 0:
                CommonUtil.ExecLog(sModuleInfo, "Found at least one visible element for given parameters and values, returning the first one or by the index specified", 2)
                return_element = all_visible_elements
            else:
                CommonUtil.ExecLog(sModuleInfo, "Did not find a visible element, however, invisible elements present", 2)
                return_element = all_invisible_elements
            return return_element[0]#[index]

        else:
            CommonUtil.ExecLog(sModuleInfo, "Could not find element by given parameters and values", 3)
            return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to get the element.  Error: %s"%(Error_Detail), 3)
        return "failed"


# Performs a series of action or logical decisions based on user input
def Sequential_Actions(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        logic_row = []
        for each in step_data:
            # finding what to do for each dataset
            if each[0][1] == "action":
                CommonUtil.TakeScreenShot(sModuleInfo)
                result = Action_Handler(each[0][0], each[1], each[0][2])
                CommonUtil.TakeScreenShot(sModuleInfo)
                if result == [] or result == "failed":
                    return "failed"
            elif each[1][1] == "action":
                CommonUtil.TakeScreenShot(sModuleInfo)
                result = Action_Handler(each[1][0], each[0], each[1][2])
                CommonUtil.TakeScreenShot(sModuleInfo)
                if result == [] or result == "failed":
                    return "failed"
            elif each[0][1] == "logic":
                logic_decision = ""
                logic_row.append(each[1])
                if len(logic_row) == 2:
                    element_step_data = each[0:len(step_data[0]) - 2:1]
                    returned_step_data_list = Validate_Step_Data(element_step_data)
                    if(returned_step_data_list == []) or (returned_step_data_list == "failed"):
                        return "failed"
                    else:
                        try:
                            Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1],
                                                  returned_step_data_list[2], returned_step_data_list[3],
                                                  returned_step_data_list[4])
                            if Element == 'failed':
                                logic_decision = "false"
                            else:
                                logic_decision = "true"
                        except Exception, errMsg:
                            errMsg = "Could not find element in the by the criteria..."
                            Exception_Info(sModuleInfo, errMsg)
                else:
                    continue

                for conditional_steps in logic_row:
                    if logic_decision in conditional_steps:
                        print conditional_steps[2]
                        list_of_steps = conditional_steps[2].split(",")
                        for each_item in list_of_steps:
                            data_set_index = int(each_item) - 1
                            Sequential_Actions([step_data[data_set_index]])
                        return "passed"

            else:
                CommonUtil.ExecLog(sModuleInfo,
                                   "The sub-field information is incorrect. Please provide accurate information on the data set(s).",
                                   3)
                return "failed"
        return "passed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print "%s" % Error_Detail
        CommonUtil.ExecLog(sModuleInfo, "Error: %s" % Error_Detail, 3)
        return "failed"


# Handles actions for the sequential logic, based on the input from the mentioned function
def Action_Handler(action_name, action_step_data=False, action_value=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        """ Need to add: long hold, pinch to zoom, """
        
        if action_name == "click":
            result = Click_Element(action_step_data[0], action_step_data[2])
            if result == "failed":
                return "failed"
        elif action_name == "text":
            result = Set_Text(action_step_data[0], action_step_data[2], action_value)
            if result == "failed":
                return "failed"
        elif action_name == "text_search":
            result = Set_Text_Enter(action_step_data[0], action_step_data[2], action_value)
            if result == "failed":
                return "failed"
        elif action_name == "wait":
            result = Wait(action_value)
            if result == "failed":
                return "failed"
        elif action_name == "swipe":
            result = Swipe()
            if result == "failed":
                return "failed"
        elif action_name == "tap":
            result = Tap(action_step_data[0], action_step_data[2])
            if result == "failed":
                return "failed"
        elif action_name == "go_back":
            result = Go_Back()
            if result == "failed":
                return "failed"
        elif action_name == "enter":
            result = SendKey_Enter()
            if result == "failed":
                return "failed"
        elif action_name == "validate full text" or action_name == "validate partial text":
            result = Validate_Text(action_step_data)
            if result == "failed":
                return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo,
                               "The action you entered is incorrect. Please provide accurate information on the data set(s).",
                               3)
            return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print "%s" % Error_Detail
        CommonUtil.ExecLog(sModuleInfo, "Error: %s" % Error_Detail, 3)
        return "failed"


def Exception_Info(sModuleInfo, errMsg):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
    CommonUtil.ExecLog(sModuleInfo, errMsg + ".  Error: %s"%(Error_Detail), 3)
    return "failed"


def SendKey_Enter():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to send enter key...", 1)
        driver.keyevent(66)
        CommonUtil.ExecLog(sModuleInfo, "Sent enter key successfully", 1)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to send enter key. %s" % Error_Detail, 3)
        return "failed"


def Go_Back():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to go back...", 1)
        driver.back()
        CommonUtil.ExecLog(sModuleInfo, "Went back successfully", 1)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go back. %s" % Error_Detail, 3)
        return "failed"


def Wait(time_to_wait):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting waiting for %s seconds.." % time_to_wait, 1)
        #function_data = Validate_Step_Data(step_data)
        driver.implicitly_wait(float(time_to_wait))
        time.sleep(float(time_to_wait))
        CommonUtil.ExecLog(sModuleInfo, "Waited successfully", 1)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to wait. %s" % Error_Detail, 3)
        return "failed"


def Swipe():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting to swipe the screen...", 1)
        driver.swipe(100, 500, 100, 100, 800)
        CommonUtil.ExecLog(sModuleInfo, "Swiped the screen successfully", 1)
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to swipe. %s" % Error_Detail, 3)
        return "failed"


def Tap(element_parameter, element_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting to tap the element...", 1)
        #element_data = Validate_Step_Data(step_data)
        elem = Get_Element(element_parameter, element_value)
        if elem.is_enabled():
            action = TouchAction(driver)
            action.tap(elem).perform()
            CommonUtil.ExecLog(sModuleInfo, "Tapped on element successfully", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to tap. The element is disabled.", 3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to tap. %s" % Error_Detail, 3)
        return "failed"


# Validating text from an element given information regarding the expected text
def Validate_Text(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare_Text_Data", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:
            dimension = driver.get_window_size('current')
            print dimension
            
            for each in step_data[0]:
                if each[0] == "current_page":
                    try:
                        Element = Get_Element_Appium('tag', 'html')
                        break
                    except Exception, e:
                        errMsg = "Could not get element from the current page."
                        Exception_Info(sModuleInfo, errMsg)
                else:
                    element_step_data = Get_Element_Step_Data_Appium(step_data)
                    returned_step_data_list = Validate_Step_Data(element_step_data)
                    if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                        return "failed"
                    else:
                        try:
                            Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                            break
                        except Exception, e:
                            errMsg = "Could not get element based on the information provided."
                            Exception_Info(sModuleInfo, errMsg)            
 
            for each_step_data_item in step_data[0]:
                if each_step_data_item[1]=="action":
                    expected_text_data = each_step_data_item[2]
                    validation_type = each_step_data_item[0]
            #expected_text_data = step_data[0][len(step_data[0]) - 1][2]
            list_of_element_text = Element.text.split('\n')
            visible_list_of_element_text = []
            for each_text_item in list_of_element_text:
                if each_text_item != "":
                    visible_list_of_element_text.append(each_text_item)
            
            #if step_data[0][len(step_data[0])-1][0] == "validate partial text":
            if validation_type == "validate partial text":
                actual_text_data = visible_list_of_element_text
                CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 1)
                CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 1)
                for each_actual_text_data_item in actual_text_data:
                    if expected_text_data in each_actual_text_data_item:
                        CommonUtil.ExecLog(sModuleInfo, "The text has been validated by a partial match.", 1)
                        return "passed"
                CommonUtil.ExecLog(sModuleInfo, "Unable to validate using partial match.", 3)
                return "failed"
            #if step_data[0][len(step_data[0])-1][0] == "validate full text":
            if validation_type == "validate full text":
                actual_text_data = visible_list_of_element_text
                CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 1)
                CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 1)
                if (expected_text_data in actual_text_data):
                    CommonUtil.ExecLog(sModuleInfo, "The text has been validated by using complete match.", 1)
                    return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to validate using complete match.", 3)
                    return "failed"
            
            else:
                CommonUtil.ExecLog(sModuleInfo, "Incorrect validation type. Please check step data", 3)
                return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not compare text as requested.  Error: %s" % (Error_Detail), 3)
        return "failed"


'''
   Moving all locate, Click and text interaction function under one 
'''
#location




def locate_element_by_id(driver, _id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by id: %s"%_id,1)
        elem = driver.find_element_by_id(_id)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)

def locate_elements_by_id(driver, _id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate elements by id: %s"%_id,1)
        elems = driver.find_elements_by_id(_id)
        return elems
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate elements. %s"%Error_Detail, 3)

    
def locate_element_by_name(driver, _name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by name: %s"%_name,1)
        elem = driver.find_element_by_name(_name)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)
    
    
def locate_element_by_class_name(driver, _class):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by class: %s"%_class,1)
        elem = driver.find_element_by_class_name(_class)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)
    
    
def locate_element_by_xpath(driver, _classpath):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by xpath: %s"%_classpath,1)
        elem = driver.find_element_by_xpath(_classpath)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)
    
def locate_element_by_accessibility_id(driver, _id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by accessibility id: %s"%_id,1)
        elem = driver.find_element_by_accessibility_id(_id)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)


def locate_element_by_android_uiautomator_text(driver, _text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by android uiautomator text: %s"%_text,1)
        elem = driver.find_element_by_android_uiautomator('new UiSelector().text('+_text+')')
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)


def locate_element_by_android_uiautomator_description(driver, _description):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by android uiautomator description: %s"%_description,1)
        elem = driver.find_element_by_android_uiautomator('new UiSelector().description('+_description+')')
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)


def locate_element_by_ios_uiautomation(driver, _description):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by ios uiautomatoion: %s"%_description,1)
        elem = driver.find_element_by_ios_uiautomation('.elements()[0]')
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3)




    
#Click

    
def click_element_by_id(driver, _id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by id: %s"%_id,1)
        elem = locate_element_by_id(driver, _id)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"
    
def click_element_by_name(driver, _name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by name: %s"%_name,1)
        elem = locate_element_by_name(driver, _name)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"
    
def click_element_by_class_name(driver, _class):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by class: %s"%_class,1)
        elem = locate_element_by_class_name(driver, _class)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"
    
def click_element_by_xpath(driver, _classpath):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by xpath: %s"%_classpath,1)
        elem = locate_element_by_xpath(driver, _classpath)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"
    
def click_element_by_accessibility_id(driver, _id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by accessibility id: %s"%_id,1)
        elem = locate_element_by_accessibility_id(driver, _id)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"
    
def click_element_by_android_uiautomator_text(driver, _text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by android uiautomator text: %s"%_text,1)
        elem = locate_element_by_android_uiautomator_text(driver, _text)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"
    
def click_element_by_android_uiautomator_description(driver, _description):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by android uiautomator description: %s"%_description,1)
        elem = locate_element_by_android_uiautomator_description(driver, _description)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"


def click_element_by_ios_uiautomation(driver, _description):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by android uiautomator description: %s"%_description,1)
        elem = locate_element_by_ios_uiautomation(driver, _description)
        if elem.is_enabled():
            elem.click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Unable to click. The element is disabled.",3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3)
        return "failed"

#text



def set_text_by_id(driver, _id, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by id: %s"%_id,1)
        elem = locate_element_by_id(driver, _id)
        if elem.is_displayed():
            elem.click()
            #driver.hide_keyboard()
            #elem.set_value(text)
            #driver.set_value(elem, text)
            elem.send_keys(text)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"
        #driver.set_value(elem, text)

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s"%Error_Detail, 3)
        return "failed"


def set_text_by_name(driver, _name, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by name: %s"%_name,1)
        elem = locate_element_by_name(driver, _name)
        if elem.is_displayed():
            elem.click()
            elem.send_keys(text)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s"%Error_Detail, 3)
        return "failed"


def set_text_by_class_name(driver, _class, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by class: %s"%_class,1)
        elem = locate_element_by_class_name(driver, _class)
        if elem.is_displayed():
            elem.click()
            elem.send_keys(text)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s"%Error_Detail, 3)
        return "failed"


def set_text_by_xpath(driver, _classpath, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by xpath: %s"%_classpath,1)
        elem = locate_element_by_xpath(driver, _classpath)
        if elem.is_displayed():
            elem.click()
            elem.send_keys(text)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s"%Error_Detail, 3)
        return "failed"


def set_text_by_accessibility_id(driver, _id, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by accessibility id: %s"%_id,1)
        elem = locate_element_by_accessibility_id(driver, _id)
        if elem.is_displayed():
            elem.click()
            elem.send_keys(text)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s" % Error_Detail, 3)
        return "failed"


def set_text_by_android_uiautomator_text(driver, _text, text_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to click on element by android uiautomator text: %s" % _text, 1)
        elem = locate_element_by_android_uiautomator_text(driver, _text)
        if elem.is_displayed():
            elem.click()
            elem.send_keys(text_value)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s" % Error_Detail, 3)
        return "failed"


def set_text_by_android_uiautomator_description(driver, _description, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,
                           "Trying to click on element by android uiautomator description: %s" % _description, 1)
        elem = locate_element_by_android_uiautomator_description(driver, _description)
        if elem.is_displayed():
            elem.click()
            elem.send_keys(text)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s" % Error_Detail, 3)
        return "failed"


def set_text_by_ios_uiautomation(driver, _description, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,
                           "Trying to click on element by android uiautomator description: %s" % _description, 1)
        elem = locate_element_by_ios_uiautomation(driver, _description)
        if elem.is_displayed():
            elem.click()
            elem.send_keys(text)
            driver.hide_keyboard()
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s" % Error_Detail, 3)
        return "failed"

"""=======================Riasat======================="""
'============================= Get Elements Section Begins =============================='    

def Get_Element_Appium(element_parameter,element_value,reference_parameter=False,reference_value=False,reference_is_parent_or_child=False,get_all_unvalidated_elements=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        All_Elements_Found = []
        if reference_is_parent_or_child == False:
            if ((reference_parameter == False) and (reference_value == False)):
                All_Elements = Get_All_Elements_Appium(element_parameter,element_value)     
                if ((All_Elements == []) or (All_Elements == 'failed')):        
                    CommonUtil.ExecLog(sModuleInfo, "Could not find your element by parameter:%s and value:%s..."%(element_parameter,element_value), 3)
                    return "failed"
                else:
                    All_Elements_Found = All_Elements
            #elif (reference_parameter != False and reference_value!= False):
            #    CommonUtil.ExecLog(sModuleInfo, "Locating element using double matching", 1)
            #    All_Elements = Get_Double_Matching_Elements(element_parameter, element_value, reference_parameter, reference_value)
            #    if ((All_Elements == []) or (All_Elements == "failed")):
            #        CommonUtil.ExecLog(sModuleInfo, "Could not find your element by parameter1:%s , value1:%s and parameter2:%s , value2:%s..."%(element_parameter,element_value,reference_parameter,reference_value), 3)
            #        return "failed"
            #    else:
            #        All_Elements_Found = All_Elements
            else:
                CommonUtil.ExecLog(sModuleInfo, "Could not find your element because you are missing at least one parameter", 3)
                return "failed"
            
        elif reference_is_parent_or_child == "parent":     
            CommonUtil.ExecLog(sModuleInfo, "Locating all parents elements", 1)   
            all_parent_elements = Get_All_Elements_Appium(reference_parameter,reference_value)#,"parent")
            all_matching_elements = []
            for each_parent in all_parent_elements:
                interested_elem = Get_All_Elements_Appium(element_parameter,element_value,each_parent) #can there be a problem when we send in each parent, or does this contain both param and value?
                if interested_elem != "failed":
                    for each_matching in interested_elem:
                        all_matching_elements.append(each_matching)
            All_Elements_Found = all_matching_elements

        elif reference_is_parent_or_child == "child":        
            all_parent_elements = Get_All_Elements_Appium(element_parameter,element_value)
            all_matching_elements = []
            for each_parent in all_parent_elements:
                interested_elem = Get_All_Elements_Appium(reference_parameter,reference_value,each_parent)
                if interested_elem != "failed":
                    all_matching_elements.append(each_parent)
            All_Elements_Found=all_matching_elements
            
        elif ((reference_is_parent_or_child!="parent") or (reference_is_parent_or_child!="child") or (reference_is_parent_or_child!=False)):
            CommonUtil.ExecLog(sModuleInfo, "Unspecified reference type; please indicate whether parent, child or leave blank", 3)
            return "failed"
        
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to run based on the current inputs, please check the inputs and re-enter values", 3)
            return "failed"
        
        #this method returns all the elements found without validation
        if(get_all_unvalidated_elements!=False):
            return All_Elements_Found
        else:
            #can later also pass on the index of the element we want
            result = Element_Validation(All_Elements_Found)#, index)
            return result
    
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find your element.  Error: %s"%(Error_Detail), 3)
        return "failed"       


#Method to get the elements based on type - more methods may be added in the future
#Called by: Get_Element
def Get_All_Elements_Appium(parameter,value,parent=False):
    #http://selenium-python.readthedocs.io/locating-elements.html
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if parent == False:
            if parameter == "id":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_id(value))
            elif parameter == "name":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_name(value))
            elif parameter == "class_name":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_class_name(value))
            elif parameter == "xpath":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_xpath(value))
            elif parameter == "accessibility_id":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_accessibility_id(value))    
            elif parameter == "android_uiautomator":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_android_uiautomator(value))    
            elif parameter == "ios_uiautomation":
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_ios_uiautomation(value))    
            else:
                All_Elements = WebDriverWait(driver, WebDriver_Wait).until(lambda driver: driver.find_elements_by_xpath("//*[@%s='%s']" %(parameter,value)))
        else:
            if parameter == "id":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_id(value))
            elif parameter == "name":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_name(value))
            elif parameter == "class_name":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_class_name(value))
            elif parameter == "xpath":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_xpath(value))
            elif parameter == "accessibility_id":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_accessibility_id(value))    
            elif parameter == "android_uiautomator":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_android_uiautomator(value))    
            elif parameter == "ios_uiautomation":
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_ios_uiautomation(value))    
            else:
                All_Elements = WebDriverWait(parent, WebDriver_Wait).until(lambda driver: driver.find_elements_by_xpath("//*[@%s='%s']" %(parameter,value)))    
        
        return All_Elements
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to get the element.  Error: %s"%(Error_Detail), 3)
        return "failed"


'===================== ===x=== Get Element Section Ends ===x=== ======================'    
    
'============================= Sequential Actions Section Begins =============================='
'=================== Riasat ======================'
#Method to get the element step data from the original step_data
def Get_Element_Step_Data_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function - Get Element Step Data", 1)
    try:
        element_step_data=[]
        for each in step_data[0]:
            if (each[1]=="action" or each[1]=="conditional action"):
                CommonUtil.ExecLog(sModuleInfo, "Not a part of element step data", 2)
                continue
            else:
                element_step_data.append(each)
                 
        return element_step_data
    
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not get element step data.  Error: %s"%(Error_Detail), 3)
        return "failed"


#Performs a series of action or logical decisions based on user input
def Sequential_Actions_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:            
        for each in step_data:
            logic_row=[]
            for row in each:
                if ((row[1] == "element parameter") or (row[1] == "reference parameter") or (row[1] == "relation type") or (row[1] == "element parameter 1 of 2") or (row[1] == "element parameter 2 of 2")):     ##modifying the filter for changes to be made in the sub-field of the step data. May remove this part of the if statement                
                    continue
                
                elif row[1]=="action":
                    CommonUtil.ExecLog(sModuleInfo, "Checking the action to be performed in the action row", 1)
                    result = Action_Handler_Appium([each],row[0])
                    if result == [] or result == "failed":
                        return "failed"
                    
                elif row[1]=="conditional action":
                    CommonUtil.ExecLog(sModuleInfo, "Checking the logical conditional action to be performed in the conditional action row", 1)
                    logic_decision=""
                    logic_row.append(row)
                    if len(logic_row)==2:
                        #element_step_data = each[0:len(step_data[0])-2:1]
                        element_step_data = Get_Element_Step_Data_Appium([each])
                        returned_step_data_list = Validate_Step_Data(element_step_data) 
                        if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                            return "failed"
                        else:
                            try:
                                Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                                if Element == 'failed':
                                    logic_decision = "false"
                                else:
                                    logic_decision = "true"                                        
                            except Exception, errMsg:
                                errMsg = "Could not find element in the by the criteria..."
                                Exception_Info(sModuleInfo, errMsg)            
                    else:
                        continue

                    for conditional_steps in logic_row:
                        if logic_decision in conditional_steps:
                            print conditional_steps[2]
                            list_of_steps = conditional_steps[2].split(",")
                            for each_item in list_of_steps:
                                data_set_index = int(each_item) - 1
                                Sequential_Actions_Appium([step_data[data_set_index]])
                            return "passed"
                
                else:
                    CommonUtil.ExecLog(sModuleInfo, "The sub-field information is incorrect. Please provide accurate information on the data set(s).", 3)
                    return "failed"                 
        return "passed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail
        return "failed"
    

#Handles actions for the sequential logic, based on the input from the mentioned function
def Action_Handler_Appium(action_step_data, action_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        if action_name =="click":
            result = Click_Element_Appium(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name == "wait":
            result = Wait(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name == "swipe":
            result = Swipe_Appium(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name == "tap":
            result = Tap_Appium(action_step_data)
            if result == "failed":
                return "failed"
        elif (action_name == "Android keystroke" or action_name == "iOS keystroke"):
            result = Keystroke_Appium(action_step_data)
            if result == "failed":
                return "failed"
        elif (action_name == "validate full text" or action_name == "validate partial text"):
            result = Validate_Text_Appium(action_step_data)
            if result == "failed":
                return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "The action you entered is incorrect. Please provide accurate information on the data set(s).", 3)
            return "failed" 
        
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail
        return "failed"


#Method to click on element; step data passed on by the user
def Click_Element_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Click_Element_Appium", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:
            #element_step_data = step_data[0][0:len(step_data[0])-1:1]
            element_step_data = Get_Element_Step_Data_Appium(step_data)            
            returned_step_data_list = Validate_Step_Data(element_step_data) 
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                    if Element.is_enabled():
                        Element.click()
                        CommonUtil.TakeScreenShot(sModuleInfo)
                        CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element with given parameters and values", 1)
                        return "passed"
                    else:
                        CommonUtil.TakeScreenShot(sModuleInfo)
                        CommonUtil.ExecLog(sModuleInfo, "Element not enabled. Unable to click.", 3)
                        return "failed"
                except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()        
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not select/click your element.  Error: %s"%(Error_Detail), 3)
                    return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find/click your element.  Error: %s"%(Error_Detail), 3)
        return "failed"
    
    
def Tap_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Tap_Appium", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:    
            element_step_data = Get_Element_Step_Data_Appium(step_data)            
            returned_step_data_list = Validate_Step_Data(element_step_data) 
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                    if Element.is_enabled():
                        action = TouchAction(driver)
                        action.tap(Element).perform()
                        CommonUtil.ExecLog(sModuleInfo, "Tapped on element successfully", 1)
                        return "passed"
                    else:
                        CommonUtil.TakeScreenShot(sModuleInfo)
                        CommonUtil.ExecLog(sModuleInfo, "Element not enabled. Unable to click.", 3)
                        return "failed"
                except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()        
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not select/click your element.  Error: %s"%(Error_Detail), 3)
                    return "failed"
                
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to tap. %s" % Error_Detail, 3)
        return "failed"

# def Double_Tap_Appium_asifurrouf

def Double_Tap_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function:Double_Tap_Appium", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
            return "failed"
        else:
            element_step_data = Get_Element_Step_Data_Appium(step_data)
            returned_step_data_list = Validate_Step_Data(element_step_data)
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1],
                                                 returned_step_data_list[2], returned_step_data_list[3],
                                                 returned_step_data_list[4])
                    if Element.is_enabled():
                        action = TouchAction(driver)

                        action.press(Element).wait(100).release().press(Element).wait(100).release().perform()

                        CommonUtil.ExecLog(sModuleInfo, "Double Tapped on element successfully", 1)
                        return "passed"
                    else:
                        CommonUtil.TakeScreenShot(sModuleInfo)
                        CommonUtil.ExecLog(sModuleInfo, "Element not enabled. Unable to click.", 3)
                        return "failed"
                except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
                        exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not select/click your element.  Error: %s" % (Error_Detail),
                                       3)
                    return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to tap. %s" % Error_Detail, 3)
        return "failed"

# Long_Press_Appium_asifurrouf_fixed Long Press time

def Long_Press_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Long_Press_Appium", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
            return "failed"
        else:
            element_step_data = Get_Element_Step_Data_Appium(step_data)
            returned_step_data_list = Validate_Step_Data(element_step_data)
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1],
                                                 returned_step_data_list[2], returned_step_data_list[3],
                                                 returned_step_data_list[4])
                    if Element.is_enabled():
                        action = TouchAction(driver)

                        action.long_press(Element, 150, 10).release().perform()

                        CommonUtil.ExecLog(sModuleInfo, "Long Pressed on element successfully", 1)
                        return "passed"
                    else:
                        CommonUtil.TakeScreenShot(sModuleInfo)
                        CommonUtil.ExecLog(sModuleInfo, "Element not enabled. Unable to click.", 3)
                        return "failed"
                except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
                        exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not select/click your element.  Error: %s" % (Error_Detail),
                                       3)
                    return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to tap. %s" % Error_Detail, 3)
        return "failed"

#asifurrouf_long_press_double_tap

#Method to enter texts in a text box; step data passed on by the user
def Enter_Text_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Enter_Text_Appium", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:
            element_step_data=Get_Element_Step_Data_Appium(step_data)
            returned_step_data_list = Validate_Step_Data(element_step_data) 
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                    for each in step_data[0]:
                        if each[1]=="action":
                            text_value=each[2]
                        else:
                            continue
                    #text_value=step_data[0][len(step_data[0])-1][2]
                    Element.click()
                    Element.clear()
                    Element.send_keys(text_value)
                    Element.click()
                    CommonUtil.TakeScreenShot(sModuleInfo)
                    CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s"%text_value, 1)
                    return "passed"
                except Exception, e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()        
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                    CommonUtil.ExecLog(sModuleInfo, "Could not enter text in the desired element.  Error: %s"%(Error_Detail), 3)
                    return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find your element.  Error: %s"%(Error_Detail), 3)
        return "failed"


def Swipe_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Swipe_Appium", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:
            swipe_direction = step_data[0][0][2]
            if swipe_direction == 'down':
                CommonUtil.ExecLog(sModuleInfo,"Swiping down!",1)
                result = driver.swipe(100, 500, 100, 100, 800)
                CommonUtil.ExecLog(sModuleInfo, "Swiped the screen down successfully", 1)
                time.sleep(3)
            elif swipe_direction == 'up':
                CommonUtil.ExecLog(sModuleInfo,"Swiping up!",1)
                result = driver.swipe(100, 100, 100, 500, 800)
                CommonUtil.ExecLog(sModuleInfo, "Swiped the screen up successfully", 1)
                time.sleep(3)
            elif swipe_direction == 'left':
                CommonUtil.ExecLog(sModuleInfo,"Swiping left!",1)
                result = driver.swipe(100, 300, 500, 300, 800)
                CommonUtil.ExecLog(sModuleInfo, "Swiped the screen left successfully", 1)
                time.sleep(3)
            elif swipe_direction == 'right':
                CommonUtil.ExecLog(sModuleInfo,"Swiping right!",1)
                result = driver.swipe(500, 300, 100, 300, 800)
                CommonUtil.ExecLog(sModuleInfo, "Swiped the screen right successfully", 1)
                time.sleep(3)    
            else:
                CommonUtil.ExecLog(sModuleInfo, "Swiping was not successful", 3)
                result = "failed"

        return result
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Failed to swipe.  Error: %s"%(Error_Detail), 3)
        return "failed"


def Android_Keystroke_Key_Mapping(keystroke):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Android_Keystroke_Key_Mapping", 1)
    try:
        if keystroke == "RETURN":
            driver.keyevent(66)
        elif keystroke == "GO BACK":
            driver.back()
        elif keystroke == "SPACE":
            driver.keyevent(62)
        elif keystroke == "BACKSPACE":
            driver.keyevent(67)
        elif keystroke == "CALL":
            driver.keyevent(5)            
        elif keystroke == "END CALL":
            driver.keyevent(6)
                                     
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not press enter for your element.  Error: %s"%(Error_Detail), 3)
        return "failed"    
    

"""MINAR: PLEASE CHECK IF THIS IS POSSIBLE FOR AN iOS"""
def iOS_Keystroke_Key_Mapping(keystroke):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: iOS_Keystroke_Key_Mapping", 1)
    try:
        if keystroke == "RETURN":
            driver.keyevent(13)
        #elif keystroke == "GO BACK":
        #    driver.back()
        elif keystroke == "SPACE":
            driver.keyevent(32)
        elif keystroke == "BACKSPACE":
            driver.keyevent(8)
        elif keystroke == "CALL":
            driver.keyevent(5)            
        elif keystroke == "END CALL":
            driver.keyevent(6)
                                     
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not press enter for your element.  Error: %s"%(Error_Detail), 3)
        return "failed"   


#Method to click on element; step data passed on by the user
def Keystroke_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Keystroke_Appium", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:
            for each in step_data[0]:
                if each[1]=="action":
                    if each[0]=="iOS keystroke":
                        keystroke_value=(each[2]).upper()
                        result = iOS_Keystroke_Key_Mapping(keystroke_value)
                    elif each[0] == "Android keystroke":
                        keystroke_value=(each[2]).upper()
                        result = Android_Keystroke_Key_Mapping(keystroke_value)
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "The correct parameter for the action has not been entered. Please check for errors.", 2)
                        result = "failed"
                else:
                    continue
                
            if (result != "failed"):
                CommonUtil.TakeScreenShot(sModuleInfo)
                CommonUtil.ExecLog(sModuleInfo, "Successfully entered keystroke for the element with given parameters and values", 1)
                return "passed"
            else:
                CommonUtil.TakeScreenShot(sModuleInfo)
                CommonUtil.ExecLog(sModuleInfo, "Could not enter keystroke for the element with given parameters and values", 3)
                return "failed"
              
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not enter keystroke.  Error: %s"%(Error_Detail), 3)
        return "failed"


"""NEED TO BE CHANGED QUITE A BIT. CURRENT_PAGE WILL BE MODIFIED TO HAVE SOMETHING ELSE"""
#Validating text from an element given information regarding the expected text
def Validate_Text_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Validate_Text", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return "failed"
        else:
            for each in step_data[0]:
                if each[0] == "current_page":
                    try:
                        Element = Get_Element_Appium('tag', 'html')
                        break
                    except Exception, e:
                        errMsg = "Could not get element from the current page."
                        Exception_Info(sModuleInfo, errMsg)
                else:
                    element_step_data = Get_Element_Step_Data_Appium(step_data)
                    returned_step_data_list = Validate_Step_Data(element_step_data)
                    if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                        return "failed"
                    else:
                        try:
                            Element = Get_Element_Appium(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                            break
                        except Exception, e:
                            errMsg = "Could not get element based on the information provided."
                            Exception_Info(sModuleInfo, errMsg)            
 
            for each_step_data_item in step_data[0]:
                if each_step_data_item[1]=="action":
                    expected_text_data = each_step_data_item[2]
                    validation_type = each_step_data_item[0]
            #expected_text_data = step_data[0][len(step_data[0]) - 1][2]
            list_of_element_text = Element.text.split('\n')
            visible_list_of_element_text = []
            for each_text_item in list_of_element_text:
                if each_text_item != "":
                    visible_list_of_element_text.append(each_text_item)
             
            #if step_data[0][len(step_data[0])-1][0] == "validate partial text":
            if validation_type == "validate partial text":
                actual_text_data = visible_list_of_element_text
                CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 1)
                CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 1)
                for each_actual_text_data_item in actual_text_data:
                    if expected_text_data in each_actual_text_data_item:
                        CommonUtil.ExecLog(sModuleInfo, "The text has been validated by a partial match.", 1)
                        return "passed"
                CommonUtil.ExecLog(sModuleInfo, "Unable to validate using partial match.", 3)
                return "failed"
            #if step_data[0][len(step_data[0])-1][0] == "validate full text":
            if validation_type == "validate full text":
                actual_text_data = visible_list_of_element_text
                CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 1)
                CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 1)
                if (expected_text_data in actual_text_data):
                    CommonUtil.ExecLog(sModuleInfo, "The text has been validated by using complete match.", 1)
                    return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to validate using complete match.", 3)
                    return "failed"
             
            else:
                CommonUtil.ExecLog(sModuleInfo, "Incorrect validation type. Please check step data", 3)
                return "failed"
 
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not compare text as requested.  Error: %s" % (Error_Detail), 3)
        return "failed"
'===================== ===x=== Sequential Actions Section Ends ===x=== ======================'    
    