'''
Created on May 15, 2016

@author: RizDesktop
'''


import os,sys
import inspect
from Utilities import CommonUtil
from Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions as bf

passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True',True,1,'1','Success','success','SUCCESS']
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE',False,0,'0']



def launch_application(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Launch application",1)
        app_name=step_data[0][0][2]
        package_name=step_data[0][1][2]
        activity_name=step_data[0][2][2]
        sTestStepReturnStatus = bf.launch_and_start_driver(package_name,activity_name)


        if   sTestStepReturnStatus in passed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Successfully Launched Application", 1)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Launch Application", 1)
             return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Unable to launch application", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Launch Application", 1)
             return sTestStepReturnStatus

        else:
             CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
             temp_q.put("failed")
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Launch Application", 1)
             return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to launch app: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"


def close_application(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Close Application",1)
        sTestStepReturnStatus = bf.close()


        if sTestStepReturnStatus in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Successfully Closed Application", 1)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Close Application", 1)
            return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Unable to close application", 3)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Close Application", 1)
            return sTestStepReturnStatus

        else:
            CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
            temp_q.put("failed")
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Close Application", 1)
            return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to close app: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"
    
    
def install_application(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Install application",1)
        app_location=step_data[0][0][1]
        package_name=step_data[0][1][1]
        activity_name=step_data[0][2][1]
        sTestStepReturnStatus = bf.install(app_location, package_name, activity_name)

        if sTestStepReturnStatus in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Successfully Installed Application", 1)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Install Application", 1)
            return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Unable to Install application", 3)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Install Application", 1)
            return sTestStepReturnStatus

        else:
            CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
            temp_q.put("failed")
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Install Application", 1)
            return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to install app: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"
    
    
def remove_application(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Remove application",1)
        app_package=step_data[0][0][1]
        sTestStepReturnStatus = bf.remove(app_package)


        if sTestStepReturnStatus in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Successfully Removed Application", 1)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Remove Application", 1)
            return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Unable to remove application", 3)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Remove Application", 1)
            return sTestStepReturnStatus

        else:
            CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
            temp_q.put("failed")
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Remove Application", 1)
            return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to remove app: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"


def click_element_appium(dependency, run_time_params, step_data, file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Click Element", 1)
        element_parameter = step_data[0][0][0]
        element_value = step_data[0][0][2]
        sTestStepReturnStatus = bf.Click_Element(element_parameter, element_value)

        if sTestStepReturnStatus in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Successfully Clicked Element Appium", 1)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Click Element Appium", 1)
            return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Unable to click element appium", 3)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Click element appium", 1)
            return sTestStepReturnStatus

        else:
            CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
            temp_q.put("failed")
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Click element appium", 1)
            return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click element: Error:%s" % (Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"


def enter_text_appium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Enter Text",1)
        element_parameter = step_data[0][0][0]
        element_value = step_data[0][0][2]
        text_value = step_data[0][1][2]
        sTestStepReturnStatus=bf.Set_Text(element_parameter, element_value, text_value)

        if sTestStepReturnStatus in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Successfully entered text appium", 1)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Enter text appium", 1)
            return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Unable to enter text appium", 3)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Enter text appium", 1)
            return sTestStepReturnStatus

        else:
            CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
            temp_q.put("failed")
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Enter text appium", 1)
            return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to enter text appium: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"


def sequential_actions_appium(dependency, run_time_params, step_data, file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Sequential Actions", 1)
        sTestStepReturnStatus = bf.Sequential_Actions(step_data)

        if sTestStepReturnStatus in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Successfully run sequential actions appium", 1)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Sequential actions appium", 1)
            return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Unable to run sequential actions appium", 3)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Sequential Actions Appium", 1)
            return sTestStepReturnStatus

        else:
            CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
            temp_q.put("failed")
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Sequential Action Appium", 1)
            return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to run sequential actions: Error:%s" % (Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"

    
    