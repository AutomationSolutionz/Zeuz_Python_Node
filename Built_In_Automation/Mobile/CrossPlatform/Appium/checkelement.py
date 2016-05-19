
import os , sys, inspect
from Utilities import CommonUtil
from Built_In_Automation.Mobile.CrossPlatform.Appium import locateinteraction as li

#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False

def check_element_by_id(driver, _id, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to find element by id: %s"%_id,1,local_run)
        elems = li.locate_elements_by_id(driver, _id, parent)
        if not elems:
            CommonUtil.ExecLog(sModuleInfo,"Element by id : %s not found"%_id,3,local_run)
            return "failed"
        elif elems[0].is_displayed():
            #click_element_by_id(_id)
            CommonUtil.ExecLog(sModuleInfo,"Element by id : %s found"%_id,1,local_run)
            return "Passed"
        
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to check the element. %s"%Error_Detail, 3,local_run)
        return "failed"
    
def check_element_by_name(driver, _name, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to find element by name: %s"%_name,1,local_run)
        elem = li.locate_element_by_name(driver, _name, parent)
        if not elem:
            CommonUtil.ExecLog(sModuleInfo,"Element by name : %s not found"%_name,3,local_run)
            return "failed"
        elif elem.is_displayed():
            #click_element_by_name(_name)
            CommonUtil.ExecLog(sModuleInfo,"Element by name : %s found"%_name,1,local_run)
            return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to check the element. %s"%Error_Detail, 3,local_run)
        return "failed"
    