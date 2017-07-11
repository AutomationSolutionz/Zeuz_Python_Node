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
actions = { # Numbers are arbitrary, and are not used anywhere
    100: {'module': 'appium', 'name': 'click', 'function': 'Click_Element_Appium'},
    101: {'module': 'appium', 'name': 'text', 'function': 'Enter_Text_Appium'},
    102: {'module': 'appium', 'name': 'wait', 'function': 'Wait_For_New_Element'},
    103: {'module': 'appium', 'name': 'tap', 'function': 'Tap_Appium'},
    104: {'module': 'appium', 'name': 'validate full text', 'function': 'Validate_Text_Appium'},
    105: {'module': 'appium', 'name': 'validate partial text', 'function': 'Validate_Text_Appium'},
    106: {'module': 'appium', 'name': 'save text', 'function': 'Save_Text'},
    107: {'module': 'appium', 'name': 'compare variable', 'function': 'Compare_Variables'},
    108: {'module': 'appium', 'name': 'initialize list', 'function': 'Initialize_List'},
    109: {'module': 'appium', 'name': 'compare list', 'function': 'Compare_Lists'},
    110: {'module': 'appium', 'name': 'insert into list', 'function': 'Insert_Into_List'},
    111: {'module': 'appium', 'name': 'install', 'function': 'install_application'},
    112: {'module': 'appium', 'name': 'launch', 'function': 'launch_application'},
    113: {'module': 'appium', 'name': 'get location', 'function': 'get_element_location_by_id'},
    114: {'module': 'appium', 'name': 'sleep', 'function': 'Sleep'},
    115: {'module': 'appium', 'name': 'swipe', 'function': 'swipe_handler'},
    116: {'module': 'appium', 'name': 'close', 'function': 'close_application'},
    117: {'module': 'appium', 'name': 'uninstall', 'function': 'uninstall_application'},
    118: {'module': 'appium', 'name': 'teardown', 'function': 'teardown_appium'},
    119: {'module': 'appium', 'name': 'keypress', 'function': 'Keystroke_Appium'},
    120: {'module': 'appium', 'name': 'tap location', 'function': 'tap_location'},
    200: {'module': 'appium', 'name': 'reset', 'function': 'reset_application'},
    121: {'module': 'rest', 'name': 'save response', 'function': 'Get_Response'},
    122: {'module': 'rest', 'name': 'compare variable', 'function': 'Compare_Variables'},
    123: {'module': 'rest', 'name': 'compare list', 'function': 'Compare_Lists'},
    124: {'module': 'rest', 'name': 'sleep', 'function': 'Sleep'},
    125: {'module': 'rest', 'name': 'initialize list', 'function': 'Initialize_List'},
    126: {'module': 'rest', 'name': 'step result', 'function': 'Step_Result'},
    127: {'module': 'rest', 'name': 'insert into list', 'function': 'Insert_Into_List'},
    128: {'module': 'selenium', 'name': 'click', 'function': 'Click_Element'},
    129: {'module': 'selenium', 'name': 'click and hold', 'function': 'Click_and_Hold_Element'},
    130: {'module': 'selenium', 'name': 'context click', 'function': 'Context_Click_Element'},
    131: {'module': 'selenium', 'name': 'double click', 'function': 'Double_Click_Element'},
    132: {'module': 'selenium', 'name': 'move to element', 'function': 'Move_To_Element'},
    133: {'module': 'selenium', 'name': 'hover', 'function': 'Hover_Over_Element'},
    134: {'module': 'selenium', 'name': 'keystroke keys', 'function': 'Keystroke_For_Element'},
    135: {'module': 'selenium', 'name': 'keystroke chars', 'function': 'Keystroke_For_Element'},
    136: {'module': 'selenium', 'name': 'text', 'function': 'Enter_Text_In_Text_Box'},
    137: {'module': 'selenium', 'name': 'wait', 'function': 'Wait_For_New_Element'},
    138: {'module': 'selenium', 'name': 'sleep', 'function': 'Sleep'},
    139: {'module': 'selenium', 'name': 'initialize list', 'function': 'Initialize_List'},
    140: {'module': 'selenium', 'name': 'validate full text', 'function': 'Validate_Text'},
    141: {'module': 'selenium', 'name': 'validate partial text', 'function': 'Validate_Text'},
    142: {'module': 'selenium', 'name': 'save text', 'function': 'Save_Text'},
    143: {'module': 'selenium', 'name': 'compare variable', 'function': 'Compare_Variables'},
    144: {'module': 'selenium', 'name': 'compare list', 'function': 'Compare_Lists'},
    145: {'module': 'selenium', 'name': 'insert into list', 'function': 'Insert_Into_List'},
    146: {'module': 'selenium', 'name': 'scroll', 'function': 'Scroll'},
    147: {'module': 'selenium', 'name': 'step result', 'function': 'Step_Result'},
    148: {'module': 'selenium', 'name': 'deselect all', 'function': 'Select_Deselect'},
    149: {'module': 'selenium', 'name': 'select by visible text', 'function': 'Select_Deselect'},
    150: {'module': 'selenium', 'name': 'deselect by visible text', 'function': 'Select_Deselect'},
    151: {'module': 'selenium', 'name': 'select by value', 'function': 'Select_Deselect'},
    152: {'module': 'selenium', 'name': 'deselect by value', 'function': 'Select_Deselect'},
    153: {'module': 'selenium', 'name': 'select by index', 'function': 'Select_Deselect'},
    154: {'module': 'selenium', 'name': 'deselect by index', 'function': 'Select_Deselect'},
    155: {'module': 'utility', 'name': 'math', 'function': 'Calculate'},
    156: {'module': 'utility', 'name': 'upload', 'function': 'Upload'},
    157: {'module': 'utility', 'name': 'save text', 'function': 'Save_Text'},
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
    172: {'module': 'utility', 'name': 'run sudo', 'function': 'Run_Sudo_Command'},
    173: {'module': 'utility', 'name': 'run command', 'function': 'Run_Command'},
    174: {'module': 'utility', 'name': 'download', 'function': 'Download_file'},
    175: {'module': 'utility', 'name': 'sleep', 'function': 'Sleep'},
    176: {'module': 'utility', 'name': 'step result', 'function': 'Step_Result'},
    177: {'module': 'utility', 'name': 'log 2', 'function': 'Add_Log'},
    178: {'module': 'utility', 'name': 'log 3', 'function': 'Add_Log'},
    179: {'module': 'utility', 'name': 'log 1', 'function': 'Add_Log'},
    180: {'module': 'utility', 'name': 'download and unzip', 'function': 'Download_File_and_Unzip'},
    181: {'module': 'utility', 'name': 'take screen shot', 'function': 'TakeScreenShot' },
    182: {'module': 'selenium', 'name': 'open browser', 'function': 'Open_Browser_Wrapper'},
    183: {'module': 'selenium', 'name': 'go to link', 'function': 'Go_To_Link'},
    184: {'module': 'selenium', 'name': 'tear down browser', 'function': 'Tear_Down_Selenium'},
    185: {'module': 'selenium', 'name': 'navigate', 'function': 'Navigate'}
}

