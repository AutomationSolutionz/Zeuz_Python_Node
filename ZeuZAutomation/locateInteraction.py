__author__ = 'shetu'




from AutomationFW.ZeuZAutomation import config
import os,sys
def Locate_Element_By_ID(element_name,parent=False):
    try:
        if isinstance(parent,bool) == True:
            e=config.sBrowser.find_element_by_id(element_name)

        else:
            e=parent.find_element_by_id(element_name)
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