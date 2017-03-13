'''
Created on May 15, 2016

@author: AutomationSolutionz Inc.
'''

import os,sys
import inspect
from Utilities import CommonUtil
from Built_In_Automation.Web.Selenium import BuiltInFunctions as Selenium_Built_In

# passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True',True,1,'1','Success','success','SUCCESS']
# failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE',False,0,'0']

#for api to work, driver needs run_params and dic is single 
#def open_browser(dependency,step_data,file_attachment,temp_q):

def open_browser(dependency,run_params,step_data,file_attachment,temp_q):
    #this function takes the dependency Browser and passes the browser type you selected during run time
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Open Browser Selenium",1)
        #browser_name=dependency['dependency']['Browser']
#         try:
#             browser_name=dependency['Browser']
#         except Exception, e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#             Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
#             CommonUtil.ExecLog(sModuleInfo, "Dependency not set for browser. Please set the Apply Filter value to YES. Error: %s" %( Error_Detail), 3)
#             temp_q.put("failed")
#             return "failed"

        sTestStepReturnStatus = Selenium_Built_In.Open_Browser(dependency)
        
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
        
        
#         if sTestStepReturnStatus in passed_tag_list:
#             CommonUtil.ExecLog(sModuleInfo,"Successfully started the browser",1)
#             temp_q.put(sTestStepReturnStatus)
#             CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Open Browser",1)
#             return sTestStepReturnStatus
# 
#         elif sTestStepReturnStatus in failed_tag_list:
#             CommonUtil.ExecLog(sModuleInfo,"Failed to start the browser",3)
#             temp_q.put(sTestStepReturnStatus)
#             CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Open Browser",1)
#             return sTestStepReturnStatus
# 
#         else:
#             CommonUtil.ExecLog(sModuleInfo,"Step return type unknown: %s" %(sTestStepReturnStatus),3)
#             temp_q.put("failed")
#             CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Open Browser",1)
#             return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start browser Selenium:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"

# def tear_down_close_browser(dependency,run_time_params,step_data,file_attachment,temp_q):
#     sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
#     try:
#         CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Close Browser Selenium",1)
#         sTestStepReturnStatus=Selenium_Built_In.Tear_Down()
#         print sTestStepReturnStatus
#         temp_q.put(sTestStepReturnStatus)
#         CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Close Browser Selenium",1)
#         return sTestStepReturnStatus
#     except Exception, e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
#         CommonUtil.ExecLog(sModuleInfo, "Unable to close browser Selenium:%s" %( Error_Detail), 3)
#         temp_q.put("Failed")
#         return "failed"

