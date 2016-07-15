'''
Created on May 15, 2016

@author: AutomationSolutionz Inc.
'''

import os,sys
import inspect
from Utilities import CommonUtil
from Built_In_Automation.Web.SeleniumAutomation import BuiltInFunctions
#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
local_run = False
#local_run = False

#for api to work, driver needs run_params and dic is single 
#def open_browser(dependency,step_data,file_attachment,temp_q):
def open_browser(dependency,run_params,step_data,file_attachment,temp_q):
    #this function takes the dependency Browser and passes the browser type you selected during run time
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Open Browser",1,local_run)
        #browser_name=dependency['dependency']['Browser']
        browser_name=dependency['Browser']
        stepReturn=BuiltInFunctions.Open_Browser(browser_name)
        CommonUtil.ExecLog(sModuleInfo,"started the browser",1,local_run)
        temp_q.put(stepReturn)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Open Browser",1,local_run)
        return stepReturn
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start browser: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"


def close_browser(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Close Browser",1,local_run)
        sTestStepReturnStatus=BuiltInFunctions.Tear_Down()
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Close Browser",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to close browser: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"


def go_to_webpage(dependency,run_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Go To Webpage",1,local_run)
        first_data_set=step_data[0]
        web_link=first_data_set[0][1]
        web_title = first_data_set[0][2]
        sTestStepReturnStatus=BuiltInFunctions.Go_To_Link(web_link, web_title)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Go To Webpage",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go to webpage: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"

def login_to_web_app(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Login To Web App",1,local_run)
        user_name=step_data[0][0][1]
        password = step_data[0][1][1]
        user_element = step_data[0][2][1]
        password_element = step_data[0][3][1]
        button_to_click =step_data[0][4][1]
        
        sTestStepReturnStatus=BuiltInFunctions.Login_To_Application(user_name, password, user_element, password_element, button_to_click)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Login To Web App",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to login to web app: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
    
    
def enter_text(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Enter Text",1,local_run)
        sTestStepReturnStatus=BuiltInFunctions.Enter_Text_In_Text_Box(step_data)
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
    
def click_element(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Click Element",1,local_run)
        sTestStepReturnStatus=BuiltInFunctions.Click_Element(step_data)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Click Element",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click element: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
    