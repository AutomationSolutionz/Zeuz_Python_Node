'''
Created on May 15, 2016

@author: AutomationSolutionz Inc.
'''

import os,sys,time
import inspect
from Utilities import CommonUtil
from Projects.ITSolutionsInc import ITSolutionsInc as ITS

passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True',True,1,'1','Success','success','SUCCESS']
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE',False,0,'0']

def select_gear_menu(dependency,run_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        item_text = step_data[0][0][1]
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Select gear menu", 1)
        sTestStepReturnStatus=ITS.Select_Gear_Menu_Item(item_text)

        if   sTestStepReturnStatus in passed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Successfully selected gear menu ", 1)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Select gear menu", 1)
             return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Unable to select gear menu", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Select gear menu", 1)
             return sTestStepReturnStatus

        else:
             CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
             temp_q.put("failed")
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Select gear menu", 1)
             return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to select gear menu: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"

def delete_sub_site(dependency,run_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        sub_site_name = step_data[0][0][1]
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Delete sub site", 1)
        sTestStepReturnStatus=ITS.Delete_Sub_Site(sub_site_name)

        if   sTestStepReturnStatus in passed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Successfully deleted sub site ", 1)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Delete sub site", 1)
             return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Unable to delete sub site", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Delete sub site", 1)
             return sTestStepReturnStatus

        else:
             CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
             temp_q.put("failed")
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Delete sub site", 1)
             return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to delete sub site: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"

def create_new_subsite(dependency,run_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        title = step_data[0][0][1]
        description = step_data[0][1][1]
        url_name = step_data[0][2][1]

        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Create new subsite", 1)
        sTestStepReturnStatus=ITS.Create_New_Subsite(title, description, url_name)
        
        if   sTestStepReturnStatus in passed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Successfully created gear menu ", 1)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Create gear menu", 1)
             return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Unable to create gear menu", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Create gear menu", 1)
             return sTestStepReturnStatus

        else:
             CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
             temp_q.put("failed")
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Create gear menu", 1)
             return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to create gear menu: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"
