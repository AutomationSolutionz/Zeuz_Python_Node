'''
Created on May 16, 2016

@author: hossa
'''
# Android environment
from lxml.html.diff import tag_token
from appium import webdriver
import os , sys, time, inspect
from Utilities import CommonUtil
from Built_In_Automation.Mobile.Android.adb_calls import adbOptions
from Built_In_Automation.Web.SeleniumAutomation import _locateInteraction
from Built_In_Automation.Web.SeleniumAutomation import _clickInteraction
from appium.webdriver.common.touch_action import TouchAction
from django.test.html import Element

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
        time.sleep(2)
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

def go_back():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to go back",1,local_run)
        driver.back()
        CommonUtil.ExecLog(sModuleInfo,"Went back successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go back. %s"%Error_Detail, 3,local_run)
        return "failed"

def click_element_by_id(_id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to find element by id: %s"%_id,1,local_run)
        elem = driver.find_element_by_id(_id)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by id: %s"%_id,1,local_run)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"

def click_element_by_name(_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to find element by name: %s"%_name,1,local_run)
        elem = driver.find_element_by_name(_name)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by name: %s"%_name,1,local_run)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"

def click_element_by_class_name(_class):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to find element by class: %s"%_class,1,local_run)
        elem = driver.find_element_by_class_name(_class)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by class: %s"%_class,1,local_run)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"

def click_element_by_xpath(_classpath):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to find element by xpath: %s"%_classpath,1,local_run)
        elem = driver.find_element_by_xpath(_classpath)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by class: %s"%_classpath,1,local_run)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"

def click_element_by_accessibility_id(_id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to find element by accessibility id: %s"%_id,1,local_run)
        elem = driver.find_element_by_accessibility_id(_id)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by accessibility id: %s"%_id,1,local_run)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"

def confirm_right():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to confirm the right menu options",1,local_run)
        click_element_by_id("ca.bellmedia.bnngo:id/action_right_toggle")
        check_element_by_id("ca.bellmedia.bnngo:id/rdo_stock")
        CommonUtil.ExecLog(sModuleInfo,"The right menu has 'Stock Lookup'",1,local_run)
        check_element_by_id("ca.bellmedia.bnngo:id/rdo_twitter")
        CommonUtil.ExecLog(sModuleInfo,"The right menu has 'Twitter'",1,local_run)
        check_element_by_id("ca.bellmedia.bnngo:id/rdo_tv")
        CommonUtil.ExecLog(sModuleInfo,"The right menu has 'Live'",1,local_run)
        CommonUtil.ExecLog(sModuleInfo,"Confirmed the right menu items successfully",1,local_run)
        return "Passed"
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
        click_element_by_id("android:id/home")
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on the section: %s"%section_name,1,local_run)
        click_element_by_name(section_name)
        CommonUtil.ExecLog(sModuleInfo,"Clicked on the left menu section",1,local_run)
        CommonUtil.ExecLog(sModuleInfo,"Trying to match the section: %s"%section_name,1,local_run)
        elem = driver.find_element_by_id("android:id/action_bar_title")
        if elem.text == section_name:
            CommonUtil.ExecLog(sModuleInfo,"Opened the section - %s successfully"%section_name,1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm the right menu options. %s"%Error_Detail, 3,local_run)
        return "failed"

def check_element_by_id(_id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to find element by id: %s"%_id,1,local_run)
        elem = driver.find_elements_by_id(_id)
        if not elem:
            CommonUtil.ExecLog(sModuleInfo,"Element by id : %s not found"%_id,1,local_run)
            
        elif elem[0].is_displayed():
            click_element_by_id(_id)
            CommonUtil.ExecLog(sModuleInfo,"Element by id : %s found"%_id,1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"
