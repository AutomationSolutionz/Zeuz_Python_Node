__author__ = 'shetu'
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from Automation.Web.SeleniumAutomation.locateInteraction import Locate_Element_By_ID,Locate_Element_By_Class,Locate_Element_By_Text,Locate_Element_By_Parameter_Value
WebDriver_Wait=20
from selenium.webdriver.support import expected_conditions as EC
import os,sys
def Click_Element_By_ID(element_name,parent=False):
    try:
        e=Locate_Element_By_ID(element_name,parent)
        e.click()
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail

def Click_Element_By_Class(class_name,parent=False):
    try:
        e=Locate_Element_By_Class(class_name,parent)
        e.click()
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail

def Click_Element_By_Text(element_text,parent=False):
    try:
        e=Locate_Element_By_Text(element_text,parent)
        e.click()
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail

def Click_By_Parameter_And_Value(parameter,value, parent=False):
    try:
        Element=Locate_Element_By_Parameter_Value(parameter,value,parent)
        Element.click()
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        return "failed"

def Click_Element_By_Name(_name,parent=False):
    try:
        if isinstance(parent, (bool)) == True:
            allElements = WebDriverWait(config.sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[text()='%s']"%_name)))
        else:
            allElements = WebDriverWait(parent, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[text()='%s']"%_name)))
        if allElements == []:
            return "failed"
        else:
            allElements=filter(lambda x:x.text==_name,allElements)
            for each in allElements:
                if (WebDriverWait(each, WebDriver_Wait).until(lambda driver : each.is_displayed())) == True:
                    Element = each
                    break
                    #Now we simply click it
        Element.click()
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        return "failed"
