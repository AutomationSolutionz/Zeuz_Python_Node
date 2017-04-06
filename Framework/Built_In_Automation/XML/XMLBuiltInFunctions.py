'''
Created on Mar 30, 2017

@author: mchowdhury
'''
import sys, inspect
from Framework.Utilities import CommonUtil
from xml.etree import ElementTree as ET

local_run = True

'''Constants'''
passed_tag_list = ['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True',True,1,'1','Success','success','SUCCESS']
failed_tag_list = ['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE',False,0,'0']
default_tag_list = ['Default', 'default', 'DEFAULT', 'Unchanged', 'unchanged', 'UNCHAGED']

update_tag_list = ['Update', 'update', 'UPDATE', 'Replace', 'replace', 'REPLACE' ] #Update/replace existing element(s)
delete_tag_list = ['Delete', 'delete', 'DELETE', 'Remove', 'remove', 'REMOVE' ] #Delete existing line or element(s)
read_tag_list = ['Read', 'read', 'READ'] #Read existing element(S)
add_tag_list = ['Add', 'add', 'ADD'] #Add additional line or element(s)


##
# This function perform the sequential actions on step-data(s) of XML file
# Called by: xml_sequential_actions drivedr function
#
# @param step_data is a set of data extract from the Automation Framework 
# and performs the actions process it XML file
#
# @return the process result 'pass' or 'fail'
def sequential_actions_xml(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: sequential_actions_xml", 1,local_run)
    try:          
        for each in step_data:
            for row in each:
                if (row[1] == "filepath"):
                    continue

                # Finding what to do with each data set
                elif ((row[1] == "reference parameter") or (row[1] == "element parameter") or (row[1] == "target parameter")):            
                    continue
                
                # Finding what to do with action data set
                elif (row[1] == "action"):
                    CommonUtil.ExecLog(sModuleInfo, "Checking the action to be performed in the action row...", 1,local_run)
                    
                    action_result = action_handler([each],row[0], row[2])
                    if action_result == [] or action_result == "Failed":
                        return "Failed"
                
                else:
                    CommonUtil.ExecLog(sModuleInfo, "The sub-field information is incorrect. Please provide accurate information in the data set(s).", 3,local_run)
                    return "Failed"
                                
        return "Passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

##
# Function to perform actions for the sequential logic based on the input in the data_set
# Called by: <action_result> in sequential_actions_xml function
#
# @param action_step_data is a set of data provided by the user 
# @param action_name provide the respective action perform on the target element
# @param action_value is the expected result of respective target element
#
# @return the process result 'pass' or 'fail'
def action_handler(action_step_data, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: action_handler", 1,local_run)
    try:
        if action_name in update_tag_list: # Get action element(s)
            result = update_element(action_step_data, action_name, action_value)
            
            if result in failed_tag_list:
                return "Failed"               
            
        elif action_name in read_tag_list: # Get action element(s)
            result = read_element(action_step_data)
             
            if result in failed_tag_list:
                return "Failed"  
        
        # not ready yet
        elif action_name in delete_tag_list: # Get action element(s)
            result = delete_element(action_step_data, action_name, action_value)
             
            if result in failed_tag_list:
                return "Failed"
            
        # not ready yet
        elif action_name in add_tag_list: # Get action element(s)
            result = delete_element(action_step_data, action_name, action_value)
             
            if result in failed_tag_list:
                return "Failed" 
            
        else:
            CommonUtil.ExecLog(sModuleInfo, "The action you entered is incorrect. Please provide accurate information in the data set(s).", 3,local_run)
            return "Failed"
        
        return result
    
    except Exception:
        errMsg = "Unable to process the action(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# Update the target element(s) of XML tree
# Called by: <result> in action_handler function
#
# @param step_data is a set of data provided by the user 
# @param action_name provide the respective action perform on the target element
# @param action_value is the expected result of respective target element
#
# @return the process result 'pass' or 'fail'
def update_element(step_data, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: update_element", 1,local_run)
    try:
        if (len(step_data) != 1):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3,local_run)
            return "Failed"
        
        else:
            element_step_data = get_element_step_data(step_data)
            returned_step_data = validate_step_data(element_step_data)
            if ((returned_step_data == []) or (returned_step_data in failed_tag_list)):
                return "Failed"
            
            else:
                returned_element = get_updated_element(action_name, action_value, returned_step_data)

                if ((returned_element == []) or (returned_element in failed_tag_list)): #if elements are failed or invalid
                    CommonUtil.ExecLog(sModuleInfo, "Unable to change the attribute value of '%s'" % returned_step_data[0], 1, local_run)
                    return "Failed"
                        
                elif returned_element in default_tag_list: #if elements are default
                    CommonUtil.ExecLog(sModuleInfo, "Nothing to change the attribute value of '%s'" % returned_step_data[0], 1, local_run)
                    return "Passed"
                        
                else: #if elements are valid and passed
                    CommonUtil.ExecLog(sModuleInfo, "Updated the target attribute value of '%s'" % returned_step_data[0], 1, local_run)
 
                    #Validating updated target attribute
                    element_validated = validate_updated_element(action_name, action_value, returned_step_data)
                    if element_validated in passed_tag_list:
                        CommonUtil.ExecLog(sModuleInfo, "Validated the target attribute value of %s " % returned_step_data[0], 1, local_run)
                        return "Passed"
                              
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "Unable to validate the target attribute value of %s" % returned_step_data[0], 3, local_run)
                        return "Failed"
                    
    except Exception:
 
        errMsg = "Could not update the element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# Delete the existing target element from the XML tree
# Called by: <result> in action_handler function
#
# @param step_data is a set of data provided by the user 
# @param action_name provide the respective action perform on the target element
# @param action_value is the expected result of respective target element
#
# @return the process result 'pass' or 'fail'
def delete_element(step_data, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: delete_element", 1,local_run)
    try:
        element_step_data = get_element_step_data(step_data)
        returned_step_data = validate_step_data(element_step_data)
        if ((returned_step_data == []) or (returned_step_data in failed_tag_list)):
            CommonUtil.ExecLog(sModuleInfo, "Unable to get the file path: '%s'" % returned_step_data[0], 1, local_run)
            return "Failed"
            
        else:
            returned_element = get_updated_element(action_name, action_value, returned_step_data)

            if ((returned_element == []) or (returned_element in failed_tag_list)): #if elements are failed or invalid
                CommonUtil.ExecLog(sModuleInfo, "Unable to change the attribute value of '%s'" % returned_step_data[0], 1, local_run)
                return "Failed"
                        
            elif returned_element in default_tag_list: #if elements are default
                CommonUtil.ExecLog(sModuleInfo, "Nothing to change the attribute value of '%s'" % returned_step_data[0], 1, local_run)
                return "Passed"
                        
            else: #if elements are valid and passed
                CommonUtil.ExecLog(sModuleInfo, "Updated the target attribute value of '%s'" % returned_step_data[0], 1, local_run)
 
                #Validating updated target attribute
                element_validated = validate_updated_element(action_name, action_value, returned_step_data)
                if element_validated in passed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Validated the target attribute value of %s " % returned_step_data[0], 1, local_run)
                    return "Passed"
                              
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to validate the target attribute value of %s" % returned_step_data[0], 3, local_run)
                    return "Failed"

    except Exception:
 
        errMsg = "Unable to delete the element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# Read the elements of XML tree
# Called by: <result> in action_handler function
#
# @param step_data is a set of data provided by the user 
#
# @return the process result 'pass' or 'fail'
def read_element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: read_element", 1,local_run)
    try:
        if (len(step_data) != 1):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3,local_run)
            return "Failed"
        
        else:
            element_step_data = get_element_step_data(step_data)
            returned_step_data = validate_step_data(element_step_data)
            if ((returned_step_data == []) or (returned_step_data in failed_tag_list)):
                CommonUtil.ExecLog(sModuleInfo, "Unable to get the file path: '%s'" % returned_step_data[0], 1, local_run)
                return "Failed"
            
            else:
                returned_element = get_file_tree(returned_step_data[0])
                CommonUtil.ExecLog(sModuleInfo, "File tree of: %s" %(returned_step_data[0]), 1, local_run)
                CommonUtil.ExecLog(sModuleInfo, "%s" % ET.tostring(returned_element[0]), 1, local_run)
    
    except Exception:
        errMsg = "Unable to read the element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# Get all element step data(s) provided in the original step_data, except 'action(s)'
# Called by: <element_step_data> in update_element, read_element functions
#
# @param step_data is a set of data provided by the user 
#
# @return the added step data elements
def get_element_step_data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: get_element_step_data", 1,local_run)
    try:
        element_step_data=[]
        for each in step_data[0]:
            if (each[1]=="action"):
                continue
            
            else:
                element_step_data.append(each)
                 
        return element_step_data
    
    except Exception:
        errMsg = "Could not get element step data."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# Validate the step data passed on by the user in the original step_data
# Called by: <returned_step_data> in update_element, delete_element, read_element functions
#
# @param step_data is a set of data provided by the user 
#
# @return data contains: file_path, tree_level, target_element, target_value, reference_element, 
# reference_value, element_element, element_valuethe added step data elements
def validate_step_data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: validate_step_data", 1,local_run)
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
                    CommonUtil.ExecLog(sModuleInfo, "Unable to find elements requested.", 3,local_run)
            
        else:
            CommonUtil.ExecLog(sModuleInfo, "Data set incorrect. Please provide accurate data set(s) information.", 3,local_run)
            return "Failed"

        returned_data = (file_path, tree_level, target_element, target_value, reference_element, reference_value, element_element, element_value)
        return returned_data    
    
    except Exception:
        errMsg = "Could not find elements requested."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# Get updated element(s) based on action value in the original step_data
# Called by: <returned_element> in update_element and delete_element functions
#
# @param action_name provide the respective action perform on the target element
# @param action_value is the expected result of respective target element
# @param returned_step_data is a set of step data(s) after validation 
#
# @return data contains the process result after action(s), which contains 'default' or 'pass' or 'fail'
# 'default' means nothing to change, 'pass' means action success, 'fail' means action failed               
def get_updated_element(action_name, action_value, returned_step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: get_updated_element", 1,local_run)
    try:
        tree_level = returned_step_data[1]

        if (tree_level == "level 1"):
            returned_target_element = update_l1_target_element(returned_step_data[0], returned_step_data[2], returned_step_data[3], returned_step_data[4], returned_step_data[5], returned_step_data[6], returned_step_data[7], action_name, action_value)
            
        elif (tree_level == "level 2"):
            returned_target_element = update_l2_target_element(returned_step_data[0], returned_step_data[2], returned_step_data[3], returned_step_data[4], returned_step_data[5], returned_step_data[6], returned_step_data[7], action_name, action_value)
         
        elif (tree_level == "level 3"):
            returned_target_element = update_l3_target_element(returned_step_data[0], returned_step_data[2], returned_step_data[3], returned_step_data[4], returned_step_data[5], returned_step_data[6], returned_step_data[7], action_name, action_value)
        
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to update target element...", 3,local_run)
            return "Failed" 
        
        return returned_target_element   

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

##
# Updated the target element(s) which is in level one
# Called by: <returned_target_element> in get_updated_element function
#
# @param file_path provide the target location of the XML file 
# @param target_element is the target tag or attribute
# @param target_value contains target attribute or value
# @param reference_element is the parent  tag or attribute
# @param reference_value contains parent tag or attribute or value
# @param element_element is the child attribute
# @param reference_value contains child value
# @param action_name provide the respective action perform on the target element
# @param action_value is the expected result of respective target element
#
# @return data contains the process result after action(s), which contains 'default' or 'pass' or 'fail'
# 'default' means nothing to change, 'pass' means action success, 'fail' means action failed  
def update_l1_target_element(file_path, target_element, target_value, reference_element, reference_value, element_element, element_value, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: update_l1_target_element", 1,local_run)
    try:
        file_tree = []
        file_tree = get_file_tree(file_path) #get the xml file tree
    
        desired = file_tree[0].findall("%s[@%s]"%(target_element, target_value))
        CommonUtil.ExecLog(sModuleInfo, "The expected attribute value is '%s'" % action_value, 1, local_run)
        
        target_attrib = target_value
        returned_target_attribute = update_target_attribute(file_path, file_tree[1], desired, target_attrib, target_value, action_name, action_value)
        
        return returned_target_attribute
    
    except Exception:
        errMsg = "Unable to update the level 1 element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# Updated the target element(s) which is in level two
# Called by: <returned_target_element> in get_updated_element function
#
# @param file_path provide the target location of the XML file 
# @param target_element is the target tag or attribute
# @param target_value contains target attribute or value
# @param reference_element is the parent  tag or attribute
# @param reference_value contains parent tag or attribute or value
# @param element_element is the child attribute
# @param reference_value contains child value
# @param action_name provide the respective action perform on the target element
# @param action_value is the expected result of respective target element
#
# @return data contains the process result after action(s), which contains 'default' or 'pass' or 'fail'
# 'default' means nothing to change, 'pass' means action success, 'fail' means action failed  
def update_l2_target_element(file_path, target_element, target_value, reference_element, reference_value, element_element, element_value, action_name, action_value):
    ''' Function to update the L2 target element(s) based on action elements
    Called by: <returned_target_element> in get_updated_element function '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: update_l2_target_element", 1,local_run)
    try:
        file_tree = []
        file_tree = get_file_tree(file_path) #get the xml file tree

        if (element_element == False and element_value == False):
            desired = file_tree[0].findall(".//*[@%s='%s']/*[@%s]" %(reference_element, reference_value, target_element))
            CommonUtil.ExecLog(sModuleInfo, "The expected attribute value is '%s'" % action_value, 1, local_run)
            
            target_attrib = target_element
                        
        else:
            desired = file_tree[0].findall(".//*[@%s='%s']/*[@%s='%s']" %(reference_element, reference_value, element_element, element_value))
            CommonUtil.ExecLog(sModuleInfo, "The expected attribute value is '%s'" % action_value, 1, local_run)
            
            target_attrib = target_value


        returned_target_attribute = update_target_attribute(file_path, file_tree[1], desired, target_attrib, target_value, action_name, action_value)
        return returned_target_attribute

    except Exception:
        errMsg = "Unable to update the level 2 element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# Updated the target element(s) which is in level three
# Called by: <returned_target_element> in get_updated_element function
#
# @param file_path provide the target location of the XML file 
# @param target_element is the target tag or attribute
# @param target_value contains target attribute or value
# @param reference_element is the parent  tag or attribute
# @param reference_value contains parent tag or attribute or value
# @param element_element is the child attribute
# @param reference_value contains child value
# @param action_name provide the respective action perform on the target element
# @param action_value is the expected result of respective target element
#
# @return data contains the process result after action(s), which contains 'default' or 'pass' or 'fail'
# 'default' means nothing to change, 'pass' means action success, 'fail' means action failed  
def update_l3_target_element(file_path, target_element, target_value, reference_element, reference_value, element_element, element_value, action_name, action_value):
    ''' Function to update the L3 target element(s) based on action elements
    Called by: <returned_target_element> in get_updated_element function '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: update_l3_target_element", 1,local_run)
    try:
        file_tree = []
        file_tree = get_file_tree(file_path) #get the xml file tree
        
        if (element_element == False and element_value == False):
            desired = file_tree[0].findall(".//*[@%s='%s']//*[@%s]" %(reference_element, reference_value, target_element))
            CommonUtil.ExecLog(sModuleInfo, "The expected attribute value is '%s'" % action_value, 1, local_run)
            
            target_attrib = target_element

        else:        
            desired = file_tree[0].findall(".//*[@%s='%s']//*[@%s='%s']" %(reference_element, reference_value, element_element, element_value))
            CommonUtil.ExecLog(sModuleInfo, "The expected attribute value is '%s'" % action_value, 1, local_run)
            
            target_attrib = target_value
        
        returned_target_attribute = update_target_attribute(file_path, file_tree[1], desired, target_attrib, target_value, action_name, action_value)
        return returned_target_attribute

    except Exception:
        errMsg = "Unable to update the level 3 element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# Get the tree of XML tree without deleting any user comment(s)
# Called by: <file_tree> in update_lx_target_element and validated_lx_target_element functions
#
# @param file_path provide the target location of the XML file 
#
# @return data contains file parse and XML tree 
def get_file_tree(file_path):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: get_file_tree", 1,local_run)
    try:
        doc = ET.parse(file_path, XMLParser())
        tree = doc.getroot()
#         CommonUtil.ExecLog(sModuleInfo, "%s" % ET.tostring(tree), 1, local_run)

        return (tree, doc)

    except Exception:
        errMsg = "Unable to get the file tree."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# Handle the user comments in the parse XML tree
# Called by: <doc> in get_file_tree function
#
# @param XMLTreeBuilder, built in Python function
#
# @return user comments in the XML tree
class XMLParser(ET.XMLTreeBuilder):
     
    def __init__(self):
        ET.XMLTreeBuilder.__init__(self)
        self._parser.CommentHandler = self.handle_comment
  
    def handle_comment(self, data):
        self._target.start(ET.Comment, {})
        self._target.data(data)
        self._target.end(ET.Comment)

##
# Updated the target attribute
# Called by: <returned_target_attribute> in update_lx_target_element functions
#
# @param file_path provide the target location of the XML file
# @param doc contains tree parse
# @param desired contains target element(s)
# @param target_attributr is the target element or value
# @param target_value contains target attribute or value
# @param action_name provide the respective action perform on the target element
# @param action_value is the expected result of respective target element
#
# @return data contains 'default' or 'pass' or 'fail'
# 'default' means nothing to change, 'pass' means action success, 'fail' means action failed 
def update_target_attribute(file_path, doc, desired, target_attrib, target_value, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: update_target_attribute", 1,local_run)
    try:
        for each in desired:
            current_value = each.attrib[target_attrib]
            
            if current_value == action_value:
                CommonUtil.ExecLog(sModuleInfo, "The current attribute value '%s' is already set to the target value." %current_value, 1, local_run)
                return "Default"
            
            elif len(desired) > 1:
                if current_value == target_value:
                    CommonUtil.ExecLog(sModuleInfo, "The current attribute value is '%s'" %current_value, 1, local_run)
                else:
                    continue
                
            elif len(desired) == 1:
                if current_value != action_value:
                    CommonUtil.ExecLog(sModuleInfo, "The current attribute value is '%s'" % current_value, 1, local_run)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Unable to find the target attribute. Please check the data set(s).", 1, local_run)  
                      
            else:
                CommonUtil.ExecLog(sModuleInfo, "Unable to find the target element. Please check the data set(s) and/or XML File.", 1, local_run)
                return "Failed"
            
            if action_name == "update":
                each.set(target_attrib, action_value)
                CommonUtil.ExecLog(sModuleInfo, "Updating the attribute value in the XML File...", 1, local_run)
            else:
                CommonUtil.ExecLog(sModuleInfo, "Unable to find the action name. Please check the data set(s).", 1, local_run)
 
            returned_action_value = update_action_value(file_path, doc)
            CommonUtil.ExecLog(sModuleInfo, "The current attribute value updated to the expected value '%s'." % action_value, 1, local_run)
                 
            return returned_action_value

    except Exception:
        errMsg = "Unable to update the target element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

# Updated the target action value
# Called by: <returned_action_value> in update_target_attribute function
#
# @param file_path provide the target location of the XML file
# @param doc contains tree parse
#
# @return contains 'pass' result
def update_action_value(file_path, doc):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: update_action_value", 1,local_run)
    try:
        doc.write(file_path)
        CommonUtil.ExecLog(sModuleInfo, "Writing the attribute value in the XML File...", 1, local_run)
        
        return "Passed"

    except Exception:
        errMsg = "Unable to update the action element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# Validate updated element(s) based on action value in the original step_data
# Called by: <element_validated> in update_element and delete_element functions
#
# @param action_name provide the respective action perform on the target element
# @param action_value is the expected result of respective target element
# @param returned_step_data is a set of step data(s) after validation 
#
# @return contains 'pass' or 'fail' result 
def validate_updated_element(action_name, action_value, returned_step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: validate_updated_element", 1,local_run)
    try:
        tree_level = returned_step_data[1]
        if (tree_level == "level 1"):
            validated_element = validate_l1_target_element(returned_step_data[0], returned_step_data[2], returned_step_data[3], returned_step_data[4], returned_step_data[5], returned_step_data[6], returned_step_data[7], action_name, action_value)

        elif (tree_level == "level 2"):
            validated_element = validate_l2_target_element(returned_step_data[0], returned_step_data[2], returned_step_data[3], returned_step_data[4], returned_step_data[5], returned_step_data[6], returned_step_data[7], action_name, action_value)
        
        elif (tree_level == "level 3"):
            validated_element = validate_l3_target_element(returned_step_data[0], returned_step_data[2], returned_step_data[3], returned_step_data[4], returned_step_data[5], returned_step_data[6], returned_step_data[7], action_name, action_value)
        
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to validate target element...", 3,local_run)
            return "Failed" 
        
        return validated_element
    
    except Exception:
        errMsg = "Could not validate the updated element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg) 

##
# Validate the target element(s) which is in level one
# Called by: <validated_element> in validate_updated_element function
#
# @param file_path provide the target location of the XML file 
# @param target_element is the target tag or attribute
# @param target_value contains target attribute or value
# @param reference_element is the parent  tag or attribute
# @param reference_value contains parent tag or attribute or value
# @param element_element is the child attribute
# @param reference_value contains child value
# @param action_name provide the respective action perform on the target element
# @param action_value is the expected result of respective target element
#
# @return contains 'pass' or 'fail' result 
def validate_l1_target_element(file_path, target_element, target_value, reference_element, reference_value, element_element, element_value, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: validate_l1_target_element", 1,local_run)
    try:
        file_tree = []
        file_tree = get_file_tree(file_path) #get the xml file tree

        desired = file_tree[0].findall("%s" %(target_element))
        target_attrib = target_value
        
        returned_validated_attribute = validate_target_attribute(desired, target_attrib, action_name, action_value)
        return returned_validated_attribute

    except Exception:
        errMsg = "Unable to validate updated the level 1 element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# Validate the target element(s) which is in level two
# Called by: <validated_element> in validate_updated_element function
#
# @param file_path provide the target location of the XML file 
# @param target_element is the target tag or attribute
# @param target_value contains target attribute or value
# @param reference_element is the parent  tag or attribute
# @param reference_value contains parent tag or attribute or value
# @param element_element is the child attribute
# @param reference_value contains child value
# @param action_name provide the respective action perform on the target element
# @param action_value is the expected result of respective target element
#
# @return contains 'pass' or 'fail' result 
def validate_l2_target_element(file_path, target_element, target_value, reference_element, reference_value, element_element, element_value, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: validate_l2_target_element", 1,local_run)
    try:
        file_tree = []
        file_tree = get_file_tree(file_path) #get the xml file tree

        if (element_element == False and element_value == False):
            desired = file_tree[0].findall(".//*[@%s='%s']/*[@%s]" %(reference_element, reference_value, target_element))
            target_attrib = target_element
                        
        else:
            desired = file_tree[0].findall(".//*[@%s='%s']/*[@%s='%s']" %(reference_element, reference_value, element_element, element_value))
            target_attrib = target_value
        
        returned_validated_attribute = validate_target_attribute(desired, target_attrib, action_name, action_value)
        return returned_validated_attribute

    except Exception:
        errMsg = "Unable to validate updated the level 2 element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# Validate the target element(s) which is in level three
# Called by: <validated_element> in validate_updated_element function
#
# @param file_path provide the target location of the XML file 
# @param target_element is the target tag or attribute
# @param target_value contains target attribute or value
# @param reference_element is the parent  tag or attribute
# @param reference_value contains parent tag or attribute or value
# @param element_element is the child attribute
# @param reference_value contains child value
# @param action_name provide the respective action perform on the target element
# @param action_value is the expected result of respective target element
#
# @return contains 'pass' or 'fail' result 
def validate_l3_target_element(file_path, target_element, target_value, reference_element, reference_value, element_element, element_value, action_name, action_value):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: validate_l3_target_element", 1,local_run)
    try:
        file_tree = []
        file_tree = get_file_tree(file_path) #get the xml file tree
        
        if (element_element == False and element_value == False):
            desired = file_tree[0].findall(".//*[@%s='%s']//*[@%s]" %(reference_element, reference_value, target_element))
            target_attrib = target_element

        else:        
            desired = file_tree[0].findall(".//*[@%s='%s']//*[@%s='%s']" %(reference_element, reference_value, element_element, element_value))
            target_attrib = target_value
        
        returned_validated_attribute = validate_target_attribute(desired, target_attrib, action_name, action_value)
        return returned_validated_attribute

    except Exception:
        errMsg = "Unable to validate updated the level 3 element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# Validate the target attribute
# Called by: <returned_validated_attribute> in validate_lx_target_element functions
#
# @param desired contains target element(s)
# @param target_attributr is the target element or value
# @param action_name provide the respective action perform on the target element
# @param action_value is the expected result of respective target element
#
# @return 'pass' or 'fail'
def validate_target_attribute(desired, target_attrib, action_name, action_value):
    ''' Function to validate the target value
    Called by: <returned_validated_attribute> in validae_l1_target_element validate_l2_target_element and validate_l3_target_element functions '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: validate_target_attribute", 1,local_run)
    try:
        if (len(desired) == 1 or len(desired) > 1):
            for each in desired:
                current_value = each.attrib[target_attrib]
            
                if current_value == action_value:
                    CommonUtil.ExecLog(sModuleInfo, "Validated the action value is set to the target element: '%s'." %current_value, 1, local_run) 
                    return "Passed"
            
                else:
                    continue
            
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to find the updated target element.", 1, local_run)
            return "Failed"

    except Exception:
        errMsg = "Unable to validate updated target element(s)."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

##
# This driver function perform the sequential actions on step-data(s) of XML file
#
# @param step_data is a set of data extract from the Automation Framework 
#
# @return the function result pass or fail
def xml_sequential_actions(step_data):
    ''' This is the main function of XML file, which provide 
    the step_data(s) to it's child function and get the result(s) '''
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function: xml_sequential_actions",1,local_run)
    try:
        sTestStepReturnStatus = sequential_actions_xml(step_data)
        if sTestStepReturnStatus in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Exit: Sequential Actions Passed",1,local_run)
            return sTestStepReturnStatus
        
        elif sTestStepReturnStatus in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Exit: Sequential Actions Failed",1,local_run)
            return sTestStepReturnStatus
        
        else:
            CommonUtil.ExecLog(sModuleInfo,"Step return type unknown: '%s'" %(sTestStepReturnStatus),1,local_run)
            CommonUtil.ExecLog(sModuleInfo,"Exit: Sequential Actions",1,local_run)

            return "failed"
    
    except Exception:
        errMsg = "Unable to perform action on target element."
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)


''' Local run '''
# android_suite-qc.xml -> target + action: Test-1712
# step_data = [ [ ( 'level 1' , 'filepath' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/qa_latest/android_suite-qc.xml' , False , False , '' ) , ( 'TestSuite' , 'target parameter' , 'operatorAuditThreshold' , False , False , '' ) , ( 'update' , 'action' , '1' , False , False , '' ) ] ]

#assetscience-refurb.ini'
# step_data = [ [ ( 'level 1' , 'filepath' , '/home/asci/AssetScience/recell_dse-candidate/assetscience-refurb.ini' , False , False , '' ) , ( 'ServerSync' , 'target parameter' , False , False , False , '' ) , ( 'update' , 'action' , 'True' , False , False , '' ) ] ]


# serviceSuiteDefinitionFile.xml -> reference + target + action: Test-2291
# step_data = [ [ ( 'level 2' , 'filepath' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/serviceSuiteDefinitionFile.xml' , False , False , '' ) , ( 'identifier' , 'reference parameter' , 'DiagnosticsQuickSuite' , False , False , '' ) , ( 'class' , 'target parameter' , 'RunDiagnostics' , False , False , '' ) , ( 'update' , 'action' , 'RunDiagnostics-update' , False , False , '' ) ] ]
# serviceDefinitionFile.xml -> reference + element + target + action: Test-2099
# step_data = [ [ ( 'level 2' , 'filepath' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/serviceDefinitionFile.xml' , False , False , '' ) , ( 'identifier' , 'reference parameter' , 'ApplicationInstall' , False , False , '' ) , ( 'name' , 'element parameter' , 'appIOS' , False , False , '' ) , ( 'Argument' , 'target parameter' , 'value' , False , False , '' ) , ( 'update' , 'action' , 'pro-diagnostics-17.3.4.ipa' , False , False , '' ) ] ]

# Teleplan.xml -> target + action: Test- ??
# step_data = [ [ ( 'level 3' , 'filepath' , '/home/asci/AssetScience/Generic/Teleplan_21212121212122_20170228083953.xml' , False , False , '' ) , ( 'read' , 'action' , False , False , False , '' ) ] ]

# failcodes.xml -> reference + target + action
step_data = [ [ ( 'level 3' , 'filepath' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/qa_latest/failcodes.xml' , False , False , '' ) , ( 'name' , 'reference parameter' , 'General Test Failure' , False , False , '' ) , ( 'name' , 'target parameter' , 'ICloudTest' , False , False , '' ) , ( 'update' , 'action' , 'ICloudTest-update' , False , False , '' ) ] ]
# android_testdefinitions.xml -> reference + element + target + action:Test-2336
# step_data = [ [ ( 'level 3' , 'filepath' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/qa_latest/android_testdefinitions.xml' , False , False , '' ) , ( 'customerIdentifier' , 'reference parameter' , 'HeadsetStereoTest' , False , False , '' ) , ( 'mode' , 'element parameter' , 'MuteBothChannel' , False , False , '' ) , ( 'AuditMode' , 'target parameter' , 'enabled' , False , False , '' ) , ( 'update' , 'action' , 'false' , False , False , '' ) ] ]

xml_sequential_actions(step_data)