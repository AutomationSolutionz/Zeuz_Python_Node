# Android environment
from appium import webdriver
import os , sys, time, inspect
from Utilities import CommonUtil
from Built_In_Automation.Mobile.Android.adb_calls import adbOptions
from Built_In_Automation.Mobile.CrossPlatform.Appium import commonOptions as co
from Built_In_Automation.Mobile.CrossPlatform.Appium import clickinteraction as ci
from Built_In_Automation.Mobile.CrossPlatform.Appium import locateinteraction as li
from Built_In_Automation.Mobile.CrossPlatform.Appium import checkelement as ce
from Built_In_Automation.Mobile.CrossPlatform.Appium import textinteraction as ti
from appium.webdriver.common.touch_action import TouchAction


#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False


def launch(package_name,activity_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        CommonUtil.ExecLog(sModuleInfo,"Trying to open the app",1,local_run)
        desired_caps = {}
        desired_caps['platformName'] = 'Android'
        df = adbOptions.get_android_version()
        CommonUtil.ExecLog(sModuleInfo,df,1,local_run)
        #adbOptions.kill_adb_server()
        desired_caps['platformVersion'] = df
        df = adbOptions.get_device_model()
        CommonUtil.ExecLog(sModuleInfo,df,1,local_run)
        #adbOptions.kill_adb_server()
        desired_caps['deviceName'] = df
        desired_caps['appPackage'] = package_name
        desired_caps['appActivity'] = activity_name
        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        global driver
        CommonUtil.ExecLog(sModuleInfo,"Opened the app successfully",1,local_run)
        co.wait(driver, 10)
        co.swipe(driver)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start WebDriver. %s"%Error_Detail, 3,local_run)
        return "failed"


def close():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to close the app",1,local_run)
        driver.close_app()
        CommonUtil.ExecLog(sModuleInfo,"Closed the app successfully",1,local_run)
        driver.quit()
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to close the driver. %s"%Error_Detail, 3,local_run)
        return "failed"
    
    
def confirm_right():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to confirm the right menu options",1,local_run)
        ci.click_element_by_id(driver, "ca.bellmedia.bnngo:id/action_right_toggle")
        ce.check_element_by_id(driver, "ca.bellmedia.bnngo:id/rdo_stock")
        ci.click_element_by_id(driver, "ca.bellmedia.bnngo:id/rdo_stock")
        CommonUtil.ExecLog(sModuleInfo,"The right menu has 'Stock Lookup'",1,local_run)
        ce.check_element_by_id(driver, "ca.bellmedia.bnngo:id/rdo_twitter")
        ci.click_element_by_id(driver, "ca.bellmedia.bnngo:id/rdo_twitter")
        CommonUtil.ExecLog(sModuleInfo,"The right menu has 'Twitter'",1,local_run)
        ce.check_element_by_id(driver,"ca.bellmedia.bnngo:id/rdo_tv")
        ci.click_element_by_id(driver, "ca.bellmedia.bnngo:id/rdo_tv")
        CommonUtil.ExecLog(sModuleInfo,"The right menu has 'Live'",1,local_run)
        CommonUtil.ExecLog(sModuleInfo,"Confirmed the right menu items successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm the right menu options. %s"%Error_Detail, 3,local_run)
        return "failed"
    

def confirm_left():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        results = "failed"
        CommonUtil.ExecLog(sModuleInfo,"Trying to confirm the left menu options",1,local_run)
        co.wait(driver, 10)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on left menu",1,local_run)
        ci.click_element_by_id(driver, "android:id/home")
        CommonUtil.ExecLog(sModuleInfo,"Trying to match the option - 'Home'...",1,local_run)
        results = ce.check_element_by_name(driver, 'Home')
        #go_back()
        CommonUtil.ExecLog(sModuleInfo,"Trying to match the option - 'News'...",1,local_run)
        results = ce.check_element_by_name(driver, 'News')
        #go_back()
        CommonUtil.ExecLog(sModuleInfo,"Trying to match the option - 'Markets'...",1,local_run)
        results = ce.check_element_by_name(driver, 'Markets')
        #go_back()
        CommonUtil.ExecLog(sModuleInfo,"Trying to match the option - 'Videos'...",1,local_run)
        results = ce.check_element_by_name(driver, 'Videos')
        #go_back()
        CommonUtil.ExecLog(sModuleInfo,"Trying to match the option - 'Shows'...",1,local_run)
        results = ce.check_element_by_name(driver, 'Shows')
        #go_back()
        CommonUtil.ExecLog(sModuleInfo,"Trying to match the option - 'Blogs'...",1,local_run)
        results = ce.check_element_by_name(driver, 'Blogs')
        #go_back()
        CommonUtil.ExecLog(sModuleInfo,"Trying to match the option - 'Top Picks'...",1,local_run)
        results = ce.check_element_by_name(driver, 'Top Picks')
        #go_back()
        if results=="Passed":
            CommonUtil.ExecLog(sModuleInfo,"Confirmed the left menu items successfully",1,local_run)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Left menu items are not confirmed.",3,local_run)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm the right menu options. %s"%Error_Detail, 3,local_run)
        return "failed"
    
    
