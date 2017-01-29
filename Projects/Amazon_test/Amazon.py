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
#local_run = True
local_run = False



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


def Add_to_Cart(search_text):
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
        else: #if search button is not found
            #Taking Screenshot
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            CommonUtil.ExecLog(sModuleInfo, "Failed to clicked your element", 3, local_run)
            CommonUtil.ExecLog(sModuleInfo, "Searching was not successful", 3, local_run)
            return "failed"

        #clicking the first search result
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on the first search result",1,local_run)
        first_element = BuiltInFunctions.Get_Element('tag','a','class','s-item-container','parent')
        if first_element!='failed':
            CommonUtil.ExecLog(sModuleInfo, "Found first search result element", 1, local_run)
            CommonUtil.ExecLog(sModuleInfo, "Clicking on the first search result element", 1, local_run)
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            first_element.click()
            time.sleep(10)
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            CommonUtil.ExecLog(sModuleInfo, "Clicked on the first search result elemnt successfully", 1, local_run)
        else:
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            CommonUtil.ExecLog(sModuleInfo, "Failed to find the first search result element", 3, local_run)
            return "failed"

        #add this item to cart
        CommonUtil.ExecLog(sModuleInfo, "Trying to add this item to cart", 1, local_run)
        CommonUtil.ExecLog(sModuleInfo, "Trying to click on Add to Cart button", 1, local_run)
        add_to_cart_button = BuiltInFunctions.Get_Element('id','add-to-cart-button')
        if add_to_cart_button != 'failed':
            CommonUtil.ExecLog(sModuleInfo, "Found Add to Cart button", 1, local_run)
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            CommonUtil.ExecLog(sModuleInfo, "Clicking on the Add to Cart button", 1, local_run)
            add_to_cart_button.click()
            time.sleep(10)
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            CommonUtil.ExecLog(sModuleInfo, "Clicked on the Add to Cart button successfully", 1, local_run)
            return "passed"
        else:
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            CommonUtil.ExecLog(sModuleInfo, "Failed to click on the Add to Cart Button", 3, local_run)
            return "failed"


    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo,"Could not add the item to cart.  Error: %s" % (search_text, Error_Detail), 3,local_run)
        return "failed"
