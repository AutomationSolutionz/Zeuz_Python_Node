
from appium import webdriver
import os, sys, inspect
from Utilities import CommonUtil
from Built_In_Automation.Mobile.CrossPlatform.Appium import locateinteraction as li


#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False


def set_text_by_id(driver, _id, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by id: %s"%_id,1,local_run)
        elem = li.locate_element_by_id(driver, _id)
        if elem.is_displayed():
            elem.click()
            driver.hide_keyboard()
            #elem.set_value(text)
            #driver.set_value(elem, text)
            elem.send_keys(text)
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1, local_run)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3, local_run)
            return "failed"
        #driver.set_value(elem, text)

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s"%Error_Detail, 3,local_run)
        return "failed"


def set_text_by_name(driver, _name, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by name: %s"%_name,1,local_run)
        elem = li.locate_element_by_name(driver, _name)
        if elem.is_displayed():
            elem.click()
            driver.hide_keyboard()
            elem.send_keys(text)
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1, local_run)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3, local_run)
            return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s"%Error_Detail, 3,local_run)
        return "failed"


def set_text_by_class_name(driver, _class, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by class: %s"%_class,1,local_run)
        elem = li.locate_element_by_class_name(driver, _class)
        if elem.is_displayed():
            elem.click()
            driver.hide_keyboard()
            elem.send_keys(text)
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1, local_run)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3, local_run)
            return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s"%Error_Detail, 3,local_run)
        return "failed"


def set_text_by_xpath(driver, _classpath, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by xpath: %s"%_classpath,1,local_run)
        elem = li.locate_element_by_xpath(driver, _classpath)
        if elem.is_displayed():
            elem.click()
            driver.hide_keyboard()
            elem.send_keys(text)
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1, local_run)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3, local_run)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s"%Error_Detail, 3,local_run)
        return "failed"


def set_text_by_accessibility_id(driver, _id, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to set text on element by accessibility id: %s"%_id,1,local_run)
        elem = li.locate_element_by_accessibility_id(driver, _id)
        if elem.is_displayed():
            elem.click()
            driver.hide_keyboard()
            elem.send_keys(text)
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1, local_run)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3, local_run)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s" % Error_Detail, 3, local_run)
        return "failed"


def set_text_by_android_uiautomator_text(driver, _text, text_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to click on element by android uiautomator text: %s" % _text, 1, local_run)
        elem = li.locate_element_by_android_uiautomator_text(driver, _text)
        if elem.is_displayed():
            elem.click()
            driver.hide_keyboard()
            elem.send_keys(text_value)
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1, local_run)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3, local_run)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s" % Error_Detail, 3, local_run)
        return "failed"


def set_text_by_android_uiautomator_description(driver, _description, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,
                           "Trying to click on element by android uiautomator description: %s" % _description, 1,
                           local_run)
        elem = li.locate_element_by_android_uiautomator_description(driver, _description)
        if elem.is_displayed():
            elem.click()
            driver.hide_keyboard()
            elem.send_keys(text)
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1, local_run)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3, local_run)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s" % Error_Detail, 3, local_run)
        return "failed"


def set_text_by_ios_uiautomation(driver, _description, text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,
                           "Trying to click on element by android uiautomator description: %s" % _description, 1,
                           local_run)
        elem = li.locate_element_by_ios_uiautomation(driver, _description)
        if elem.is_displayed():
            elem.click()
            driver.hide_keyboard()
            elem.send_keys(text)
            CommonUtil.ExecLog(sModuleInfo, "Text set on element successfully", 1, local_run)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to set text. The element is hidden.", 3, local_run)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s" % Error_Detail, 3, local_run)
        return "failed"

