# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

'''
    Created on Mar 30, 2017
    Updated on July 20, 2017 --> use new LocateElement function and common Sequential Actions

    @author: mchowdhury
    Name: Built In Functions - XML
    Description: Sequential Actions for reading/writing XML files
'''

#########################
#                       #
#        Modules        #
#                       #
#########################

import sys, inspect
from lxml import etree as ET
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import LocateElement as LE
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list

#########################
#                       #
#    Global Variables   #
#                       #
#########################

default_tag_list = ['Default', 'default', 'DEFAULT', 'Unchanged', 'unchanged', 'UNCHAGED']
update_tag_list = ['Update', 'update', 'UPDATE', 'Replace', 'replace', 'REPLACE' ] #Update/replace existing element(s)
delete_tag_list = ['Delete', 'delete', 'DELETE', 'Remove', 'remove', 'REMOVE' ] #Delete existing line or element(s)
read_tag_list = ['Read', 'read', 'READ'] #Read existing element(s)
add_tag_list = ['Add', 'add', 'ADD'] #Add additional line(s) or element(s)


'===================== ===x=== Actions on XML File ===x=== ======================'

def update_element(step_data):
    '''
     Function to update the target element(s) of XML tree
    '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: update_element", 1)
    try:
        if (len([step_data]) != 1): #Verifies that length of step_data greater than one
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "Failed"
        
        else: 
            #Function to collect the user provided step data elements 
            element_step_data = get_element_step_data(step_data)
            if ((element_step_data == []) or (element_step_data in failed_tag_list)):
                return "Failed"
            
            else:
                #Function to update the target element(s) as per 'action' 
                returned_element = get_target_element(element_step_data[0], element_step_data[1], element_step_data[2], element_step_data[3], element_step_data[4], step_data)

                if ((returned_element == []) or (returned_element in failed_tag_list)): #if failed to update target elements
                    CommonUtil.ExecLog(sModuleInfo, "Unable to change the attribute value of '%s'" % element_step_data[0], 3)
                    return "Failed"
                        
                elif returned_element in default_tag_list: #if target elements are same as expected elements
                    CommonUtil.ExecLog(sModuleInfo, "Nothing to change the attribute value of '%s'" % element_step_data[0], 1)
                    return "Passed"
                        
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Updated the target attribute value of '%s'" % element_step_data[0], 1)
                    return "Passed"
                    
    except Exception:
 
        errMsg = "Could not update the element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def read_element(step_data):
    '''
    Function to read the elements from XML file 
    '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: read_element", 1)
    try:
        if (len([step_data]) != 1): #Verifies that length of step_data greater than one
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "Failed"
        
        else: 
            #Function to collect the user provided step data elements 
            element_step_data = get_element_step_data(step_data)
            if ((element_step_data == []) or (element_step_data in failed_tag_list)):
                CommonUtil.ExecLog(sModuleInfo, "Unable to get the file path of: '%s'" % element_step_data[0], 3)
                return "Failed"

            
            else:
                #Function to get the XML file tree
                returned_element = get_file_tree(element_step_data[0]) 
                CommonUtil.ExecLog(sModuleInfo, "File tree of: %s" %(element_step_data[0]), 1)
                CommonUtil.ExecLog(sModuleInfo, "%s" % ET.tostring(returned_element[0]), 1)
                return "Passed"
    
    except Exception:
        errMsg = "Unable to read the element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
