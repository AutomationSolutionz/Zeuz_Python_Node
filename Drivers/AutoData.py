from appium import webdriver
import os,sys,time
import inspect
from Utilities import CommonUtil
from AutoData import AndroidDemo_script
from Automation.Web.SeleniumAutomation import navigate as n
#from Automation.Web.SeleniumAutomation import locateInteraction
from Utilities import CompareModule
#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False


def open_app(dependency,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        package_name=step_data[0][0][1]
        activity_name=step_data[0][1][1]
        sTestStepReturnStatus = AndroidDemo_script.launch(package_name,activity_name)
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to launch app: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"

def confirm_right_menu_items(dependency,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        sTestStepReturnStatus = AndroidDemo_script.confirm_right()
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm right menu options: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"

def go_to_a_left_menu_section(dependency,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        section_name=step_data[0][0][1]
        sTestStepReturnStatus = AndroidDemo_script.go_left(section_name)
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go to left menu section: %s: Error:%s" %(section_name, Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"

def close_app(dependency,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        sTestStepReturnStatus = AndroidDemo_script.close()
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to close app: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"

def open_browser(dependency,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        #first_data_set=step_data[0]
        browser_name=dependency['dependency']['Browser']
        stepReturn=n.selectBrowser(browser_name)
        CommonUtil.ExecLog(sModuleInfo,"started the browser",1,local_run)
        temp_q.put(stepReturn)
        return stepReturn
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start browser: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"

def close_browser(dependency,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        sTestStepReturnStatus=n.tearDown()
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to close browser: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"

def go_to_webpage(dependency,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        first_data_set=step_data[0]
        web_link=first_data_set[0][1]
        sTestStepReturnStatus=n.openLink(web_link)
        time.sleep(10)
        print sTestStepReturnStatus
        temp_q.put(sTestStepReturnStatus)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go to webpage: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"

def car_selection(dependency,step_data,file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        first_data_set=step_data[0]
        print first_data_set
        distinct =sorted(list(set([x[0] for x in first_data_set])),key=lambda x:x)
        car_data=[]
        for e in distinct:
            l=filter(lambda x:x[0]==e,first_data_set)
            Dict={}
            for i in l:
                Dict.update({i[1]:i[2]})
            car_data.append(Dict)
        print car_data
        if AndroidDemo_script.select_base_car(car_data[0]):
            CommonUtil.ExecLog(sModuleInfo,"Selected the first car successfully",1,local_run)
            AndroidDemo_script.select_car(car_data[1],1)
            AndroidDemo_script.select_car(car_data[2],2)
            AndroidDemo_script.select_car(car_data[3],3)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Can't select the first car",1,local_run)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to complete car selection: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
		
def car_selection_base(dependency,step_data,file_attachment, temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        first_data_set=step_data[0]
        print first_data_set
        distinct =sorted(list(set([x[0] for x in first_data_set])),key=lambda x:x)
        car_data=[]
        for e in distinct:
            l=filter(lambda x:x[0]==e,first_data_set)
            Dict={}
            for i in l:
                Dict.update({i[1]:i[2]})
            car_data.append(Dict)
        print car_data
        AndroidDemo_script.select_base_car(car_data[0])
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to complete car selection: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
		
def verify_data(dependency,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        first_data_set=step_data[0]
        tag_list=filter(lambda x:x[0]=='tag',first_data_set)
        rest_data=filter(lambda x:x[0]!='tag',first_data_set)
        total_list=AndroidDemo_script.read_data_from_page(tag_list)
        oCompare=CompareModule()
        expected_list=CompareModule.make_single_data_set_compatible(rest_data)
        actual_list=CompareModule.make_single_data_set_compatible(total_list)
        status=oCompare.compare([expected_list],[actual_list])
        temp_q.put(status)
        return status
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to verify data: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
    
def lock_car(dependency,steps_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        first_data_set=steps_data[0]
        car_number=int(first_data_set[0][1])
        stepReturnStatus=AndroidDemo_script.lock_unlock_car(car_number,True)
        temp_q.put(stepReturnStatus)
        return stepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to verify data: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
    
def unlock_car(dependency,steps_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        first_data_set=steps_data[0]
        car_number=int(first_data_set[0][1])
        stepReturnStatus=AndroidDemo_script.lock_unlock_car(car_number)
        temp_q.put(stepReturnStatus)
        return stepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to verify data: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"

def open_detail_pop_up(dependency,steps_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        first_data_set=steps_data[0]
        tag_to_click=first_data_set[0][1]
        description_to_match=first_data_set[1][1]
        actual_data=AndroidDemo_script.open_detail_pop_up(tag_to_click,description_to_match)
        if actual_data:
            oCompare=CompareModule()
            expected_list=CompareModule.make_single_data_set_compatible(first_data_set)
            actual_list=CompareModule.make_single_data_set_compatible(actual_data)
            stepReturnStatus=oCompare.compare([expected_list],[actual_list])
        else:
            stepReturnStatus=False
        temp_q.put(stepReturnStatus)
        return stepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to verify data: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
    
def check_nissan_advantage_tag(dependency,steps_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        first_data_set=steps_data[0]
        stepReturnStatus=AndroidDemo_script.check_nissan_adv_tag(first_data_set[0][1])
        temp_q.put(stepReturnStatus)
        return stepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to verify data: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"
import Queue
if __name__=='__main__':
    q=Queue.Queue()
    open_browser({},[[('browser','chrome',False,False)]],{},q)
    go_to_webpage({},[[('web_link','http://compare.nissanusa.com/nissan_compare/NNAComparator/Compare.jsp?clientID=273266&modelName=z&#params:main=competitorselect~acode=XGC60NIC041A0',False,False)]],{},q)
    check_nissan_advantage_tag({},[[('tag','Recommended fuel',False,False)]],{},q)
    #open_detail_pop_up({},[[('tag','Body material',False,False),('description','The front bumper is body color.',False,False)]],{},q)
    #car_selection({},[ [ ( 'car 1' , 'model' , 'GT-R Coupe' , False , False ) , ( 'car 1' , 'year' , '2015' , False , False ) , ( 'car 1' , 'version' , 'Premium' , False , False ) , ( 'car 2' , 'year' , '2015' , False , False ) , ( 'car 2' , 'make' , 'Mitsubishi' , False , False ) , ( 'car 2' , 'model' , 'Lancer' , False , False ) , ( 'car 2' , 'trim' , 'SE 4dr 4WD Sedan' , False , False ) ] ],{},q)
    #verify_data({},[[('tag','Pricing',False,False),('tag','Fuel Economy',False,False)]],{},q)
    #lock_car({},[[('car_number',2,False,False)]],{},q)
    #unlock_car({},[[('car_number',2,False,False)]],{},q)
    close_browser({},[],{},q)
