'''
Created on May 15, 2016

@author: RizDesktop
'''


import os,sys
import inspect
from Utilities import CommonUtil
from Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions as bf

#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False


def launch_application(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Launch application",1,local_run)
        app_name=step_data[0][0][2]
        package_name=step_data[0][1][2]
        activity_name=step_data[0][2][2]
        sTestStepReturnStatus = bf.launch_and_start_driver(package_name,activity_name)
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Launch application",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to launch app: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"


def close_application(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Close Application",1,local_run)
        sTestStepReturnStatus = bf.close()
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Close Application",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to close app: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
    
    
def install_application(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Install application",1,local_run)
        app_location=step_data[0][0][1]
        package_name=step_data[0][1][1]
        activity_name=step_data[0][2][1]
        sTestStepReturnStatus = bf.install(app_location, package_name, activity_name)
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Install application",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to install app: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
    
    
def remove_application(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Launch application",1,local_run)
        app_package=step_data[0][0][1]
        sTestStepReturnStatus = bf.remove(app_package)
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Launch application",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to remove app: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"


def click_element_appium(dependency, run_time_params, step_data, file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Click Element", 1, local_run)
        sTestStepReturnStatus = bf.Click_Element(step_data)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Click Element", 1, local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click element: Error:%s" % (Error_Detail), 3, local_run)
        temp_q.put("Failed")
        return "failed"


def enter_text_appium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Enter Text",1,local_run)
        sTestStepReturnStatus=bf.Enter_Text_In_Text_Box(step_data)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Enter Text",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to enter text: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"


def sequential_actions_appium(dependency, run_time_params, step_data, file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Sequential Actions", 1, local_run)
        sTestStepReturnStatus = bf.Sequential_Actions(step_data)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Sequential Actions", 1, local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to run sequential actions: Error:%s" % (Error_Detail), 3, local_run)
        temp_q.put("Failed")
        return "failed"

    
    