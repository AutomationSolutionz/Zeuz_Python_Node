'''
Created on May 15, 2016

@author: AutomationSolutionz Inc.
'''

import os,sys
import inspect
from Utilities import CommonUtil
from Built_In_Automation.Web.SeleniumAutomation import BuiltInFunctions as Selenium_Built_In
#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
local_run = False
#local_run = False

#for api to work, driver needs run_params and dic is single 
#def open_browser(dependency,step_data,file_attachment,temp_q):
def open_browser(dependency,run_params,step_data,file_attachment,temp_q):
    #this function takes the dependency Browser and passes the browser type you selected during run time
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Open Browser Selenium",1,local_run)
        #browser_name=dependency['dependency']['Browser']
        browser_name=dependency['Browser']
        stepReturn=Selenium_Built_In.Open_Browser(browser_name)
        CommonUtil.ExecLog(sModuleInfo,"started the browser",1,local_run)
        temp_q.put(stepReturn)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Open Browser",1,local_run)
        return stepReturn
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start browser Selenium:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"


def tear_down_close_browser(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Close Browser Selenium",1,local_run)
        sTestStepReturnStatus=Selenium_Built_In.Tear_Down()
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Close Browser Selenium",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to close browser Selenium:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"


def go_to_webpage(dependency,run_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Go To Webpage Selenium",1,local_run)
#         first_data_set=step_data[0]
#         web_link=first_data_set[0][1]
#         web_title = first_data_set[0][2]
#         sTestStepReturnStatus=Selenium_Built_In.Go_To_Link(web_link, web_title)
        first_data_set=step_data[0]
        web_link=first_data_set[0][2]
        #web_title = first_data_set[0][2]
        sTestStepReturnStatus=Selenium_Built_In.Go_To_Link(web_link)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Go To Webpage Selenium",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go to webpage Selenium:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"


def enter_text_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Enter Text Selenium",1,local_run)
        sTestStepReturnStatus=Selenium_Built_In.Enter_Text_In_Text_Box(step_data)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Enter Text Selenium",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to enter text Selenium:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
    
def click_element_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Click Element Selenium",1,local_run)
        sTestStepReturnStatus=Selenium_Built_In.Click_Element(step_data)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Click Element Selenium",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click element Selenium:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
    
def sequential_actions_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Sequential Actions Selenium",1,local_run)
        sTestStepReturnStatus=Selenium_Built_In.Sequential_Actions(step_data)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Sequential Actions Selenium",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click element Selenium: %s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"

def keystroke_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Keystroke_For_Element Selenium",1,local_run)
        sTestStepReturnStatus=Selenium_Built_In.Keystroke_For_Element(step_data)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Keystroke_For_Element Selenium",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to send keystroke:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"  
'======'
def hover_over_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Hover_Over_Element Selenium",1,local_run)
        sTestStepReturnStatus=Selenium_Built_In.Hover_Over_Element(step_data)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Hover_Over_Element Selenium",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to Hover Over Element Selenium:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"     

def wait_for_element_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Wait for Element to appear Selenium",1,local_run)
        sTestStepReturnStatus=Selenium_Built_In.Wait_For_New_Element(step_data)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Wait for Element to appear Selenium",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Couldn't find element Selenium:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"  

def validate_text_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Validate Text Selenium",1,local_run)
        sTestStepReturnStatus=Selenium_Built_In.Validate_Text(step_data)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Validate Text Selenium",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to validate text Selenium:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"  

def validate_table_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Validate Table",1,local_run)
        sTestStepReturnStatus=Selenium_Built_In.Validate_Table(step_data)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Validate Table",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to Validate Table:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"  

def tear_down_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Tear Down Selenium",1,local_run)
        sTestStepReturnStatus=Selenium_Built_In.Tear_Down(step_data)
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Tear Down Selenium",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to Tear Down Selenium:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"  