def go_left(section_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to go to the left menu section: %s"%section_name,1,local_run)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on left menu",1,local_run)
        ci.click_element_by_id(driver, "android:id/home")
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on the section: %s"%section_name,1,local_run)
        results = ci.click_element_by_name(driver, section_name)
        if results=="Passed":
            CommonUtil.ExecLog(sModuleInfo,"Clicked on the left menu section %s"%section_name,1,local_run)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Could not click on the section %s"%section_name,3,local_run)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go left. %s"%Error_Detail, 3,local_run)
        return "failed"
    
def go_sub(section_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to go to the left sub-menu section: %s"%section_name,1,local_run)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on the sub section: %s"%section_name,1,local_run)
        results = ci.click_element_by_name(driver, section_name)
        if results=="Passed":
            CommonUtil.ExecLog(sModuleInfo,"Clicked on the left menu section %s"%section_name,1,local_run)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Could not click on the section %s"%section_name,3,local_run)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go sub section. %s"%Error_Detail, 3,local_run)
        return "failed"    

def check_section(section_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to match the section: %s"%section_name,1,local_run)
        elem = li.locate_element_by_id(driver, "android:id/action_bar_title")
        found = ce.check_element_by_name(driver, section_name)
        if found == "Passed" and elem.text == section_name:
            co.swipe(driver)
            CommonUtil.ExecLog(sModuleInfo,"Opened the section - %s successfully"%section_name,1,local_run)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Opened section does not match with %s."%section_name,3,local_run)
            return "failed"
        
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to check the opened section. %s"%Error_Detail, 3,local_run)
        return "failed"

    
def confirm_submenu(section_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to check sub menu for the section: %s"%section_name,1,local_run)
        CommonUtil.ExecLog(sModuleInfo,"Trying to check section - %s on left sub menu"%section_name,1,local_run)
        res = ce.check_element_by_id(driver, "ca.bellmedia.bnngo:id/txt_title")
        #check_element_by_id("ca.bellmedia.bnngo:id/list")
        res2 = ce.check_element_by_id(driver, "ca.bellmedia.bnngo:id/btn_back")
        if res=="Passed" and res2=="Passed":
            CommonUtil.ExecLog(sModuleInfo,"Sub-menu for the section - %s confirmed successfully"%section_name,1,local_run)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Sub-menu for the section - %s was not found"%section_name,3,local_run)
            return "failed"
        
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to find the sub-menu. %s"%Error_Detail, 3,local_run)
        return "failed"
    
    
def confirm_submenu_items(submenus):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to check sub menu items...",1,local_run)
        items = submenus.split(",")
        for each in items:
            CommonUtil.ExecLog(sModuleInfo,"Trying to check sub menu - %s ..."%each.strip(),1,local_run)
            result = ce.check_element_by_name(driver, each)
            if result == "Passed":
                CommonUtil.ExecLog(sModuleInfo,"Sub-menu item %s confirmed successfully"%each.strip(),1,local_run)
            else:
                CommonUtil.ExecLog(sModuleInfo,"Sub-menu item %s is not confirmed"%each.strip(),3,local_run)
        CommonUtil.ExecLog(sModuleInfo,"Sub-menu items checked successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to find the sub-menu. %s"%Error_Detail, 3,local_run)
        return "failed"
    
    
def confirm_player():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to confirm the video playing...",1,local_run)
        co.wait(driver, 5)
        ci.click_element_by_id(driver, "ca.bellmedia.bnngo:id/img_picture")
        co.wait(driver, 2)
        res = ce.check_element_by_id(driver, "ca.bellmedia.bnngo:id/pbBufferingSpinner")
        if res=="Passed":
            CommonUtil.ExecLog(sModuleInfo,"Confirmed the video player opening successfully",1,local_run)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Video player did not open.",3,local_run)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm the right menu options. %s"%Error_Detail, 3,local_run)
        return "failed"
    
    
    