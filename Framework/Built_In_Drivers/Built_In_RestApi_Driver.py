'''
Created on May 15, 2016

@author: AutomationSolutionz Inc.

@asifurrouf
'''

import os,sys
import inspect
from Utilities import CommonUtil
from Built_In_Automation.API.REST import BuiltInFunctions as REST_Api_Built_In

passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True',True,1,'1','Success','success','SUCCESS']
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE',False,0,'0']

def get_method_single(dependency, run_params, step_data, file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Get Method Single", 1)


        url=step_data[0][0][2]

        #sTestStepReturnStatus = Selenium_Built_In.Go_To_Link(web_link)

        sTestStepReturnStatus = REST_Api_Built_In.Data_By_GET_Method(url)

        if  sTestStepReturnStatus in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Successfully received get method single", 1)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Get Method Single", 1)
            return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo,"Unable to receive get method single", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Get Method Single", 1)
             return sTestStepReturnStatus

        else:
            CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
            temp_q.put("failed")
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Get Method Single", 1)
            return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to receive get method single:%s" % (Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"


def get_method_multiple(dependency, run_params, step_data, file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - get method multiple", 1)

        ########### URL Zone ###########

        url=step_data[0][0][2]

        ########### Parameters Zone ###########

        param_Key_1 = step_data[1][1][0]
        param_Key_2 = step_data[1][2][0]
        param_Key_3 = step_data[1][3][0]

        param_value_1 = step_data[1][1][2]
        param_value_2 = step_data[1][2][2]
        param_value_3 = step_data[1][3][2]

        ############ Payload Zone ##############
        payload = {}

        payload[param_Key_3] = param_value_3
        payload[param_Key_2] = param_value_2
        payload[param_Key_1] = param_value_1

        ############ Headers Zone ##############

        header_Key = step_data[2][1][0]
        header_value = step_data[2][1][2]

        header = {}
        header[header_Key] = header_value

        ############ Data_By_GET_Method_Multiple Usage ##############

        sTestStepReturnStatus = REST_Api_Built_In.Data_By_GET_Method_Multiple(url,payload,header)

        if  sTestStepReturnStatus in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Successfully received get method multiple", 1)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Get Method Multiple", 1)
            return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo,"Unable to receive get method multiple", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Get Method Multiple", 1)
             return sTestStepReturnStatus

        else:
            CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
            temp_q.put("failed")
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Get Method Multiple", 1)
            return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to receive get method multiple:%s" % (Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"



def post_method_single(dependency, run_params, step_data, file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Post Method Single", 1)

        ########### URL ZONE ###########################

        url=step_data[0][0][2]

        ########### Parameters Zone ####################
        param_Key = step_data[1][1][0]
        param_value = step_data[1][1][2]

        payload={}
        payload[param_Key]=param_value

        ########## Data_By_POST_Method Usage ######

        sTestStepReturnStatus = REST_Api_Built_In.Data_By_POST_Method(url,payload)
        temp_q.put(sTestStepReturnStatus)

        if  sTestStepReturnStatus in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Successfully received post method single", 1)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Post Method Single", 1)
            return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo,"Unable to receive post method single", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Post Method Single", 1)
             return sTestStepReturnStatus

        else:
            CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
            temp_q.put("failed")
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Post Method Single", 1)
            return "failed"


    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception :%s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to receive post method single: %s. Error:%s" % (url, Error_Detail), 3)
        CommonUtil.TakeScreenShot(sModuleInfo)
        return "failed"

def post_method_multiple(dependency, run_params, step_data, file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Post Method Multiple", 1)

        ########### URL ZONE ##################

        url=step_data[0][0][2]

        ########### Parameters Zone ###########

        param_Key_1 = step_data[1][1][0]
        param_Key_2 = step_data[1][2][0]
        param_Key_3 = step_data[1][3][0]

        param_value_1 = step_data[1][1][2]
        param_value_2 = step_data[1][2][2]
        param_value_3 = step_data[1][3][2]

        ############ Payload Zone ##############
        payload={}

        payload[param_Key_3]=param_value_3
        payload[param_Key_2]=param_value_2
        payload[param_Key_1]=param_value_1

        ############ Headers Zone ##############

        header_Key= step_data[2][1][0]
        header_value = step_data[2][1][2]

        header={}
        header[header_Key]=header_value

        ########## Data_By_POST_Method_Multiple Usage ######

        sTestStepReturnStatus = REST_Api_Built_In.Data_By_POST_Method_Multiple(url,payload,header)

        if  sTestStepReturnStatus in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Successfully received post method Multiple", 1)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Post Method Multiple", 1)
            return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo,"Unable to receive post method Multiple", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Post Method Multiple", 1)
             return sTestStepReturnStatus

        else:
            CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
            temp_q.put("failed")
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Post Method Multiple", 1)
            return "failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception :%s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to receive post method multiple: %s. Error:%s" % (url, Error_Detail), 3)
        CommonUtil.TakeScreenShot(sModuleInfo)
        return "failed"