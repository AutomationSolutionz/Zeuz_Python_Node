'''
    Sequential Actions - Main Functions
    Function: Handles incoming step data and distributes it to the specified functions
    
    Instructions for adding new functionality
        Adding new actions:
            Add to the actions dictionary - module and name must be lowercase with single spaces, function should be the exact spelling of the function name
            
        Adding new Sub-Field keywords
            Add to the action_suport list - must be lowercase with single spaces
            
        Adding a new dynamically called module
            Add to the load_sa_modules() function, follow same format as other sections
'''

# Dictionary of supported actions and their respective modules
# Rules: Action NAME must be lower case, no underscores, single spaces, no trailing whitespace. Module names must match those used in load_sa_modules()
# Common module: These are functions that are common to multiple Built In Functions, which have special handling. See common_functions.py where they are stored for more information
# Caveat: Modules that are common to more than one built in function are listed here as with the module set to "common". If there is a "common" function, and another module with the same name created here, there may be a conflict, and the wrong function may execute
actions = { # Numbers are arbitrary, and are not used anywhere
    900: {'module': 'common', 'name': 'step result', 'function': 'step_result'},
    901: {'module': 'common', 'name': 'sleep', 'function': 'Sleep'},
    902: {'module': 'common', 'name': 'wait', 'function': 'Wait_For_Element'},
    903: {'module': 'common', 'name': 'wait disable', 'function': 'Wait_For_Element'},
    904: {'module': 'common', 'name': 'save text', 'function': 'Save_Text'},
    905: {'module': 'common', 'name': 'compare variable', 'function': 'Compare_Variables'},
    906: {'module': 'common', 'name': 'initialize list', 'function': 'Initialize_List'},
    907: {'module': 'common', 'name': 'compare list', 'function': 'Compare_Lists'},
    908: {'module': 'common', 'name': 'insert into list', 'function': 'Insert_Into_List'},
    
    100: {'module': 'appium', 'name': 'click', 'function': 'Click_Element_Appium'},
    101: {'module': 'appium', 'name': 'text', 'function': 'Enter_Text_Appium'},
    103: {'module': 'appium', 'name': 'tap', 'function': 'Tap_Appium'},
    104: {'module': 'appium', 'name': 'validate full text', 'function': 'Validate_Text_Appium'},
    105: {'module': 'appium', 'name': 'validate partial text', 'function': 'Validate_Text_Appium'},
    111: {'module': 'appium', 'name': 'install', 'function': 'install_application'},
    112: {'module': 'appium', 'name': 'launch', 'function': 'launch_application'},
    113: {'module': 'appium', 'name': 'get location', 'function': 'get_element_location_by_id'},
    115: {'module': 'appium', 'name': 'swipe', 'function': 'swipe_handler'},
    116: {'module': 'appium', 'name': 'close', 'function': 'close_application'},
    117: {'module': 'appium', 'name': 'uninstall', 'function': 'uninstall_application'},
    118: {'module': 'appium', 'name': 'teardown', 'function': 'teardown_appium'},
    119: {'module': 'appium', 'name': 'keypress', 'function': 'Keystroke_Appium'},
    120: {'module': 'appium', 'name': 'tap location', 'function': 'tap_location'},
    200: {'module': 'appium', 'name': 'reset', 'function': 'reset_application'},
    121: {'module': 'rest', 'name': 'save response', 'function': 'Get_Response'},
    128: {'module': 'selenium', 'name': 'click', 'function': 'Click_Element'},
    129: {'module': 'selenium', 'name': 'click and hold', 'function': 'Click_and_Hold_Element'},
    130: {'module': 'selenium', 'name': 'context click', 'function': 'Context_Click_Element'},
    131: {'module': 'selenium', 'name': 'double click', 'function': 'Double_Click_Element'},
    132: {'module': 'selenium', 'name': 'move to element', 'function': 'Move_To_Element'},
    133: {'module': 'selenium', 'name': 'hover', 'function': 'Hover_Over_Element'},
    134: {'module': 'selenium', 'name': 'keystroke keys', 'function': 'Keystroke_For_Element'},
    135: {'module': 'selenium', 'name': 'keystroke chars', 'function': 'Keystroke_For_Element'},
    136: {'module': 'selenium', 'name': 'text', 'function': 'Enter_Text_In_Text_Box'},
    139: {'module': 'selenium', 'name': 'initialize list', 'function': 'Initialize_List'},
    140: {'module': 'selenium', 'name': 'validate full text', 'function': 'Validate_Text'},
    141: {'module': 'selenium', 'name': 'validate partial text', 'function': 'Validate_Text'},
    146: {'module': 'selenium', 'name': 'scroll', 'function': 'Scroll'},
    148: {'module': 'selenium', 'name': 'deselect all', 'function': 'Select_Deselect'},
    149: {'module': 'selenium', 'name': 'select by visible text', 'function': 'Select_Deselect'},
    150: {'module': 'selenium', 'name': 'deselect by visible text', 'function': 'Select_Deselect'},
    151: {'module': 'selenium', 'name': 'select by value', 'function': 'Select_Deselect'},
    152: {'module': 'selenium', 'name': 'deselect by value', 'function': 'Select_Deselect'},
    153: {'module': 'selenium', 'name': 'select by index', 'function': 'Select_Deselect'},
    154: {'module': 'selenium', 'name': 'deselect by index', 'function': 'Select_Deselect'},
    155: {'module': 'utility', 'name': 'math', 'function': 'Calculate'},
    156: {'module': 'utility', 'name': 'upload', 'function': 'Upload'},
    157: {'module': 'utility', 'name': 'save string', 'function': 'Save_Text'},
    158: {'module': 'utility', 'name': 'copy', 'function': 'Copy_File_or_Folder'},
    159: {'module': 'utility', 'name': 'delete', 'function': 'Delete_File_or_Folder'},
    160: {'module': 'utility', 'name': 'create', 'function': 'Create_File_or_Folder'},
    161: {'module': 'utility', 'name': 'find', 'function': 'Find_File'},
    162: {'module': 'utility', 'name': 'rename', 'function': 'Rename_File_or_Folder'},
    163: {'module': 'utility', 'name': 'move', 'function': 'Move_File_or_Folder'},
    164: {'module': 'utility', 'name': 'zip', 'function': 'Zip_File_or_Folder'},
    165: {'module': 'utility', 'name': 'unzip', 'function': 'Unzip_File_or_Folder'},
    166: {'module': 'utility', 'name': 'compare', 'function': 'Compare_File'},
    167: {'module': 'utility', 'name': 'empty', 'function': 'Empty_Trash'},
    168: {'module': 'utility', 'name': 'user name', 'function': 'Get_User_Name'},
    169: {'module': 'utility', 'name': 'current documents', 'function': 'Get_Current_Documents'},
    170: {'module': 'utility', 'name': 'current desktop', 'function': 'Get_Current_Desktop'},
    171: {'module': 'utility', 'name': 'home directory', 'function': 'Get_Home_Directory'},
    172: {'module': 'utility', 'name': 'run sudo', 'function': 'Run_Command'},
    173: {'module': 'utility', 'name': 'run command', 'function': 'Run_Command'},
    174: {'module': 'utility', 'name': 'download', 'function': 'Download_file'},
    177: {'module': 'utility', 'name': 'log 2', 'function': 'Add_Log'},
    178: {'module': 'utility', 'name': 'log 3', 'function': 'Add_Log'},
    179: {'module': 'utility', 'name': 'log 1', 'function': 'Add_Log'},
    180: {'module': 'utility', 'name': 'download and unzip', 'function': 'Download_File_and_Unzip'},
    181: {'module': 'utility', 'name': 'take screen shot', 'function': 'TakeScreenShot' },
    182: {'module': 'selenium', 'name': 'open browser', 'function': 'Open_Browser_Wrapper'},
    183: {'module': 'selenium', 'name': 'go to link', 'function': 'Go_To_Link'},
    184: {'module': 'selenium', 'name': 'tear down browser', 'function': 'Tear_Down_Selenium'},
    185: {'module': 'selenium', 'name': 'navigate', 'function': 'Navigate'},
    186: {'module': 'xml', 'name': 'update', 'function': 'update_element'},
    187: {'module': 'xml', 'name': 'add', 'function': 'add_element'},
    188: {'module': 'xml', 'name': 'read', 'function': 'read_element'},
    189: {'module': 'xml', 'name': 'delete', 'function': 'delete_element'},
    190: {'module': 'appium', 'name': 'imei', 'function': 'device_information'},
    192: {'module': 'desktop', 'name': 'click', 'function': 'Click_Element'},
    193: {'module': 'desktop', 'name': 'double click', 'function': 'Double_Click_Element'},
    194: {'module': 'desktop', 'name': 'hover', 'function': 'Hover_Over_Element'},
    195: {'module': 'desktop', 'name': 'keystroke keys', 'function': 'Keystroke_For_Element'},
    196: {'module': 'desktop', 'name': 'keystroke chars', 'function': 'Keystroke_For_Element'},
    197: {'module': 'desktop', 'name': 'enter text', 'function': 'Enter_Text_In_Text_Box'},
    198: {'module': 'desktop', 'name': 'wait', 'function': 'Sleep'},
    199: {'module': 'selenium', 'name': 'get location', 'function': 'get_location_of_element'},
    201: {'module': 'appium', 'name': 'validate screen text', 'function': 'Validate_Text_Appium'},
    202: {'module': 'appium', 'name': 'model name', 'function': 'device_information'},
    203: {'module': 'appium', 'name': 'version', 'function': 'device_information'},
    204: {'module': 'selenium', 'name': 'validate table', 'function': 'validate_table'},
    205: {'module': 'appium', 'name': 'serial no', 'function': 'device_information'},
    206: {'module': 'appium', 'name': 'storage', 'function': 'device_information'}
}

