'''
Created on May 15, 2016

@author: AutomationSolutionz Inc.

@asifurrouf
'''

import os,sys
import inspect
from Utilities import CommonUtil
from Built_In_Automation.API.REST import BuiltInFunctions as REST_Api_Built_In



def get_method_single(dependency, run_params, step_data, file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Now We are going to use GET Method", 1)


        url=step_data[0][0][2]

        #sTestStepReturnStatus = Selenium_Built_In.Go_To_Link(web_link)

        sTestStepReturnStatus = REST_Api_Built_In.Data_By_GET_Method(url)
        temp_q.put(sTestStepReturnStatus)

        CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Data have been Received POST Method", 1)
        return sTestStepReturnStatus

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go to webpage Selenium:%s" % (Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"


def get_method_multiple(dependency, run_params, step_data, file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Now We are going to use GET Method", 1)

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

        temp_q.put(sTestStepReturnStatus)

        CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Data have been Received POST Method", 1)
        return sTestStepReturnStatus

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go to webpage Selenium:%s" % (Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"



def post_method_single(dependency, run_params, step_data, file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Now We are going to use POST Method", 1)

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

        CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Data have been Received POST Method", 1)
        return sTestStepReturnStatus

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception :%s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Received Wrong Data your link: %s. Error:%s" % (url, Error_Detail), 3)
        CommonUtil.TakeScreenShot(sModuleInfo)
        return "failed"

def post_method_multiple(dependency, run_params, step_data, file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Now We are going to use POST Method", 1)

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
        temp_q.put(sTestStepReturnStatus)

        CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Data have been Received POST Method", 1)
        return sTestStepReturnStatus

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception :%s" % e, 3)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Received Wrong Data your link: %s. Error:%s" % (url, Error_Detail), 3)
        CommonUtil.TakeScreenShot(sModuleInfo)
        return "failed"