###
# Function to delete the target element(s) of XML tree
''' This delete function not ready yet '''
def delete_element(step_data, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: delete_element", 1)
    try:
        if (len([step_data]) != 1): #Verifies that length of step_data greater than one
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "Failed"
        
        else: 
            #Function to collect the user provided step data elements 
            element_step_data = get_element_step_data(step_data)
            if ((element_step_data == []) or (element_step_data in failed_tag_list)):
                return "Failed"
            
            else:
                #Function to update the target element(s) as per 'action' 
                returned_element = get_target_element(element_step_data[0], element_step_data[1], element_step_data[2], element_step_data[3], element_step_data[4], step_data)

                if ((returned_element == []) or (returned_element in failed_tag_list)): #if failed to update target elements
                    CommonUtil.ExecLog(sModuleInfo, "Unable to change the attribute value of '%s'" % element_step_data[0], 3)
                    return "Failed"
                        
                elif returned_element in default_tag_list: #if target elements are same as expected elements
                    CommonUtil.ExecLog(sModuleInfo, "Nothing to change the attribute value of '%s'" % element_step_data[0], 1)
                    return "Passed"
                        
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Updated the target attribute value of '%s'" % element_step_data[0], 1)
                    return "Passed"
                
    except Exception:
 
        errMsg = "Unable to delete the element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


'===================== ===x=== Get Elements From Step Data ===x=== ======================'

def get_element_step_data(step_data):
    '''
    Function to collect user provided target and action elements from step data
    '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: get_element_step_data", 1)
    try:
        file_path = False
        target_parameter = False
        target_value = False
        action_parameter = False
        action_value = False
        if (len(step_data) >= 1):
            for each in step_data:
                if (each[1] == "path"):
                    file_path = each[2]
                
                elif ((each[1] == "parent parameter") or (each[1] == "child parameter") or (each[1] == "element parameter")):            
                    continue

                elif each[1]=="target parameter":
                    target_parameter = each[0]
                    target_value = each[2]
                    
                elif each[1]=="action":
                    action_parameter = each[0]
                    action_value = each[2]
                    
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to find elements requested.", 3)
            
        else:
            CommonUtil.ExecLog(sModuleInfo, "Data set incorrect. Please provide accurate data set(s) information.", 3)
            return "Failed"

        returned_data = (file_path, target_parameter, target_value, action_parameter, action_value)
        return returned_data    

    except Exception:
        errMsg = "Could not get element step data."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'===================== ===x=== Get Elements From XML File ===x=== ======================'  

def get_target_element(file_path, target_parameter, target_value, action_name, action_value, step_data):
    '''
    Function to get the target element(s) as per 'action'
    ''' 
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: get_target_element", 1)
    try:
        file_tree = []
        #Function to get the XML file tree
        file_tree = get_file_tree(file_path) 
         
        driver = None
        driver = file_tree[0]
        #Function to get the elements from the XML file
        matching_elements = LE.Get_Element(step_data, driver)
        CommonUtil.ExecLog(sModuleInfo, ">>> The expected attribute value is: '%s'" %action_value, 1)
         
        #Function to update the target element
        returned_target_element = update_target_element(file_path, file_tree[1], matching_elements, target_parameter, target_value, action_name, action_value) 
        
        return returned_target_element   

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

'''
 Function to get the XML file tree without deleting any user comment(s) '''
def get_file_tree(file_path):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: get_file_tree", 1)
    try:
        #Function to get the file parse
        doc = ET.parse(file_path) 
        
        #Function to get the file tree
        tree = doc.getroot() 
        # CommonUtil.ExecLog(sModuleInfo, "%s" % ET.tostring(tree), 1)
        
        return (tree, doc)
    
    except Exception:
        errMsg = "Unable to get the file tree."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'===================== ===x=== Updating Elements ===x=== ======================'

def update_target_element(file_path, doc, matching_elements, target_attrib, target_value, action_name, action_value):
    '''
     Function to update the target element value
    '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: update_target_element", 1)
    try:
        current_value = matching_elements.attrib[target_attrib]
        if current_value == action_value:
            CommonUtil.ExecLog(sModuleInfo, ">>> The current attribute value '%s' is already set to the target value." %current_value, 1)
            return "Default"
        
        elif current_value != action_value:
            CommonUtil.ExecLog(sModuleInfo, ">>> The current attribute value is: '%s'" %current_value, 1)
        
        else:
            CommonUtil.ExecLog(sModuleInfo, ">>> Unable to find the target attribute. Please check the data set(s)." , 1)
            
        if action_name == "update":
            #Function to replace the target attribute value of XML tree with the user provided action value
            matching_elements.attrib[target_attrib] = action_value
            CommonUtil.ExecLog(sModuleInfo, ">>> Updating the attribute value in the XML File...", 1)
        
        else:
            CommonUtil.ExecLog(sModuleInfo, ">>> Unable to find the action name. Please check the data set(s).", 1)
  
        #Function the write the user provided action value in the XML file
        returned_action_value = update_action_value(file_path, doc) 
        CommonUtil.ExecLog(sModuleInfo, ">>> The current attribute value updated to the expected value '%s'" %action_value, 1)
        
        return returned_action_value
        
    except Exception:
        errMsg = "Unable to update the target element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

def update_action_value(file_path, doc):
    '''
     Function the write the user provided action value in the XML file
    '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: update_action_value", 1)
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        
        #Function to write the action value in the XML file
        doc.write(file_path) 
        CommonUtil.ExecLog(sModuleInfo, ">>> Writing the attribute value in the XML File...", 1)
        
        return "Passed"

    except Exception:
        errMsg = "Unable to update the action element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'===================== ===x=== ======================'