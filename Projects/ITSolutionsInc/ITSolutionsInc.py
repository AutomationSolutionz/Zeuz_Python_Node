# -*- coding: cp1252 -*-
'''
Created on May 15, 2016

@author: Built_In_Automation Solutionz Inc.
'''

import sys
import os
sys.path.append("..")
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import inspect
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
#Ver1.0
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from Utilities import CommonUtil
from selenium.webdriver.support import expected_conditions as EC

#Built in function import 
from Built_In_Automation.Web.SeleniumAutomation import BuiltInFunctions
from datetime import datetime


global WebDriver_Wait 
WebDriver_Wait = 20
global WebDriver_Wait_Short
WebDriver_Wait_Short = 10

#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
local_run = True
#local_run = False

  

def Select_Gear_Menu_Item(item_text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to click on Settings Gear Icon", 1,local_run)
        try:
            BuiltInFunctions.Click_By_Parameter_And_Value('title',"Open the Settings menu to access personal and app settings", parent=False)
        except:
            CommonUtil.ExecLog(sModuleInfo, "Could not click on the Gear icon", 3,local_run)
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            return "failed"  
        time.sleep(3)
        #We now try to find the right element and click it
        CommonUtil.ExecLog(sModuleInfo, "Trying locate %s menu"%item_text, 1,local_run)
        result= BuiltInFunctions.Get_Element_With_Reference('aria-label',item_text,'ispopup', '1',"parent")
        if result != "failed":
            result.click()
            CommonUtil.ExecLog(sModuleInfo, "Clicked your element", 1,local_run)            
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Failed to clicked your element", 3,local_run)            
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not click on the Gear menu item: %s.  Error: %s"%(item_text, Error_Detail), 3,local_run)
        return "failed"       



        

    
def Create_New_Subsite(title="Automated Sub Site",description="This description was filled out by automation",url_name="Automated_Sub_Site"):
    #this function assumes you are in Site Content page
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to click on Create new site", 1,local_run)
        try:
            BuiltInFunctions.Click_By_Parameter_And_Value("id","createnewsite", parent=False)
        except:
            CommonUtil.ExecLog(sModuleInfo, "Could not click on the Create New Site Button", 3,local_run)
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            return "failed"  
        #We now fill out the form
        CommonUtil.ExecLog(sModuleInfo, "Trying to fill out the form..", 1,local_run)
        result_Title= BuiltInFunctions.Set_Text_Field_By_Parameter_And_Value('title','Title',title)
        result_Description= BuiltInFunctions.Set_Text_Field_By_Parameter_And_Value('title','Description',description)
        result_SubSite = BuiltInFunctions.Set_Text_Field_By_Parameter_And_Value('title','Create Subsite Name',url_name) 
        result_Create = BuiltInFunctions.Click_By_Parameter_And_Value('value','Create')
        if (result_Title=="passed" and result_Description == "passed" and result_SubSite== "passed" and result_Create== "passed"):
            CommonUtil.ExecLog(sModuleInfo, "Successfully filled out the form and clicked on Create", 1,local_run)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to create the form", 3,local_run)
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
        
        
        #Wait until the creating page appears
        #This should probably go in BuiltINfunction
        CommonUtil.ExecLog(sModuleInfo, "Waiting for working on creating page appears", 1,local_run)
        max_wait = 5
        i=0
        t1 = datetime.now()
        found_the_window = False
        t2=False
        while max_wait !=i: 
            result = BuiltInFunctions.Get_Element('id',"ms-loading-box")
            time.sleep(1)
            i = i+1
            if result != "failed":
                t2 = datetime.now()
                found_the_window = True
                break
        if t2==False:
            t2 = datetime.now()
        delta = t2 - t1
        if found_the_window == True:
            CommonUtil.ExecLog(sModuleInfo, "Found the waiting for creating window in: %s seconds"%delta, 1,local_run)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to find the creating window in: %s seconds"%delta, 3,local_run)
            return "failed"
        #Now that we have found the waiting for creating window... we need to wait until its gone....
        CommonUtil.ExecLog(sModuleInfo, "Waiting for working on creating page appears", 1,local_run)
        max_wait = 10
        i=0
        t1 = datetime.now()
        found_the_window = True
        t2=False
        while max_wait !=i: 
            result = BuiltInFunctions.Get_Element('id',"ms-loading-box")
            time.sleep(1)
            i = i+1
            if result == "failed":
                t2 = datetime.now()
                found_the_window = False
                break
        if t2==False:
            t2 = datetime.now()
        delta = t2 - t1
        if found_the_window == False:
            CommonUtil.ExecLog(sModuleInfo, "Creating window is gone in: %s seconds"%delta, 1,local_run)
        else:
            CommonUtil.ExecLog(sModuleInfo, "Creating window was never gone in: %s seconds"%delta, 3,local_run)
            return "failed"    
        # Need to click by text Publish it 
               

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to create the form  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"          
    
def Delete_Site(root_site='https://engitsolutions.sharepoint.com/sites/Demo/', sub_site_name='Automated Sub Site'):
    #this function assumes you are in Site Content page
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Checking to see if any sub site exists", 1,local_run)
        #first go to root site 
        BuiltInFunctions.Go_To_Link(root_site)
        #go to site contents
        Select_Gear_Menu_Item("Site contents")
        
        result = BuiltInFunctions.Get_All_Elements('text()','This site does not have any subsites.') 
        print result
    
    
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to create the form  Error: %s"%(Error_Detail), 3,local_run)
        return "failed"          
 
