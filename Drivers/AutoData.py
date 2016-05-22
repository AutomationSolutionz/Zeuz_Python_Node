
import os,sys
import inspect
from Utilities import CommonUtil
from Projects.AutoData import Mobile_Functions as MF
from Projects.AutoData import Browser_Functions as BF
#from Built_In_Automation.Web.SeleniumAutomation import _navigate as n
#from Built_In_Automation.Web.SeleniumAutomation import locateInteraction
from Utilities import CompareModule
#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False


def car_selection(dependency,run_time_params,step_data,file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Car Selection",1,local_run)
        first_data_set=step_data[0]
        stepResult=BF.selectCar(first_data_set)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Car Selection",1,local_run)
        return stepResult
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to complete car selection: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
    
        
def car_selection_base(dependency,run_time_params,step_data,file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Car Selection Base",1,local_run)
        first_data_set=step_data[0]
        stepResult=BF.select_car_base(first_data_set)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Car Selection Base",1,local_run)
        return stepResult
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to complete car selection base: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"


def verify_data(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Verify Data",1,local_run)
        first_data_set=step_data[0]
        status = BF.data_verify(first_data_set)
        temp_q.put(status)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Verify Data",1,local_run)
        return status
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to verify data: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
    
def lock_car(dependency,run_time_params,steps_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Lock Car",1,local_run)
        first_data_set=steps_data[0]
        car_number=int(first_data_set[0][1])
        stepReturnStatus=BF.lock_unlock_car(car_number,True)
        temp_q.put(stepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Lock Car",1,local_run)
        return stepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to lock car: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
    
def unlock_car(dependency,run_time_params,steps_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Unlock Car",1,local_run)
        first_data_set=steps_data[0]
        car_number=int(first_data_set[0][1])
        stepReturnStatus=BF.lock_unlock_car(car_number)
        temp_q.put(stepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Unlock Car",1,local_run)
        return stepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to unlock car: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"

def open_detail_pop_up(dependency,run_time_params,steps_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Open Detail Pop-up",1,local_run)
        first_data_set=steps_data[0]
        tag_to_click=first_data_set[0][1]
        description_to_match=first_data_set[1][1]
        actual_data=BF.open_detail_pop_up(tag_to_click,description_to_match)
        if actual_data:
            oCompare=CompareModule()
            expected_list=CompareModule.make_single_data_set_compatible(first_data_set)
            actual_list=CompareModule.make_single_data_set_compatible(actual_data)
            stepReturnStatus=oCompare.compare([expected_list],[actual_list])
        else:
            stepReturnStatus=False
        temp_q.put(stepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Open Detail Pop-up",1,local_run)
        return stepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to open detail pop-up: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
    
def check_nissan_advantage_tag(dependency,run_time_params,steps_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Check Nissan Advantage Tag",1,local_run)
        first_data_set=steps_data[0]
        stepReturnStatus=BF.check_nissan_adv_tag(first_data_set[0][1])
        temp_q.put(stepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Check Nissan Advantage Tag",1,local_run)
        return stepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to verify data: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"


def confirm_right_menu_items(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Confirm Right Menu Items",1,local_run)
        sTestStepReturnStatus = MF.confirm_right()
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Confirm right menu items",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm right menu options: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"


def go_to_a_left_menu_section(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Enter: Step - Go to a left menu section",1,local_run)
        section_name=step_data[0][0][1]
        sTestStepReturnStatus = MF.go_left(section_name)
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        CommonUtil.ExecLog(sModuleInfo,"Exit: Step - Go to a left menu section",1,local_run)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go to left menu section: %s: Error:%s" %(section_name, Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"

