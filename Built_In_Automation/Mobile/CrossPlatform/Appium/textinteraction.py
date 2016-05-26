
from appium import webdriver
import os , sys, inspect
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
        driver.set_value(elem, text)
        CommonUtil.ExecLog(sModuleInfo,"Text set on element successfully",1,local_run)
        return "Passed"
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
        driver.set_value(elem, text)
        CommonUtil.ExecLog(sModuleInfo,"Text set on element successfully",1,local_run)
        return "Passed"
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
        driver.set_value(elem, text)
        CommonUtil.ExecLog(sModuleInfo,"Text set on element successfully",1,local_run)
        return "Passed"
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
        driver.set_value(elem, text)
        CommonUtil.ExecLog(sModuleInfo,"Text set on element successfully",1,local_run)
        return "Passed"
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
        driver.set_value(elem, text)
        CommonUtil.ExecLog(sModuleInfo,"Text set on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to set text on the element. %s"%Error_Detail, 3,local_run)
        return "failed"