# List of Sub-Field keywords, must be all lowercase, and using single spaces - no underscores
action_support = [
    'action',
    'optional action',
    'conditional action',
    'element parameter',
    'child parameter',
    'parent parameter',
    'target parameter',
    'method',
    'url',
    'body',
    'header',
    'headers',
    'compare',
    'path',
    'value',
    'result',
    'table parameter'
]

# Import modules
import inspect, sys, os
from Framework.Utilities import CommonUtil
import common_functions as common # Functions that are common to all modules
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list, skipped_tag_list # Allowed return strings, used to normalize pass/fail
from Framework.Built_In_Automation.Shared_Resources import LocateElement

# Recall dependency, if not already set
dependency = None
if sr.Test_Shared_Variables('dependency'): # Check if driver is already set in shared variables
    dependency = sr.Get_Shared_Variables('dependency') # Retreive appium driver


def load_sa_modules(module): # Load module "AS" must match module name we get from step data (See actions variable above)
    ''' Dynamically loads modules when needed '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    if module == 'common':
        pass # Already imported at top of this file
    elif module == 'appium':
        global appium
        from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions as appium
    elif module == 'selenium':
        global selenium
        from Framework.Built_In_Automation.Web.Selenium import BuiltInFunctions as selenium
    elif module == 'rest':
        global rest
        from Framework.Built_In_Automation.Web.REST import BuiltInFunctions as rest
    elif module == 'utility':
        global utility
        from Framework.Built_In_Automation.Built_In_Utility.CrossPlatform import BuiltInUtilityFunction as utility
    elif module == 'xml':
        global xml
        from Framework.Built_In_Automation.XML import BuiltInFunctions_XML as xml
    elif module == 'desktop':
        global desktop
        from Framework.Built_In_Automation.Desktop.CrossPlatform import BuiltInFunctions as desktop
    else:
        CommonUtil.ExecLog(sModuleInfo, "Invalid sequential actions module: %s" % module, 3)
        return 'failed'
    return 'passed'

def Sequential_Actions(step_data, _dependency = {}, _run_time_params = '', _file_attachment = {}, _temp_q = '',screen_capture='Desktop'):
    ''' Main Sequential Actions function - Performs logical decisions based on user input '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)
    
    # Set dependency, file_attachemnt as global variables
    global dependency, file_attachment
    if _dependency != {}:
        dependency = _dependency # Save to global variable
        sr.Set_Shared_Variables('dependency', _dependency) # Save in Shared Variables
    
    if _file_attachment != {}: # If a file attachment was passed
        file_attachment = _file_attachment # Save as a global variable
        sr.Set_Shared_Variables('file_attachment', _file_attachment) # Add entire file attachment dictionary to Shared Variables
        for file_attachment_name in _file_attachment: # Add each attachment as it's own Shared Variable, so the user can easily refer to it
            sr.Set_Shared_Variables(file_attachment_name, _file_attachment[file_attachment_name])
    
    # Set screen capture type (desktop/mobile) as shared variable, so TakeScreenShot() can read it
    sr.Set_Shared_Variables('screen_capture', screen_capture.lower().strip()) # Save the screen capture type
    CommonUtil.set_screenshot_vars(sr.Shared_Variable_Export()) # Get all the shared variables, and pass them to CommonUtil

    # Prepare step data for processing
    step_data = common.sanitize(step_data, column = 1) # Sanitize Sub-Field
    step_data = common.adjust_element_parameters(step_data) # Parse any mobile platform related fields
    if common.verify_step_data(step_data) in failed_tag_list: return 'failed' # Verify step data is in correct format
    
    try:
        result = 'failed' # Initialize result            
        for data_set in step_data: # For each data set within step data
            logic_row=[] # Holds conditional actions
            for row in data_set: # For each row of the data set
                action_name = row[1] # Get Sub-Field
                
                # Don't process these suport items right now, but also don't fail
                if action_name in action_support:
                    continue

                # If middle column = action, call action handler, but always return a pass
                elif "optional action" in action_name:
                    CommonUtil.ExecLog(sModuleInfo, "Checking the optional action to be performed in the action row: %s" % str(row), 0)
                    result = Action_Handler(data_set, row) # Pass data set, and action_name to action handler
                    if result == 'failed':
                        CommonUtil.ExecLog(sModuleInfo, "Optional action failed. Returning pass anyway", 2)
                    result = 'passed'
                    
                # If middle column = conditional action, evaluate data set
                elif "conditional action" in action_name:
                    CommonUtil.ExecLog(sModuleInfo, "Checking the logical conditional action to be performed in the conditional action row: %s" % str(row), 0)
                    logic_row.append(row)
                    
                    # Only run this when we have two conditional actions for this data set (a true and a false preferably)
                    if len(logic_row) == 2:
                        CommonUtil.ExecLog(sModuleInfo, "Found 2 conditional actions - moving ahead with them", 1)
                        return Conditional_Action_Handler(step_data, data_set, row, logic_row) # Pass step_data, and current iteration of data set to decide which data sets will be processed next
                        # At this point, we don't process any more data sets, which is why we return here. The conditional action function takes care of the rest of the execution
                
                # If middle column = action, call action handler
                elif "action" in action_name: # Must be last, since it's a single word that also exists in other action types
                    CommonUtil.ExecLog(sModuleInfo, "Checking the action to be performed in the action row: %s" % str(row), 0)
                    result = Action_Handler(data_set, row) # Pass data set, and action_name to action handler

                    # Check if user wants to store the result for later use
                    stored = False
                    for r in data_set:
                        if r[0].lower().strip() == 'store' and r[1].lower().strip() == 'result': # If Field = store and Sub-Field = result
                            CommonUtil.ExecLog(sModuleInfo, "Storing result for later use. Will not exit if action failed: %s" % result, 1)
                            sr.Set_Shared_Variables(r[2].strip(), result) # Use the Value as the shared variable name, and save the result
                            stored = True # In the case of a failed result, skip the return that comes after this
                            
                    # Check result of action handler 
                    if stored == False and result in failed_tag_list:
                        return "failed"
                
                # Middle column not listed above, so data set is wrong
                else:
                    CommonUtil.ExecLog(sModuleInfo, "The sub-field information is incorrect. Please provide accurate information on the data set(s).", 3)
                    return "failed"                 
        
        # No failures, return result
        return result

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

 

