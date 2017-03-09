# import python modules
import os,sys,time
import inspect

# import android modules
from uiautomator import device as device

# import modules for ZeuZ Core Framework
from Utilities import CommonUtil



def unlock_phone(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        devinfo = device.info
        xAxis = devinfo[u'displaySizeDpX']
        yAxis = devinfo[u'displaySizeDpY']
        device.screen.on()
        device.swipe(xAxis,yAxis,0,0)
        device.press('home')
        CommonUtil.ExecLog(sModuleInfo, "unlocked android phone", 1)
        temp_q.put("True")
        return "True"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to unlock android phone: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"

def open_android_app(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        first_data_set=step_data[0]
        app_name=first_data_set[0][1]
        device(className="android.widget.TextView",description="Apps").click()
        device(text=app_name).click()
        CommonUtil.ExecLog(sModuleInfo,"App opened on Android",1)
        temp_q.put("True")
        return "True"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to open app on Android: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"

def close_android_app(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        devinfo = device.info
        xAxis = devinfo[u'displaySizeDpX']
        yAxis = devinfo[u'displaySizeDpY']
        device.press("recent")
        time.sleep(2)
        device.drag(xAxis/2,yAxis,xAxis,yAxis, 10)
        device.press("home")
        CommonUtil.ExecLog(sModuleInfo,"App closed on Android",1)
        temp_q.put("True")
        return "True"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to close app on Android: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"

def click_on_android_text(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        first_data_set=step_data[0]
        text_data=first_data_set[0][1]
        device(text=text_data).click()
        temp_q.put("True")
        return "True"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click text on Android Screen: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"
				
def verify_android_text(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        first_data_set=step_data[0]
        text_data=first_data_set[0][1]
        status = device(text=text_data).exists
        temp_q.put(status)
        return status
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to verify text on Android Screen: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"
