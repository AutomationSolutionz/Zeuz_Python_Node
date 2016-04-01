__author__ = 'shetu'
from AutomationFW.ZeuZAutomation.locateInteraction import Locate_Element_By_ID,Locate_Element_By_Class,Locate_Element_By_Text
from AutomationFW.ZeuZAutomation import config
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

