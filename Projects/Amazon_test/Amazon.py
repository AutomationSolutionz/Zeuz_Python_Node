'''

@author: Automation Solutionz
'''

import sys
import os

sys.path.append("..")
import inspect
import time
from Utilities import CommonUtil
from Built_In_Automation.Web.Selenium import BuiltInFunctions


# if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
local_run = True
# local_run = False



def Item_Search(search_text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        #Writing Logs with CommonUtil
        CommonUtil.ExecLog(sModuleInfo, "Trying locate search menu", 1, local_run)

        #Finding the Search Box
        search_box = BuiltInFunctions.Get_Element('id','twotabsearchtextbox')

        #Entering provided text in Search Box
        search_box.send_keys(search_text)

        time.sleep(10)
        CommonUtil.ExecLog(sModuleInfo, "Trying to click the search button", 1, local_run)

        #Finding the search button
        search_button = BuiltInFunctions.Get_Element('value','Go')

        if search_button != "failed": #if search button found
            #Clicking on the search button
            BuiltInFunctions.Click_Element_StandAlone(search_button)
            time.sleep(10)
            #Taking Screenshot
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            CommonUtil.ExecLog(sModuleInfo, "Clicked your element", 1, local_run)
            CommonUtil.ExecLog(sModuleInfo, "Searching successfully done!!!", 1, local_run)
            return "passed"
        else: #if search button is not found
            #Taking Screenshot
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            CommonUtil.ExecLog(sModuleInfo, "Failed to clicked your element", 3, local_run)
            CommonUtil.ExecLog(sModuleInfo, "Searching was not successful", 3, local_run)
            return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo,"Could not search item: %s.  Error: %s" % (search_text, Error_Detail), 3,local_run)
        return "failed"

