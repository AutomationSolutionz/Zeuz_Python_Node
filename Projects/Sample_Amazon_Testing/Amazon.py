# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
'''

@author: Automation Solutionz
'''

import sys
import os
import xlrd

sys.path.append("..")
import inspect
import time
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions


MODULE_NAME = inspect.getmoduleinfo(__file__).name


def Item_Search(search_text):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        #Writing Logs with CommonUtil
        CommonUtil.ExecLog(sModuleInfo, "Trying locate search menu", 1)

        #Finding the Search Box
        search_box = BuiltInFunctions.Get_Element('id','twotabsearchtextbox')

        #Entering provided text in Search Box
        search_box.send_keys(search_text)

        time.sleep(10)
        CommonUtil.ExecLog(sModuleInfo, "Trying to click the search button", 1)

        #Finding the search button
        search_button = BuiltInFunctions.Get_Element('value','Go')

        if search_button != "failed": #if search button found
            #Clicking on the search button
            BuiltInFunctions.Click_Element_StandAlone(search_button)
            time.sleep(10)
            #Taking Screenshot
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Clicked your element", 1)
            CommonUtil.ExecLog(sModuleInfo, "Searching successfully done!!!", 1)
            return "passed"
        else: #if search button is not found
            #Taking Screenshot
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Failed to clicked your element", 3)
            CommonUtil.ExecLog(sModuleInfo, "Searching was not successful", 3)
            return "failed"

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo,"Could not search item: %s.  Error: %s" % (search_text, Error_Detail), 3)
        return "failed"


def Add_to_Cart(search_text):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        #Writing Logs with CommonUtil
        CommonUtil.ExecLog(sModuleInfo, "Trying locate search menu", 1)

        #Finding the Search Box
        search_box = BuiltInFunctions.Get_Element('id','twotabsearchtextbox')

        #Entering provided text in Search Box
        search_box.send_keys(search_text)

        time.sleep(10)
        CommonUtil.ExecLog(sModuleInfo, "Trying to click the search button", 1)

        #Finding the search button
        search_button = BuiltInFunctions.Get_Element('value','Go')

        if search_button != "failed": #if search button found
            #Clicking on the search button
            BuiltInFunctions.Click_Element_StandAlone(search_button)
            time.sleep(10)
            #Taking Screenshot
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Clicked your element", 1)
            CommonUtil.ExecLog(sModuleInfo, "Searching successfully done!!!", 1)
        else: #if search button is not found
            #Taking Screenshot
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Failed to clicked your element", 3)
            CommonUtil.ExecLog(sModuleInfo, "Searching was not successful", 3)
            return "failed"

        #clicking the first search result
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on the first search result",1)
        first_element = BuiltInFunctions.Get_Element('tag','a','class','s-item-container','parent')
        if first_element!='failed':
            CommonUtil.ExecLog(sModuleInfo, "Found first search result element", 1)
            CommonUtil.ExecLog(sModuleInfo, "Clicking on the first search result element", 1)
            CommonUtil.TakeScreenShot(sModuleInfo)
            first_element.click()
            time.sleep(10)
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Clicked on the first search result element successfully", 1)
        else:
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Failed to find the first search result element", 3)
            return "failed"

        #add this item to cart
        CommonUtil.ExecLog(sModuleInfo, "Trying to add this item to cart", 1)
        CommonUtil.ExecLog(sModuleInfo, "Trying to click on Add to Cart button", 1)
        add_to_cart_button = BuiltInFunctions.Get_Element('id','add-to-cart-button')
        if add_to_cart_button != 'failed':
            CommonUtil.ExecLog(sModuleInfo, "Found Add to Cart button", 1)
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Clicking on the Add to Cart button", 1)
            add_to_cart_button.click()
            time.sleep(10)
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Clicked on the Add to Cart button successfully", 1)
            return "passed"
        else:
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Failed to click on the Add to Cart Button", 3)
            return "failed"


    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo,"Could not add the item to cart.  Error: %s" % (search_text, Error_Detail), 3)
        return "failed"



def Add_to_Cart_Using_Selenium(step_data,file_attachment):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        excel_file_name = step_data[0][0][2]
        file_name = file_attachment[excel_file_name]
        book = xlrd.open_workbook(file_name)

        # select the sheet that the data resids in
        work_sheet = book.sheet_by_index(0)
        search_text = work_sheet.cell_value(0, 1)

        #Writing Logs with CommonUtil
        CommonUtil.ExecLog(sModuleInfo, "Trying locate search menu", 1)

        #Finding the Search Box

        #global selenium_driver
        from Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions import selenium_driver
        #search_box = BuiltInFunctions.Get_Element('id','twotabsearchtextbox')
        search_box = selenium_driver.find_element_by_id("twotabsearchtextbox")

        #Entering provided text in Search Box
        search_box.send_keys(search_text)

        time.sleep(10)
        CommonUtil.ExecLog(sModuleInfo, "Trying to click the search button", 1)

        #Finding the search button
        #search_button = BuiltInFunctions.Get_Element('value','Go')
        search_button = selenium_driver.find_element_by_xpath('//*[@id="nav-search"]/form/div[2]/div/input')

        if search_button != "failed": #if search button found
            #Clicking on the search button
            search_button.click()
            #BuiltInFunctions.Click_Element_StandAlone(search_button)
            time.sleep(10)
            #Taking Screenshot
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Clicked your element", 1)
            CommonUtil.ExecLog(sModuleInfo, "Searching successfully done!!!", 1)
        else: #if search button is not found
            #Taking Screenshot
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Failed to clicked your element", 3)
            CommonUtil.ExecLog(sModuleInfo, "Searching was not successful", 3)
            return "failed"

        #clicking the first search result
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on the first search result",1)
        #first_element = BuiltInFunctions.Get_Element('tag','a','class','s-item-container','parent')
        first_element = selenium_driver.find_element_by_xpath('//*[@id="result_0"]/div/div[3]/div[1]/a/h2')
        if first_element!='failed':
            CommonUtil.ExecLog(sModuleInfo, "Found first search result element", 1)
            CommonUtil.ExecLog(sModuleInfo, "Clicking on the first search result element", 1)
            CommonUtil.TakeScreenShot(sModuleInfo)
            first_element.click()
            time.sleep(10)
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Clicked on the first search result elemnt successfully", 1)
        else:
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Failed to find the first search result element", 3)
            return "failed"

        #add this item to cart
        CommonUtil.ExecLog(sModuleInfo, "Trying to add this item to cart", 1)
        CommonUtil.ExecLog(sModuleInfo, "Trying to click on Add to Cart button", 1)
        #add_to_cart_button = BuiltInFunctions.Get_Element('id','add-to-cart-button')
        add_to_cart_button = selenium_driver.find_element_by_id("add-to-cart-button")
        if add_to_cart_button != 'failed':
            CommonUtil.ExecLog(sModuleInfo, "Found Add to Cart button", 1)
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Clicking on the Add to Cart button", 1)
            add_to_cart_button.click()
            time.sleep(10)
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Clicked on the Add to Cart button successfully", 1)
            return "passed"
        else:
            CommonUtil.TakeScreenShot(sModuleInfo)
            CommonUtil.ExecLog(sModuleInfo, "Failed to click on the Add to Cart Button", 3)
            return "failed"


    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo,"Could not add the item %s to cart.  Error: %s" % (search_text, Error_Detail), 3)
        return "failed"
