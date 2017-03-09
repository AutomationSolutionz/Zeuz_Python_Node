'''
Created on May 16, 2016

@author: hossa
'''
# Android environment
import os , sys, inspect
from Utilities import CommonUtil
from Built_In_Automation.Mobile.CrossPlatform.Appium import locateinteraction as li
from Built_In_Automation.Mobile.CrossPlatform.Appium import clickinteraction as ci
from Built_In_Automation.Mobile.CrossPlatform.Appium import checkelement as ce




def confirm_right():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to confirm the right menu options",1)
        ci.click_element_by_id("ca.bellmedia.bnngo:id/action_right_toggle")
        ce.check_element_by_id("ca.bellmedia.bnngo:id/rdo_stock")
        CommonUtil.ExecLog(sModuleInfo,"The right menu has 'Stock Lookup'",1)
        ce.check_element_by_id("ca.bellmedia.bnngo:id/rdo_twitter")
        CommonUtil.ExecLog(sModuleInfo,"The right menu has 'Twitter'",1)
        ce.check_element_by_id("ca.bellmedia.bnngo:id/rdo_tv")
        CommonUtil.ExecLog(sModuleInfo,"The right menu has 'Live'",1)
        CommonUtil.ExecLog(sModuleInfo,"Confirmed the right menu items successfully",1)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm the right menu options. %s"%Error_Detail, 3)
        return "failed"

def go_left(section_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to go to the left menu section: %s"%section_name,1)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on left menu",1)
        ci.click_element_by_id("android:id/home")
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on the section: %s"%section_name,1)
        ci.click_element_by_name(section_name)
        CommonUtil.ExecLog(sModuleInfo,"Clicked on the left menu section",1)
        CommonUtil.ExecLog(sModuleInfo,"Trying to match the section: %s"%section_name,1)
        elem = li.locate_element_by_id("android:id/action_bar_title")
        if elem.text == section_name:
            CommonUtil.ExecLog(sModuleInfo,"Opened the section - %s successfully"%section_name,1)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm the right menu options. %s"%Error_Detail, 3)
        return "failed"

