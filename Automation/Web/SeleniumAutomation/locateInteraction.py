__author__ = 'shetu'
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
WebDriver_Wait=20
from Automation.Web.SeleniumAutomation import config as config
from selenium.webdriver.support import expected_conditions as EC
import os,sys
def Locate_Element_By_ID(element_name,parent=False):
    try:

        if isinstance(parent,bool) == True:
            #e=config.sBrowser.find_element_by_id(element_name)
            e = WebDriverWait(config.sBrowser, WebDriver_Wait).until(EC.presence_of_element_located((By.ID, element_name)))
        else:
            e = WebDriverWait(parent, WebDriver_Wait).until(EC.presence_of_element_located((By.ID, element_name)))
        return e
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail

def Locate_Element_By_Class(class_name,parent=False):
    try:
        if isinstance(parent,bool) == True:
            e=config.sBrowser.find_element_by_class_name(class_name)
        else:
            e=parent.find_element_by_class_name(class_name)
        return e
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail

def Locate_Element_By_Text(element_text,parent=False):
    try:
        if isinstance(parent,bool) == True:
            e=config.sBrowser.find_element_by_link_text(element_text)
        else:
            e=parent.find_element_by_link_text(element_text)
        return e
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail

def Locate_Element_By_Tag(tag_text,parent=False,multiple=False):
    try:
        if isinstance(parent,bool) == True:
            if not multiple:
                e=config.sBrowser.find_element_by_tag_name(tag_text)
            else:
                e=config.sBrowser.find_elements_by_tag_name(tag_text)
        else:
            if not multiple:
                e=parent.find_element_by_tag_name(tag_text)
            else:
                e=parent.find_elements_by_tag_name(tag_text)
        return e
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))

def Locate_Element_By_Name(element_name,parent=False):
    try:
        if isinstance(parent,bool) == True:
            e=config.sBrowser.find_element_by_name(element_name)

        else:
            e=parent.find_element_by_name(element_name)
        return e
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail

def Locate_Elements_By_Class(class_name,parent=False):
    try:
        if isinstance(parent,bool) == True:
            e=config.sBrowser.find_elements_by_class_name(class_name)
        else:
            e=parent.find_elements_by_class_name(class_name)
        return e
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail

def Locate_Element_By_Parameter_Value(parameter,value,parent=False,multiple=False):
    try:
        if isinstance(parent, (bool)) == True:
            Element = WebDriverWait(config.sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@%s='%s']"%(parameter,value))))
        else:
            Element = WebDriverWait(parent, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@%s='%s']"%(parameter,value))))
        if multiple:
            return Element
        else:
            return Element[0]
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        return "failed"

def Locate_Element_In_Table_By_Text(_text,parent,multiple=False):
    try:
        if isinstance(parent, (bool)) == True:
            Element = WebDriverWait(config.sBrowser, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'td')))
        else:
            Element = WebDriverWait(parent, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.TAG_NAME,'td')))
        filtered_elements=filter(lambda x:x.text==_text,Element)
        if multiple:
            return filtered_elements
        else:
            return filtered_elements[0]
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        return "failed"