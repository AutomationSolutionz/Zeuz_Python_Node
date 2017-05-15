# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

'''
Created on Mar 30, 2017

@author: mchowdhury
Comment: Not published yet
'''

import sys, inspect
from Framework.Utilities import CommonUtil
from xml.etree import ElementTree as ET


'''Constants'''
passed_tag_list = ['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True',True,1,'1','Success','success','SUCCESS']
failed_tag_list = ['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE',False,0,'0']
default_tag_list = ['Default', 'default', 'DEFAULT', 'Unchanged', 'unchanged', 'UNCHAGED']

update_tag_list = ['Update', 'update', 'UPDATE', 'Replace', 'replace', 'REPLACE' ] #Update/replace existing element(s)
delete_tag_list = ['Delete', 'delete', 'DELETE', 'Remove', 'remove', 'REMOVE' ] #Delete existing line or element(s)
read_tag_list = ['Read', 'read', 'READ'] #Read existing element(s)
add_tag_list = ['Add', 'add', 'ADD'] #Add additional line(s) or element(s)


'===================== ===x=== Sequential Action Section Starts ===x=== ======================'
'''
 This function perform the sequential actions on step-data(s) of XML file '''
def xml_sequential_actions(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: xml_sequential_actions", 1)
    try:          
        for each in step_data:
            for row in each:
                if (row[1] == "filepath"): #Looking for file path
                    continue

                #Looking for element parameters
                elif ((row[1] == "reference parameter") or (row[1] == "element parameter") or (row[1] == "target parameter")):            
                    continue
                
                #Looking for action(s) provided in the user data
                elif (row[1] == "action"):
                    CommonUtil.ExecLog(sModuleInfo, "Checking the action to be performed in the action row...", 1)

                    action_result = action_handler([each],row[0], row[2])
                    if action_result == [] or action_result == "Failed":
                        return "Failed"

                # If middle column = optional action, call action handler, but always return a pass
                elif row[1] == "optional action":
                    CommonUtil.ExecLog(sModuleInfo,"Checking the optional action to be performed in the action row: %s" % str(row), 1)
                    result = action_handler(each, row[0], row[2])  # Pass data set, and action_name to action handler
                    if result == 'failed':
                        CommonUtil.ExecLog(sModuleInfo, "Optional action failed. Returning pass anyway", 2)
                    result = 'passed'
                
                else:
                    CommonUtil.ExecLog(sModuleInfo, "The sub-field information is incorrect. Please provide accurate information in the data set(s).", 3)
                    return "Failed"
                                
        return "Passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

'===================== ===x=== Sequential Action Section Ends ===x=== ======================'


'===================== ===x=== Action Handler Starts ===x=== ======================'
'''
 Function to perform actions for the sequential logic based on the input in the data_set '''
def action_handler(action_step_data, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: action_handler", 1)
    try:
        if action_name in update_tag_list: #Perform the update action
            result = update_element(action_step_data, action_name, action_value)
            
            if result in failed_tag_list:
                return "Failed"               
            
        elif action_name in read_tag_list: #Perform the read action
            result = read_element(action_step_data)
             
            if result in failed_tag_list:
                return "Failed"  
        
        # not ready yet
        elif action_name in delete_tag_list: #Perform the delete action
            result = delete_element(action_step_data, action_name, action_value)
             
            if result in failed_tag_list:
                return "Failed"
            
        # not ready yet
        elif action_name in add_tag_list: #Perform the add action
            result = delete_element(action_step_data, action_name, action_value)
             
            if result in failed_tag_list:
                return "Failed" 
            
        else:
            CommonUtil.ExecLog(sModuleInfo, "The action you entered is incorrect. Please provide accurate information in the data set(s).", 3)
            return "Failed"
        
        return result
    
    except Exception:
        errMsg = "Unable to process the action(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'''
 Function to update the target element(s) of XML tree '''
def update_element(step_data, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: update_element", 1)
    try:
        if (len(step_data) != 1): #Verifies that length of step_data greater than one
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "Failed"
        
        else: 
            #Function to collect the user provided step data elements 
            element_step_data = get_element_step_data(step_data)
            
            #Function to validate the user provided step data elements 
            returned_step_data = validate_step_data(element_step_data) 
            if ((returned_step_data == []) or (returned_step_data in failed_tag_list)):
                return "Failed"
            
            else:
                #Function to update the target element(s) as per 'action' 
                returned_element = get_target_element(action_name, action_value, returned_step_data) 

                if ((returned_element == []) or (returned_element in failed_tag_list)): #if failed to update target elements
                    CommonUtil.ExecLog(sModuleInfo, "Unable to change the attribute value of '%s'" % returned_step_data[0], 1)
                    return "Failed"
                        
                elif returned_element in default_tag_list: #if target elements are same as expected elements
                    CommonUtil.ExecLog(sModuleInfo, "Nothing to change the attribute value of '%s'" % returned_step_data[0], 1)
                    return "Passed"
                        
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Updated the target attribute value of '%s'" % returned_step_data[0], 1)
 
                    #Function to verify/validate that element(s) in the XML file updated properly
                    element_validated = validate_target_element(action_name, action_value, returned_step_data) 
                    if element_validated in passed_tag_list:
                        CommonUtil.ExecLog(sModuleInfo, "Validated the target attribute value of %s " % returned_step_data[0], 1)
                        return "Passed"
                              
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "Unable to validate the target attribute value of %s" % returned_step_data[0], 3)
                        return "Failed"
                    
    except Exception:
 
        errMsg = "Could not update the element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

###
# Function to delete the target element(s) of XML tree
''' This delete function not ready yet '''
def delete_element(step_data, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: delete_element", 1)
    try:
        #Function to collect the user provided step data elements 
        element_step_data = get_element_step_data(step_data) 
        
        #Function to validate the user provided step data elements 
        returned_step_data = validate_step_data(element_step_data) 
        if ((returned_step_data == []) or (returned_step_data in failed_tag_list)):
            CommonUtil.ExecLog(sModuleInfo, "Unable to get the file path: '%s'" % returned_step_data[0], 1)
            return "Failed"
            
        else:
            #Function to update the target element(s) as per 'action' 
            returned_element = get_target_element(action_name, action_value, returned_step_data) 

            if ((returned_element == []) or (returned_element in failed_tag_list)): #if failed to delete target elements
                CommonUtil.ExecLog(sModuleInfo, "Unable to change the attribute value of '%s'" % returned_step_data[0], 1)
                return "Failed"
                        
            elif returned_element in default_tag_list: #if target elements are same as expected elements
                CommonUtil.ExecLog(sModuleInfo, "Nothing to change the attribute value of '%s'" % returned_step_data[0], 1)
                return "Passed"
                        
            else: #if elements are deleted properly
                CommonUtil.ExecLog(sModuleInfo, "Updated the target attribute value of '%s'" % returned_step_data[0], 1)
 
                #Function to verify/validate that element(s) in the XML file updated properly
                element_validated = validate_target_element(action_name, action_value, returned_step_data)
                if element_validated in passed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Validated the target attribute value of %s " % returned_step_data[0], 1)
                    return "Passed"
                              
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to validate the target attribute value of %s" % returned_step_data[0], 3)
                    return "Failed"

    except Exception:
 
        errMsg = "Unable to delete the element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'''
 Function to read the elements from XML file '''
def read_element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: read_element", 1)
    try:
        if (len(step_data) != 1): #Verifies that length of step_data greater than one
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "Failed"
        
        else:
            #Function to collect the user provided step data elements 
            element_step_data = get_element_step_data(step_data) 
            
            #Function to validate the user provided step data elements 
            returned_step_data = validate_step_data(element_step_data) 
            if ((returned_step_data == []) or (returned_step_data in failed_tag_list)):
                CommonUtil.ExecLog(sModuleInfo, "Unable to get the file path: '%s'" % returned_step_data[0], 1)
                return "Failed"
            
            else:
                #Function to get the XML file tree
                returned_element = get_file_tree(returned_step_data[0]) 
                CommonUtil.ExecLog(sModuleInfo, "File tree of: %s" %(returned_step_data[0]), 1)
                CommonUtil.ExecLog(sModuleInfo, "%s" % ET.tostring(returned_element[0]), 1)
    
    except Exception:
        errMsg = "Unable to read the element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'===================== ===x=== Action Handler Ends ===x=== ======================'


'===================== ===x=== Get Elements From Step Data Starts ===x=== ======================'

'''
 Function to collect user provided step data elements '''
def get_element_step_data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: get_element_step_data", 1)
    try:
        element_step_data=[]
        for each in step_data[0]:
            if (each[1]=="action"):
                continue
            
            else:
                #ElementTree function to append the elements from each lines of step data except 'action' line
                element_step_data.append(each) 
                 
        return element_step_data
    
    except Exception:
        errMsg = "Could not get element step data."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'''
 Function to validate user provided step data elements '''
def validate_step_data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: validate_step_data", 1)
    try:
        reference_element = False
        reference_value = False
        element_element = False
        element_value = False
        target_element = False
        target_value = False
        if (len(step_data) >= 1):
            for each in step_data:
                if (each[1] == "filepath"):
                    file_path = each[2]
                    tree_level = each[0]
                    
                elif (each[1]=="reference parameter"):
                    reference_element = each[0]
                    reference_value = each[2]
                    
                elif (each[1]=="element parameter"):
                    element_element = each[0]
                    element_value =each[2]

                elif each[1]=="target parameter":
                    target_element = each[0]
                    target_value = each[2]
                    
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to find elements requested.", 3)
            
        else:
            CommonUtil.ExecLog(sModuleInfo, "Data set incorrect. Please provide accurate data set(s) information.", 3)
            return "Failed"

        returned_data = (file_path, tree_level, target_element, target_value, reference_element, reference_value, element_element, element_value)
        return returned_data    
    
    except Exception:
        errMsg = "Could not find elements requested."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    
'===================== ===x=== Get Elements From Step Data Ends ===x=== ======================'


'===================== ===x=== Get Elements From File Starts ===x=== ======================'
'''
 Function to get the target element(s) as per 'action' '''           
def get_target_element(action_name, action_value, returned_step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: get_target_element", 1)
    try:
        tree_level = returned_step_data[1]

        if (tree_level == "level 1"): 
            #Function to get the level 1 target element(s)
            returned_target_element = get_l1_target_element(returned_step_data[0], returned_step_data[2], returned_step_data[3], returned_step_data[4], returned_step_data[5], returned_step_data[6], returned_step_data[7], action_name, action_value)
            
        elif (tree_level == "level 2"): 
            #Function to get the level 2 target element(s)
            returned_target_element = get_l2_target_element(returned_step_data[0], returned_step_data[2], returned_step_data[3], returned_step_data[4], returned_step_data[5], returned_step_data[6], returned_step_data[7], action_name, action_value)
         
        elif (tree_level == "level 3"): 
            #Function to get the level 3 target element(s)
            returned_target_element = get_l3_target_element(returned_step_data[0], returned_step_data[2], returned_step_data[3], returned_step_data[4], returned_step_data[5], returned_step_data[6], returned_step_data[7], action_name, action_value)
        
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to update target element...", 3)
            return "Failed" 
        
        return returned_target_element   

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

'''
 Function to get the level 1 target element(s) '''
def get_l1_target_element(file_path, target_element, target_value, reference_element, reference_value, element_element, element_value, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: get_l1_target_element", 1)
    try:
        file_tree = []
        #Function to get the XML file tree
        file_tree = get_file_tree(file_path) 
        
        #ElementTree function to get the parent matching level 1 target element(s)
        desired = file_tree[0].findall("%s[@%s]"%(target_element, target_value)) 
        CommonUtil.ExecLog(sModuleInfo, "The expected attribute value is '%s'" % action_value, 1)
        
        target_attrib = target_value
        
        #Function to update the target element
        returned_l1_target_element = update_target_element(file_path, file_tree[1], desired, target_attrib, target_value, action_name, action_value) 
        
        return returned_l1_target_element
    
    except Exception:
        errMsg = "Unable to update the level 1 element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'''
 Function to get the level 2 target element(s) '''
def get_l2_target_element(file_path, target_element, target_value, reference_element, reference_value, element_element, element_value, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: get_l2_target_element", 1)
    try:
        file_tree = []
        #Function to get the tree of XML file 
        file_tree = get_file_tree(file_path) 

        if (element_element == False and element_value == False):
            #ElementTree function to get the parent matching level 2 target element(s)
            desired = file_tree[0].findall(".//*[@%s='%s']/*[@%s]" %(reference_element, reference_value, target_element)) 
            CommonUtil.ExecLog(sModuleInfo, "The expected attribute value is '%s'" % action_value, 1)
            
            target_attrib = target_element
                        
        else:
            #ElementTree function to get the parent and child matching level 3 target element(s)
            desired = file_tree[0].findall(".//*[@%s='%s']/*[@%s='%s']" %(reference_element, reference_value, element_element, element_value)) 
            CommonUtil.ExecLog(sModuleInfo, "The expected attribute value is '%s'" % action_value, 1)
            
            target_attrib = target_value

        #Function to update the target element
        returned_l2_target_element = update_target_element(file_path, file_tree[1], desired, target_attrib, target_value, action_name, action_value) 
        return returned_l2_target_element

    except Exception:
        errMsg = "Unable to update the level 2 element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'''
 Function to get the level 3 target element(s) '''
def get_l3_target_element(file_path, target_element, target_value, reference_element, reference_value, element_element, element_value, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: get_l3_target_element", 1)
    try:
        file_tree = []
        #Function to get the XML file tree
        file_tree = get_file_tree(file_path) 
        
        if (element_element == False and element_value == False):
            #ElementTree function to get the parent matching level 3 target element(s)
            desired = file_tree[0].findall(".//*[@%s='%s']//*[@%s]" %(reference_element, reference_value, target_element)) 
            CommonUtil.ExecLog(sModuleInfo, "The expected attribute value is '%s'" % action_value, 1)
            
            target_attrib = target_element

        else:        
            #ElementTree function to get the parent and child matching level 3 target element(s)
            desired = file_tree[0].findall(".//*[@%s='%s']//*[@%s='%s']" %(reference_element, reference_value, element_element, element_value)) 
            CommonUtil.ExecLog(sModuleInfo, "The expected attribute value is '%s'" % action_value, 1)
            
            target_attrib = target_value
        
        #Function to update the target element
        returned_l3_target_element = update_target_element(file_path, file_tree[1], desired, target_attrib, target_value, action_name, action_value) 
        return returned_l3_target_element

    except Exception:
        errMsg = "Unable to update the level 3 element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'===================== ===x=== Get Elements From File Ends ===x=== ======================'


'===================== ===x=== File Reading Starts ===x=== ======================'
'''
 Function to get the XML file tree without deleting any user comment(s) '''
def get_file_tree(file_path):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: get_file_tree", 1)
    try:
        #ElementTree function to get the file parse
        doc = ET.parse(file_path, XMLParser()) 
        
        #ElementTree function to get the file tree
        tree = doc.getroot() 
#         CommonUtil.ExecLog(sModuleInfo, "%s" % ET.tostring(tree), 1)

        return (tree, doc)

    except Exception:
        errMsg = "Unable to get the file tree."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'''
 Class function to handle the user comments in the parse XML tree '''
class XMLParser(ET.XMLTreeBuilder):
     
    def __init__(self):
        ET.XMLTreeBuilder.__init__(self)
        self._parser.CommentHandler = self.handle_comment
    
    #ElementTree function to handle the comments in the XML file
    def handle_comment(self, data): 
        self._target.start(ET.Comment, {})
        self._target.data(data)
        self._target.end(ET.Comment)

'===================== ===x=== File Reading Ends ===x=== ======================'


'===================== ===x=== Update Element Starts ===x=== ======================'
'''
 Function to update the target element value '''
def update_target_element(file_path, doc, desired, target_attrib, target_value, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: update_target_element", 1)
    try:
        for each in desired:
            #ElementTree function to get the target attribute value
            current_value = each.attrib[target_attrib] 
            
            if current_value == action_value:
                CommonUtil.ExecLog(sModuleInfo, "The current attribute value '%s' is already set to the target value." %current_value, 1)
                return "Default"
            
            elif len(desired) > 1: #If more than one desired elements found
                if current_value == target_value:
                    CommonUtil.ExecLog(sModuleInfo, "The current attribute value is '%s'" %current_value, 1)
                else:
                    continue
                
            elif len(desired) == 1: #If only one desired elements found
                if current_value != action_value:
                    CommonUtil.ExecLog(sModuleInfo, "The current attribute value is '%s'" % current_value, 1)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to find the target attribute. Please check the data set(s).", 1)  
                      
            else:
                CommonUtil.ExecLog(sModuleInfo, "Unable to find the target element. Please check the data set(s) and/or XML File.", 1)
                return "Failed"
            
            if action_name == "update":
                #ElementTree function to replace the target attribute value of XML tree with the user provided action value
                each.set(target_attrib, action_value) 
                CommonUtil.ExecLog(sModuleInfo, "Updating the attribute value in the XML File...", 1)
            else:
                CommonUtil.ExecLog(sModuleInfo, "Unable to find the action name. Please check the data set(s).", 1)
 
            #Function the write the user provided action value in the XML file
            returned_action_value = update_action_value(file_path, doc) 
            CommonUtil.ExecLog(sModuleInfo, "The current attribute value updated to the expected value '%s'." % action_value, 1)
                 
            return returned_action_value

    except Exception:
        errMsg = "Unable to update the target element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'''
 Function the write the user provided action value in the XML file '''
def update_action_value(file_path, doc):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: update_action_value", 1)
    try:
        #ElementTree function to write the action value in the XML file
        doc.write(file_path) 
        CommonUtil.ExecLog(sModuleInfo, "Writing the attribute value in the XML File...", 1)
        
        return "Passed"

    except Exception:
        errMsg = "Unable to update the action element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'===================== ===x=== Update Element Ends ===x=== ======================'


'===================== ===x=== Validate Element Starts ===x=== ======================'
'''
 Function to verify/validate that element(s) in the XML file updated properly '''
def validate_target_element(action_name, action_value, returned_step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: validate_target_element", 1)
    try:
        tree_level = returned_step_data[1]
        if (tree_level == "level 1"): 
            #Function to validate the level 1 target element(s)
            validated_element = validate_l1_target_element(returned_step_data[0], returned_step_data[2], returned_step_data[3], returned_step_data[4], returned_step_data[5], returned_step_data[6], returned_step_data[7], action_name, action_value)

        elif (tree_level == "level 2"): 
            #Function to validate the level 2 target element(s)
            validated_element = validate_l2_target_element(returned_step_data[0], returned_step_data[2], returned_step_data[3], returned_step_data[4], returned_step_data[5], returned_step_data[6], returned_step_data[7], action_name, action_value)
        
        elif (tree_level == "level 3"): 
            #Function to validate the level 3 target element(s)
            validated_element = validate_l3_target_element(returned_step_data[0], returned_step_data[2], returned_step_data[3], returned_step_data[4], returned_step_data[5], returned_step_data[6], returned_step_data[7], action_name, action_value)
        
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to validate target element...", 3)
            return "Failed" 
        
        return validated_element
    
    except Exception:
        errMsg = "Could not validate the updated element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg) 

'''
 Function to validate the level 1 target element(s) '''
def validate_l1_target_element(file_path, target_element, target_value, reference_element, reference_value, element_element, element_value, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: validate_l1_target_element", 1)
    try:
        file_tree = []
        #Function to get the XML file tree
        file_tree = get_file_tree(file_path) 

        #ElementTree function to get the parent matching level 1 target element(s)
        desired = file_tree[0].findall("%s" %(target_element)) 
        target_attrib = target_value
        
        #Function to validate the target attribute value
        returned_validated_attribute = validate_target_attribute(desired, target_attrib, action_name, action_value) 
        return returned_validated_attribute

    except Exception:
        errMsg = "Unable to validate updated the level 1 element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'''
 Function to validate the level 2 target element(s) '''
def validate_l2_target_element(file_path, target_element, target_value, reference_element, reference_value, element_element, element_value, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: validate_l2_target_element", 1)
    try:
        file_tree = []
        #Function to get the XML file tree
        file_tree = get_file_tree(file_path) 

        if (element_element == False and element_value == False):
            #ElementTree function to get the parent matching level 2 target element(s)
            desired = file_tree[0].findall(".//*[@%s='%s']/*[@%s]" %(reference_element, reference_value, target_element)) 
            target_attrib = target_element
                        
        else:
            #ElementTree function to get the parent and child matching level 3 target element(s)
            desired = file_tree[0].findall(".//*[@%s='%s']/*[@%s='%s']" %(reference_element, reference_value, element_element, element_value)) 
            target_attrib = target_value
        
        #Function to validate the target attribute value
        returned_validated_attribute = validate_target_attribute(desired, target_attrib, action_name, action_value) 
        return returned_validated_attribute

    except Exception:
        errMsg = "Unable to validate updated the level 2 element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'''
 Function to validate the level 3 target element(s) '''
def validate_l3_target_element(file_path, target_element, target_value, reference_element, reference_value, element_element, element_value, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: validate_l3_target_element", 1)
    try:
        file_tree = []
        #Function to get the XML file tree
        file_tree = get_file_tree(file_path)
        
        if (element_element == False and element_value == False):
            #ElementTree function to get the parent matching level 2 target element(s)
            desired = file_tree[0].findall(".//*[@%s='%s']//*[@%s]" %(reference_element, reference_value, target_element)) 
            target_attrib = target_element

        else:        
            #ElementTree function to get the parent and child matching level 3 target element(s)
            desired = file_tree[0].findall(".//*[@%s='%s']//*[@%s='%s']" %(reference_element, reference_value, element_element, element_value)) 
            target_attrib = target_value
        
        #Function to validate the target attribute value
        returned_validated_attribute = validate_target_attribute(desired, target_attrib, action_name, action_value) 
        return returned_validated_attribute

    except Exception:
        errMsg = "Unable to validate updated the level 3 element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'''
 Function to validate the target attribute value '''
def validate_target_attribute(desired, target_attrib, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: validate_target_attribute", 1)
    try:
        if (len(desired) == 1 or len(desired) > 1): #If one or more than one desired elements found
            for each in desired:
                #ElementTree function to get the target attribute value
                current_value = each.attrib[target_attrib] 
            
                if current_value == action_value:
                    CommonUtil.ExecLog(sModuleInfo, "Validated the action value is set to the target element: '%s'." %current_value, 1) 
                    return "Passed"
            
                else:
                    continue
            
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to find the updated target element.", 1)
            return "Failed"

    except Exception:
        errMsg = "Unable to validate updated target element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

'===================== ===x=== Validate Element Ends ===x=== ======================'