def Conditional_Action_Handler(step_data, data_set, row, logic_row):
    ''' Process conditional actions, called only by Sequential_Actions() '''
     
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    # Get module and dynamically load it
    module = row[1].split(' ')[0]
    load_sa_modules(module)

    # Convert any shared variables into their strings
    data_set = common.shared_variable_to_value(data_set)
    if data_set in failed_tag_list:
        return 'failed'
    
    # Test if data set contains the recall line, and if so, get the saved result from the previous action
    try:
        stored = False
        for row in data_set:
            if row[0].lower().strip() == 'recall' and row[1].lower().strip() == 'result': # If Field = recall and Sub-Field = result
                CommonUtil.ExecLog(sModuleInfo, "Recalled result: %s" % str(row[2]), 1)
                stored = True
                result = row[2] # Retrieve the saved result (already converted from shared variable)
    except:
        errMsg = "Error reading stored result. Perhaps it was not stored, or you failed to include the store result line in your previous action"
        return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)

    if stored == False: # Just to be clear, we can't to log that we are using the old method
        CommonUtil.ExecLog(sModuleInfo, "Could not find the recall result row. It's either missing or mispelled. Trying old method of Conditional Action, but suggest you update to the currently accepted method", 2)
        
    if stored == True: # Use saved result from previous data set
        if result in failed_tag_list: # Check result from previous action 
            logic_decision = "false"
        else: # Passed / Skipped
            logic_decision = "true"


    # *** Old method of conditional actions in the if statements below. Only kept for backwards compatibility *** #
    
    elif module == 'appium' or module == 'selenium':
        try:
            Element = LocateElement.Get_Element(data_set, eval(module).get_driver()) # Get the element object or 'failed'
            if Element in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Conditional Actions could not find the element", 3)
                logic_decision = "false"
            else:
                logic_decision = "true"
        except: # Element doesn't exist, proceed with the step data following the fail/false path
            CommonUtil.ExecLog(sModuleInfo, "Conditional Actions could not find the element", 3)
            logic_decision = "false"
                         
    elif module == 'rest':
        Get_Element_Step_Data = getattr(eval(module), 'Get_Element_Step_Data')
        element_step_data = Get_Element_Step_Data(
            [data_set])  # Pass data set as a list, and get back anything that's not an "action" or "conditional action"
        Validate_Step_Data = getattr(eval(module), 'Validate_Step_Data')
        returned_step_data_list = Validate_Step_Data(
            element_step_data[0])  # Make sure the element step data we got back from above is good
        if ((returned_step_data_list == []) or (
            returned_step_data_list == "failed")):  # Element step data is bad, so fail
            CommonUtil.ExecLog(sModuleInfo, "Element data is bad: %s" % str(element_step_data), 3)
            return "failed"
        else:  # Element step data is good, so continue
            # Check if element from data set exists on device
            try:
                Get_Response = getattr(eval(module), 'Get_Response')
                Element = Get_Response(element_step_data[0])
                if Element == 'failed':  # Element doesn't exist, proceed with the step data following the fail/false path
                    logic_decision = "false"
                else:  # Any other return means we found the element, proceed with the step data following the pass/true pass
                    logic_decision = "true"
            except Exception:  # Element doesn't exist, proceed with the step data following the fail/false path
                CommonUtil.ExecLog(sModuleInfo, "Could not find element in the by the criteria...", 3)
                logic_decision = "false"
                return CommonUtil.Exception_Handler(sys.exc_info())

    elif module == 'utility':
        Get_Path_Step_Data = getattr(eval(module), 'Get_Path_Step_Data')
        element_step_data = Get_Path_Step_Data(
            data_set)  # Pass data set as a list, and get back anything that's not an "action" or "conditional action"
        Validate_Path_Step_Data = getattr(eval(module), 'Validate_Path_Step_Data')
        returned_step_data_list = Validate_Path_Step_Data(
            [element_step_data[0]])  # Make sure the element step data we got back from above is good
        if ((returned_step_data_list == []) or (
            returned_step_data_list == "failed")):  # Element step data is bad, so fail
            CommonUtil.ExecLog(sModuleInfo, "Element data is bad: %s" % str(element_step_data), 3)
            return "failed"
        else:  # Element step data is good, so continue
            # Check if element from data set exists on device
            try:
                find = getattr(eval(module), 'find')
                Element = find(returned_step_data_list[0])
                if Element == False:
                    logic_decision = "false"
                else:
                    logic_decision = "true"
            except Exception:  # Element doesn't exist, proceed with the step data following the fail/false path
                CommonUtil.ExecLog(sModuleInfo, "Could not find element in the by the criteria...", 3)
                logic_decision = "false"
                return CommonUtil.Exception_Handler(sys.exc_info())

    # *** Old method of conditional actions in the if statements above. Only kept for backwards compatibility *** #
    
    else:
        CommonUtil.ExecLog(sModuleInfo, "Either no module was specified in the Conditional Action line, or it is incorrect", 3)
        return "failed"

    # Process the path as defined above (pass/fail)
    for conditional_steps in logic_row: # For each conditional action from the data set
        CommonUtil.ExecLog(sModuleInfo, "Processing conditional action: %s" % str(conditional_steps), 1)
        if logic_decision in conditional_steps: # If we have a result from the element check above (true/false)
            list_of_steps = conditional_steps[2].split(",") # Get the data set numbers for this conditional action and put them in a list
            for each_item in list_of_steps: # For each data set number we need to process before finishing
                CommonUtil.ExecLog(sModuleInfo, "Processing conditional step %s" % str(each_item), 1)
                data_set_index = int(each_item.strip()) - 1 # data set number, -1 to offset for data set numbering system
                
                if step_data[data_set_index] == data_set: # If the data set we are GOING to pass back to sequential_actions() is the same one that called THIS function in the first place, then the step data is calling itself again, and we must pass all of the step data instead, so it doesn't crash later when it tries to refer to data sets that don't exist
                    result = Sequential_Actions(step_data) # Pass the step data to sequential_actions() - Mainly used when the step data is in a deliberate recursive loop of conditional actions
                else: # Normal process - most conditional actions will come here
                    result = Sequential_Actions([step_data[data_set_index]]) # Recursively call this function until all called data sets are complete
            return result # Return only the last result of the last row of the last data set processed - This should generally be a "step result action" command

    # Shouldn't get here, but just in case
    return 'passed'