# List of Sub-Field keywords, must be all lowercase, and using single spaces - no underscores
action_support = [
    'action',
    'optional action',
    'conditional action',
    'element parameter',
    'child parameter',
    'parent parameter',
    'method',
    'url',
    'body',
    'header',
    'headers',
    'compare',
    'path',
    'value'
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
    
    if module == 'appium':
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
    appium_driver = None
    screen_capture = screen_capture.lower().strip()
    sr.Set_Shared_Variables('screen_capture', screen_capture) # Save the screen capture type
    if screen_capture == 'desktop':
        CommonUtil.set_screen_capture_type(sr.Get_Shared_Variables('screen_capture'))
    elif screen_capture == 'web':
        if sr.Test_Shared_Variables('selenium_driver'):
            selenium_driver = sr.Get_Shared_Variables('selenium_driver')  # If the appium driver was set, get the driver object
            CommonUtil.set_screen_capture_type(sr.Get_Shared_Variables('screen_capture'), selenium_driver)
    elif screen_capture == 'mobile':
        if sr.Test_Shared_Variables('appium_driver'):
            appium_driver = sr.Get_Shared_Variables('appium_driver') # If the appium driver was set, get the driver object
            CommonUtil.set_screen_capture_type(sr.Get_Shared_Variables('screen_capture'), appium_driver) # Update the screen capture with the type and driver object if available

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
                        return Conditional_Action_Handler(step_data, data_set, row, logic_row, result) # Pass step_data, and current iteration of data set to decide which data sets will be processed next
                        # At this point, we don't process any more data sets, which is why we return here. The conditional action function takes care of the rest of the execution
                
                # If middle column = action, call action handler
                elif "action" in action_name: # Must be last, since it's a single word that also exists in other action types
                    CommonUtil.ExecLog(sModuleInfo, "Checking the action to be performed in the action row: %s" % str(row), 0)
                    result = Action_Handler(data_set, row) # Pass data set, and action_name to action handler
                    if result in failed_tag_list: # Check result of action handler
                        return "failed"
                
                # Middle column not listed above, so data set is wrong
                else:
                    CommonUtil.ExecLog(sModuleInfo, "The sub-field information is incorrect. Please provide accurate information on the data set(s).", 3)
                    return "failed"                 
        
        # No failures, return result
        return result

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

 

def Conditional_Action_Handler(step_data, data_set, row, logic_row, result):
    ''' Process conditional actions, called only by Sequential_Actions() '''
     
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function Start", 0)

    # Get module and dynamically load it
    module = row[1].split(' ')[0]
    load_sa_modules(module)

    data_set = shared_variable_to_value(data_set)
    if data_set in failed_tag_list:
        return 'failed'
    
    if module == 'appium' or module == 'selenium':
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
    action_value = action_row[2]

    # Get module and function for this action
    module = ''
    function = ''
    if action_name != 'step result': # Step result is handle here becaue it's common to all functions - we use this line because we don't want to process it as a module
        module, function = get_module_and_function(action_name, action_subfield) # New, get the module to execute
        CommonUtil.ExecLog(sModuleInfo, "Function identified as function: %s in module: %s" % (function, module), 0)
    
        if module in failed_tag_list or module == '' or function == '': # New, make sure we have a function
            CommonUtil.ExecLog(sModuleInfo, "You probably didn't add the module as part of the action. Eg: appium action", 3)
            return "failed"

    # Strip the "optional" keyword, and module, so functions work properly (result of optional action is handled by sequential_actions)
    data_set = []
    for row in _data_set:
        new_row = list(row)
        if 'optional' in row[1]:
            new_row[1] = new_row[1].replace('optional', '').strip()
        if module in row[1]:
            new_row[1] = new_row[1].replace(module, '').strip()
        data_set.append(tuple(new_row))

    # Convert shared variables to their string equivelent
    data_set = shared_variable_to_value(data_set)
    if data_set in failed_tag_list:
        return 'failed'

    try:
        if action_name == "step result": # Result from step data the user wants to specify (passed/failed)
            if action_value in failed_tag_list: # Convert user specified pass/fail into standard result
                return 'failed'
            elif action_value in skipped_tag_list:
                return 'skipped'
            elif action_value in passed_tag_list:
                return 'passed'
            else:
                CommonUtil.ExecLog(sModuleInfo, "Step Result action has invalid VALUE", 3)
                return 'failed'
        else:
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
 

def get_module_and_function(action_name, action_sub_field):
    ''' Function to split module from the action name, and with the action name tries to find the corrosponding function name '''
    
    try:
        action_list = action_sub_field.split(' ') # Split sub-field, so we can get moudle name from step data
        if action_list > 1: # Should be at least two words in the sub-field
            module = action_list[0] # Save first word which is the module name
            _exit = 0
            function = ''
            for i in actions: # For each dictionary in the dictionary
                if _exit == 1: break # Exit if we found what we are looking for
                for j in actions[i]: # For each entry in the sub-dictionary
                    if actions[i]['module'] == module and actions[i]['name'] == action_name: # Module and action name match
                        function = actions[i]['function'] # Save function
                        _exit = 1 # Exit for loop
                        break

            return module, function # Return module and function name
        else:
            return '','' # Error handled in calling function
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def shared_variable_to_value(data_set):
    ''' Look for any Shared Variable strings in step data, convert them into their values, and return '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    new_data = [] # Rebuild the data_set with the new variable (because it's a list of tuples which we can't update)

    try:
        for row in data_set: # For each row of the data set
            data_row = list(row) # Convert row which is a tuple to a list, so we can update it if we need to
            for i in range(0, 3): # For each field (Field, Sub-Field, Value)
                if row[i] != False: # !!!! Probbly not needed
                    while "%|" in data_row[i] and "|%" in data_row[i]: # If string contains these characters, it's a shared variable
                        CommonUtil.ExecLog(sModuleInfo, "Shared Variable: %s" % row[i], 0)
                        data_row[i] = sr.get_previous_response_variables_in_strings(data_row[i])# replace just the variable name with it's value (has to be in string format)
                        if data_row[i] == 'failed': #!!!this won't work if there's extra strings around the shared variable 
                            CommonUtil.ExecLog(sModuleInfo, "Invalid shared variable", 3)
                            return "failed"
            new_data.append(tuple(data_row)) # Convert row from list to tuple, and append to new data_set
        return new_data # Return parsed data_set
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