def go_to_webpage(dependency,run_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Go To Webpage Selenium",1)
#         first_data_set=step_data[0]
#         web_link=first_data_set[0][1]
#         web_title = first_data_set[0][2]
#         sTestStepReturnStatus=Selenium_Built_In.Go_To_Link(web_link, web_title)
#         first_data_set=step_data[0]
#         web_link=first_data_set[0][2]
        #web_title = first_data_set[0][2]
        sTestStepReturnStatus=Selenium_Built_In.Go_To_Link(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
        
#         if sTestStepReturnStatus in passed_tag_list:
#             CommonUtil.ExecLog(sModuleInfo, "Successfully went to webpage", 1)
#             temp_q.put(sTestStepReturnStatus)
#             CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Go To Webpage Selenium",1)
#             return sTestStepReturnStatus
#         elif sTestStepReturnStatus in failed_tag_list:
#             CommonUtil.ExecLog(sModuleInfo, "Unable to go to webpage", 3)
#             temp_q.put(sTestStepReturnStatus)
#             CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Go To Webpage Selenium",1)
#             return sTestStepReturnStatus
#         else:
#             CommonUtil.ExecLog(sModuleInfo,"Step return type unknown: %s" %(sTestStepReturnStatus), 3)
#             temp_q.put("failed")
#             CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Go To Webpage Selenium",1)
#             return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go to webpage Selenium:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"

def enter_text_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Enter Text Selenium",1)
        sTestStepReturnStatus=Selenium_Built_In.Enter_Text_In_Text_Box(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
# 
#         if sTestStepReturnStatus in passed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Successfully entered text", 1)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Enter text selenium", 1)
#              return sTestStepReturnStatus
# 
#         elif sTestStepReturnStatus in failed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Unable to enter text", 3)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Enter text selenium", 1)
#              return sTestStepReturnStatus
# 
#         else:
#              CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
#              temp_q.put("failed")
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Enter text selenium", 1)
#              return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to enter text Selenium:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"

def keystroke_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Keystroke_For_Element Selenium",1)
        sTestStepReturnStatus=Selenium_Built_In.Keystroke_For_Element(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    
#         if sTestStepReturnStatus in passed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Successfully sent Keystroke", 1)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Keystroke for element selenium", 1)
#              return sTestStepReturnStatus
# 
#         elif sTestStepReturnStatus in failed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Unable to send keystroke", 3)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Keystroke for element selenium", 1)
#              return sTestStepReturnStatus
# 
#         else:
#              CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
#              temp_q.put("failed")
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Keystroke for element selenium", 1)
#              return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to send keystroke:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"  
    
def click_element_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Click Element Selenium",1)
        sTestStepReturnStatus=Selenium_Built_In.Click_Element(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)

#         if sTestStepReturnStatus in passed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Successfully Clicked Element", 1)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Click element selenium", 1)
#              return sTestStepReturnStatus
# 
#         elif sTestStepReturnStatus in failed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Unable to click element", 3)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Click element selenium", 1)
#              return sTestStepReturnStatus
# 
#         else:
#              CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
#              temp_q.put("failed")
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Click element selenium", 1)
#              return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click element Selenium:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"

def hover_over_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Hover_Over_Element Selenium",1)
        sTestStepReturnStatus=Selenium_Built_In.Hover_Over_Element(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)

#         if sTestStepReturnStatus in passed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Successfully Hover Over Element Selenium", 1)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Hover Over Element Selenium", 1)
#              return sTestStepReturnStatus
# 
#         elif sTestStepReturnStatus in failed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Unable to Hover Over Element Selenium", 3)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Hover Over Element Selenium", 1)
#              return sTestStepReturnStatus
# 
#         else:
#              CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
#              temp_q.put("failed")
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Hover Over element selenium", 1)
#              return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to Hover Over Element Selenium:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"     

def wait_for_element_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Wait for Element to appear Selenium",1)
        sTestStepReturnStatus=Selenium_Built_In.Wait_For_New_Element(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
    
#         if sTestStepReturnStatus in passed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Successfully waited for element to appear", 1)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Wait for element selenium", 1)
#              return sTestStepReturnStatus
# 
#         elif sTestStepReturnStatus in failed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Unable to wait for element selenium", 3)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Wait for element selenium", 1)
#              return sTestStepReturnStatus
# 
#         else:
#              CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
#              temp_q.put("failed")
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Wait for element selenium", 1)
#              return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Couldn't find element Selenium:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"  

def validate_text_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Validate Text Selenium",1)
        sTestStepReturnStatus=Selenium_Built_In.Validate_Text(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)

#         if sTestStepReturnStatus in passed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Successfully Validated Text Selenium", 1)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Validate Text Selenium", 1)
#              return sTestStepReturnStatus
# 
#         elif sTestStepReturnStatus in failed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Unable to validate text selenium", 3)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Validate Text Selenium", 1)
#              return sTestStepReturnStatus
# 
#         else:
#              CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
#              temp_q.put("failed")
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Validate Text Selenium", 1)
#              return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to validate text Selenium:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"  

def sleep_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Sleep Selenium",1)
        sTestStepReturnStatus=Selenium_Built_In.Sleep(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)

#         if sTestStepReturnStatus in passed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Successfully sleep mode selenium", 1)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - sleep selenium", 1)
#              return sTestStepReturnStatus
# 
#         elif sTestStepReturnStatus in failed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Unable to go to sleep mode", 3)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - sleep selenium", 1)
#              return sTestStepReturnStatus
# 
#         else:
#              CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
#              temp_q.put("failed")
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - sleep selenium", 1)
#              return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go to sleep mode:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"  

def scroll_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Scroll Selenium",1)
        sTestStepReturnStatus=Selenium_Built_In.Scroll(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)

#         if sTestStepReturnStatus in passed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Successfully Scrolled Selenium", 1)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Scroll Selenium", 1)
#              return sTestStepReturnStatus
# 
#         elif sTestStepReturnStatus in failed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Unable to scroll selenium", 3)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Scroll Selenium", 1)
#              return sTestStepReturnStatus
# 
#         else:
#              CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
#              temp_q.put("failed")
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Scroll selenium", 1)
#              return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to scroll:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"  

def step_result_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Step Result Selenium",1)
        sTestStepReturnStatus=Selenium_Built_In.Step_Result(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)

#         if sTestStepReturnStatus in passed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Successfully showing correct step result ", 1)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Step result selenium", 1)
#              return sTestStepReturnStatus
# 
#         elif sTestStepReturnStatus in failed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Unable to show correct result", 3)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Step result selenium", 1)
#              return sTestStepReturnStatus
# 
#         else:
#              CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
#              temp_q.put("failed")
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Step result selenium", 1)
#              return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to show correct step result:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"  

def sequential_actions_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Sequential Actions Selenium",1)
        sTestStepReturnStatus=Selenium_Built_In.Sequential_Actions(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)
# 
#         if sTestStepReturnStatus in passed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Successfully run sequential actions selenium", 1)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Sequential actions selenium", 1)
#              return sTestStepReturnStatus
# 
#         elif sTestStepReturnStatus in failed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Unable to run sequential actions selenium", 3)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Sequential actions selenium", 1)
#              return sTestStepReturnStatus
# 
#         else:
#              CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
#              temp_q.put("failed")
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Sequential actions selenium", 1)
#              return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to run sequential actions Selenium: %s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"

def validate_table_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Validate Table",1)
        sTestStepReturnStatus=Selenium_Built_In.Validate_Table(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)

#         if sTestStepReturnStatus in passed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Successfully validated table selenium", 1)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Validate table selenium", 1)
#              return sTestStepReturnStatus
# 
#         elif sTestStepReturnStatus in failed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Unable to validate table selenium", 3)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Validate table selenium", 1)
#              return sTestStepReturnStatus
# 
#         else:
#              CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
#              temp_q.put("failed")
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Validate table selenium", 1)
#              return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to Validate Table:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"  

'======'

def tear_down_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Tear Down Selenium",1)
        sTestStepReturnStatus=Selenium_Built_In.Tear_Down()
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus,temp_q)

#         if sTestStepReturnStatus in passed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Successfully Teared Down Selenium", 1)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Tear Down Selenium", 1)
#              return sTestStepReturnStatus
# 
#         elif sTestStepReturnStatus in failed_tag_list:
#              CommonUtil.ExecLog(sModuleInfo, "Unable to tear down selenium", 3)
#              temp_q.put(sTestStepReturnStatus)
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Tear Down Selenium", 1)
#              return sTestStepReturnStatus
# 
#         else:
#              CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
#              temp_q.put("failed")
#              CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Tear Down Selenium", 1)
#              return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to Tear Down Selenium:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"  
