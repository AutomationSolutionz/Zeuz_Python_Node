
import os , sys, inspect
from Utilities import CommonUtil
from appium import webdriver
from Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions as bf

#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False

#Get the initiated global driver
global driver
driver = bf.get_driver()



def locate_element_by_id(_id, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by id: %s"%_id,1,local_run)
        if isinstance(parent,bool) == True:
            elem = driver.find_element_by_id(_id)
        else:
            elem=parent.find_element_by_id(_id)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3,local_run)

def locate_elements_by_id(_id, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate elements by id: %s"%_id,1,local_run)
        if isinstance(parent,bool) == True:
            elems = driver.find_elements_by_id(_id)
        else:
            elems=parent.find_elements_by_id(_id)
        return elems
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate elements. %s"%Error_Detail, 3,local_run)

    
def locate_element_by_name(_name, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by name: %s"%_name,1,local_run)
        if isinstance(parent,bool) == True:
            elem = driver.find_element_by_name(_name)
        else:
            elem=parent.find_element_by_name(_name)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3,local_run)
    
    
def locate_element_by_class_name(_class, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by class: %s"%_class,1,local_run)
        if isinstance(parent,bool) == True:
            elem = driver.find_element_by_class_name(_class)
        else:
            elem=parent.find_element_by_class_name(_class)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3,local_run)
    
    
def locate_element_by_xpath(_classpath, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by xpath: %s"%_classpath,1,local_run)
        if isinstance(parent,bool) == True:
            elem = driver.find_element_by_xpath(_classpath)
        else:
            elem=parent.find_element_by_xpath(_classpath)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3,local_run)
    
def locate_element_by_accessibility_id(_id, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by accessibility id: %s"%_id,1,local_run)
        if isinstance(parent,bool) == True:
            elem = driver.find_element_by_accessibility_id(_id)
        else:
            elem=parent.find_element_by_accessibility_id(_id)
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3,local_run)


def locate_element_by_android_uiautomator_text(_text, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by android uiautomator text: %s"%_text,1,local_run)
        if isinstance(parent,bool) == True:
            elem = driver.find_element_by_android_uiautomator('new UiSelector().text('+_text+')')
        else:
            elem=parent.find_element_by_android_uiautomator('new UiSelector().text('+_text+')')
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3,local_run)


def locate_element_by_android_uiautomator_description(_description, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to locate element by android uiautomator description: %s"%_description,1,local_run)
        if isinstance(parent,bool) == True:
            elem = driver.find_element_by_android_uiautomator('new UiSelector().description('+_description+')')
        else:
            elem=parent.find_element_by_android_uiautomator('new UiSelector().description('+_description+')')
        return elem
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate the element. %s"%Error_Detail, 3,local_run)