def Action_Handler(_data_set, action_row):
    ''' Finds the appropriate function for the requested action in the step data and executes it '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    # Split data set row into the usable parts
    action_name = action_row[0]
    action_subfield = action_row[1]

    # Get module and function for this action
    module = ''
    function = ''
    original_module = ''
    module, function, original_module = common.get_module_and_function(action_name, action_subfield) # New, get the module to execute
    CommonUtil.ExecLog(sModuleInfo, "Function identified as function: %s in module: %s" % (function, module), 0)

    if module in failed_tag_list or module == '' or function == '': # New, make sure we have a function
        CommonUtil.ExecLog(sModuleInfo, "You probably didn't add the module as part of the action. Eg: appium action", 3)
        return "failed"

    # If this is a common function, try to get the webdriver for it, if there is one, and save it to shared variables. This will allow common functions to work with whichever webdriver they need
    if original_module != '': # This was identified as a common module
        try:
            common_driver = eval(original_module).get_driver() # Get webdriver object
            sr.Set_Shared_Variables('common_driver', common_driver) # Save in shared variable
        except: pass # Not all modules have get_driver, so don't worry if this crashes
    
    # Strip the "optional" keyword, and module, so functions work properly (result of optional action is handled by sequential_actions)
    data_set = []
    for row in _data_set:
        new_row = list(row)
        if 'optional' in row[1]:
            new_row[1] = new_row[1].replace('optional', '').strip()
        if module in row[1]:
            new_row[1] = new_row[1].replace(module, '').strip()
        if original_module != '' and original_module in row[1]:
            new_row[1] = new_row[1].replace(original_module, '').strip()
        data_set.append(tuple(new_row))

    # Convert shared variables to their string equivelent
    data_set = common.shared_variable_to_value(data_set)
    if data_set in failed_tag_list:
        return 'failed'

    # Execute the action's function
    try:
        result = load_sa_modules(module) # Load the appropriate module
        if result == 'failed':
            CommonUtil.ExecLog(sModuleInfo, "Can't find module for %s" % module, 3)
            return 'failed'
            
        CommonUtil.ExecLog(sModuleInfo, "Executing %s with data set %s" % (function, str(data_set)), 1)
        run_function = getattr(eval(module), function) # create a reference to the function
        result = run_function(data_set) # Execute function, providing all rows in the data set
        return result # Return result to sequential_actions()

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
 

