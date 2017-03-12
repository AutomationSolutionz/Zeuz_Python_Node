
import os, sys
import inspect
from Utilities import CommonUtil
from Projects.DigiFlare import AndroidDemo_script

passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True',True,1,'1','Success','success','SUCCESS']
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE',False,0,'0']


def open_app(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        package_name=step_data[0][0][1]
        activity_name=step_data[0][1][1]

        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Open App", 1)
        sTestStepReturnStatus = AndroidDemo_script.launch(package_name,activity_name)

        if   sTestStepReturnStatus in passed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Successfully opened app", 1)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Open App", 1)
             return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Unable to launch app", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Open App", 1)
             return sTestStepReturnStatus

        else:
             CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
             temp_q.put("failed")
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Open App", 1)
             return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to launch app: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"
    
def confirm_right_menu_items(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Confirm right menu items", 1)
        sTestStepReturnStatus = AndroidDemo_script.confirm_right()

        if   sTestStepReturnStatus in passed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Successfully confirmed right menu options", 1)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm right menu items", 1)
             return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Unable to confirm right menu options", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm right menu items", 1)
             return sTestStepReturnStatus

        else:
             CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
             temp_q.put("failed")
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm right mneu items", 1)
             return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm right menu options: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"
    
    
def confirm_left_menu_items(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Confirm left menu items", 1)
        sTestStepReturnStatus = AndroidDemo_script.confirm_left()

        if   sTestStepReturnStatus in passed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Successfully confirmed left menu options", 1)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm Left Menu Items", 1)
             return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Unable to confirm left menu options", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm Left Menu Items", 1)
             return sTestStepReturnStatus

        else:
             CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
             temp_q.put("failed")
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm Left Menu Items", 1)
             return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm left menu options: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"


def check_sub_menu_exixts(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        section_name = step_data[0][0][1]

        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Check Sub Mneu Exist", 1)
        sTestStepReturnStatus = AndroidDemo_script.confirm_submenu(section_name)

        if   sTestStepReturnStatus in passed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Successfully Confirmed Sub Menu", 1)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Check Sub Menu Exist", 1)
             return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Unable to confirm sub menu", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Check Sub Menu Exist", 1)
             return sTestStepReturnStatus

        else:
             CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
             temp_q.put("failed")
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Check Sub Menu Exist", 1)
             return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm sub menu: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"



def confirm_opened_section(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        section_name = step_data[0][0][1]

        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Confirmed open section", 1)
        sTestStepReturnStatus = AndroidDemo_script.check_section(section_name)

        if   sTestStepReturnStatus in passed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Successfully Confirmed Open Section", 1)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm opened section", 1)
             return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Unable to confirm the section", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm opened section", 1)
             return sTestStepReturnStatus

        else:
             CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
             temp_q.put("failed")
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm opened section", 1)
             return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm the section: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"



def confirm_sub_menu_items(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        submenus=step_data[0][0][1]

        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Confirm sub menu items", 1)
        sTestStepReturnStatus = AndroidDemo_script.confirm_submenu_items(submenus)

        if   sTestStepReturnStatus in passed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Successfully Confirmed sub menu options", 1)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm sub menu items", 1)
             return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Unable to confirm sub menu options", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm sub menu items", 1)
             return sTestStepReturnStatus

        else:
             CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
             temp_q.put("failed")
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm sub menu items", 1)
             return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm sub menu options: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"


def confirm_video_player(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Confirm video player", 1)
        sTestStepReturnStatus = AndroidDemo_script.confirm_player()

        if   sTestStepReturnStatus in passed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Successfully Confirmed Video Player", 1)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm video player", 1)
             return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Unable to confirm video player", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm video player", 1)
             return sTestStepReturnStatus

        else:
             CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
             temp_q.put("failed")
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Confirm video player", 1)
             return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm video player: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"
    

def go_to_a_left_menu_section(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        section_name=step_data[0][0][1]

        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Go to a left menu section", 1)
        sTestStepReturnStatus = AndroidDemo_script.go_left(section_name)

        if   sTestStepReturnStatus in passed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Successfully went to a left menu section", 1)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Go to a left menu section", 1)
             return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Unable to go to left menu section", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Go to a left menu section", 1)
             return sTestStepReturnStatus

        else:
             CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
             temp_q.put("failed")
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Go to a left menu section", 1)
             return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go to left menu section: %s: Error:%s" %(section_name, Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"
    
def go_to_a_sub_menu_section(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        section_name=step_data[0][0][1]

        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Go to a sub menu section", 1)
        sTestStepReturnStatus = AndroidDemo_script.go_sub(section_name)

        if   sTestStepReturnStatus in passed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Successfully went to a sub menu section", 1)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Go to a sub menu section", 1)
             return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Unable to go to a sub menu section", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Go to a sub menu section", 1)
             return sTestStepReturnStatus

        else:
             CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
             temp_q.put("failed")
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Go to a sub menu section", 1)
             return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go to left sub-menu section: %s: Error:%s" %(section_name, Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"

def close_app(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Close App", 1)
        sTestStepReturnStatus = AndroidDemo_script.close()

        if   sTestStepReturnStatus in passed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Successfully Closed the App", 1)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Close App", 1)
             return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
             CommonUtil.ExecLog(sModuleInfo, "Unable to close the app", 3)
             temp_q.put(sTestStepReturnStatus)
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Close App", 1)
             return sTestStepReturnStatus

        else:
             CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
             temp_q.put("failed")
             CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Close app", 1)
             return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to close app: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"
    