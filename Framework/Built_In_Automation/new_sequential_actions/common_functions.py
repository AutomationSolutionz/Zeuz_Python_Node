import inspect, sys, time
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources

passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True','1','Success','success','SUCCESS',True]
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE','0',False]

def sanitize(step_data):
    ''' Sanitize step data Field and Sub-Field ''' 
    for each in step_data: # For each data set within step data
        for row in each: # For each row of the data set
            for i in range(0, 2): # For first 2 fields (Field, Sub-Field)
                row[i] = row[i].replace('  ', ' ')
                row[i] = row[i].replace('_', ' ')
    return step_data


def Get_Element_Step_Data_Appium(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function - Get Element Step Data", 1)
    
    try:
        element_step_data=[]
        for each in step_data[0]:
            if "action" in each[1]:
                CommonUtil.ExecLog(sModuleInfo, "Not a part of element step data", 2)
                continue
            else:
                element_step_data.append(each)
                 
        return element_step_data
    
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Validate_Step_Data(step_data):
    ''' Ensures step data is accurate, and returns only the pertinent values '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Validate_Step_Data", 1)
    try:    
        if (len(step_data)==1): # One row in the data set
            element_parameter = step_data[0][0] # Get Field (element object)
            element_value = step_data[0][2] # Get element value
            reference_parameter = False
            reference_value = False    
            reference_is_parent_or_child = False
#         elif (len(step_data)==2): #??? Whys is this commented out ???
#             for each in step_data:
#                 if each[1]=="element parameter 1 of 2":
#                     element_parameter = each[0]
#                     element_value = each[2]
#                 elif each[1]=="element parameter 2 of 2":
#                     reference_parameter = each[0]
#                     reference_value = each[2]
#             reference_is_parent_or_child = False
        elif (len(step_data)==3): # Three rows in the data set
            for each in step_data: # For each row
                if each[1]=="element parameter": # If Sub-Field is element parameter
                    element_parameter = each[0] # Get Field (element object)
                    element_value = each[2] # Get element value
                elif each[1]=="reference parameter": # If Sub-FIeld is reference parameter
                    reference_parameter = each[0] # Get Field (element object)
                    reference_value = each[2] # Get element value
                elif each[1]=="relation type": # If Sub-Field is relation type
                    reference_is_parent_or_child = each[2] # Get reference value
        else: # Invalid step data
            CommonUtil.ExecLog(sModuleInfo, "Data set incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        validated_data = (element_parameter, element_value, reference_parameter, reference_value, reference_is_parent_or_child)
        return validated_data # Return data as tuple
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Get_Element_Appium(element_parameter,element_value,reference_parameter=False,reference_value=False,reference_is_parent_or_child=False,get_all_unvalidated_elements=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        All_Elements_Found = []
        if reference_is_parent_or_child == False:
            if ((reference_parameter == False) and (reference_value == False)):
                All_Elements = Get_All_Elements_Appium(element_parameter,element_value)     
                if ((All_Elements == []) or (All_Elements == 'failed')):        
                    CommonUtil.ExecLog(sModuleInfo, "Could not find your element by parameter:%s and value:%s..."%(element_parameter,element_value), 3)
                    return "failed"
                else:
                    All_Elements_Found = All_Elements
            #elif (reference_parameter != False and reference_value!= False):
            #    CommonUtil.ExecLog(sModuleInfo, "Locating element using double matching", 1)
            #    All_Elements = Get_Double_Matching_Elements(element_parameter, element_value, reference_parameter, reference_value)
            #    if ((All_Elements == []) or (All_Elements == "failed")):
            #        CommonUtil.ExecLog(sModuleInfo, "Could not find your element by parameter1:%s , value1:%s and parameter2:%s , value2:%s..."%(element_parameter,element_value,reference_parameter,reference_value), 3)
            #        return "failed"
            #    else:
            #        All_Elements_Found = All_Elements
            else:
                CommonUtil.ExecLog(sModuleInfo, "Could not find your element because you are missing at least one parameter", 3)
                return "failed"
            
        elif reference_is_parent_or_child == "parent":     
            CommonUtil.ExecLog(sModuleInfo, "Locating all parents elements", 1)   
            all_parent_elements = Get_All_Elements_Appium(reference_parameter,reference_value)#,"parent")
            all_matching_elements = []
            for each_parent in all_parent_elements:
                interested_elem = Get_All_Elements_Appium(element_parameter,element_value,each_parent) #can there be a problem when we send in each parent, or does this contain both param and value?
                if interested_elem != "failed":
                    for each_matching in interested_elem:
                        all_matching_elements.append(each_matching)
            All_Elements_Found = all_matching_elements

        elif reference_is_parent_or_child == "child":        
            all_parent_elements = Get_All_Elements_Appium(element_parameter,element_value)
            all_matching_elements = []
            for each_parent in all_parent_elements:
                interested_elem = Get_All_Elements_Appium(reference_parameter,reference_value,each_parent)
                if interested_elem != "failed":
                    all_matching_elements.append(each_parent)
            All_Elements_Found=all_matching_elements
            
        elif ((reference_is_parent_or_child!="parent") or (reference_is_parent_or_child!="child") or (reference_is_parent_or_child!=False)):
            CommonUtil.ExecLog(sModuleInfo, "Unspecified reference type; please indicate whether parent, child or leave blank", 3)
            return "failed"
        
        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to run based on the current inputs, please check the inputs and re-enter values", 3)
            return "failed"
        
        #this method returns all the elements found without validation
        if(get_all_unvalidated_elements!=False):
            return All_Elements_Found
        else:
            #can later also pass on the index of the element we want
            result = Element_Validation(All_Elements_Found)#, index)
            return result
    
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())      

def Sleep(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Sleep", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,
                                   "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                                   3)
            return "failed"
        else:
            tuple = step_data[0][0]
            seconds = int(tuple[2])
            CommonUtil.ExecLog(sModuleInfo, "Sleeping for %s seconds" % seconds, 1)
            time.sleep(seconds)
            return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Wait_For_New_Element(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Wait_For_New_Page_Element", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):# or (len(step_data[1]) != 1)):
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:
            #element_step_data = step_data[0][0:len(step_data[0])-1:1]
            element_step_data = Get_Element_Step_Data(step_data)
            returned_step_data_list = Validate_Step_Data(element_step_data)
            if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                return "failed"
            else:
                try:
                    for each in step_data[0]:
                        if each[1]=="action":
                            timeout_duration = int(each[2])

                    start_time = time.time()
                    interval = 1
                    for i in range(timeout_duration):
                        time.sleep(start_time + i*interval - time.time())
                        Element = Get_Element(returned_step_data_list[0], returned_step_data_list[1], returned_step_data_list[2], returned_step_data_list[3], returned_step_data_list[4])
                        if (Element == []):
                            continue
                        else:
                            break

                    if ((Element == []) or (Element == "failed")):
                        return "failed"
                    else:
                        #return Element
                        return "passed"
                except Exception:
                    element_attributes = Element.get_attribute('outerHTML')
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s"%(element_attributes),3)
                    errMsg = "Could not find the new page element requested."
                    return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Get_Element(element_parameter,element_value,reference_parameter=False,reference_value=False,reference_is_parent_or_child=False,get_all_unvalidated_elements=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        All_Elements_Found = []
        if reference_is_parent_or_child == False:
            if ((reference_parameter == False) and (reference_value == False)):
                All_Elements = Get_All_Elements(element_parameter,element_value)
                if ((All_Elements == []) or (All_Elements == 'failed')):
                    CommonUtil.ExecLog(sModuleInfo, "Could not find your element by parameter:%s and value:%s..."%(element_parameter,element_value), 3)
                    return "failed"
                else:
                    All_Elements_Found = All_Elements
            elif (reference_parameter != False and reference_value!= False):
                CommonUtil.ExecLog(sModuleInfo, "Locating element using double matching", 1)
                All_Elements = Get_Double_Matching_Elements(element_parameter, element_value, reference_parameter, reference_value)
                if ((All_Elements == []) or (All_Elements == "failed")):
                    CommonUtil.ExecLog(sModuleInfo, "Could not find your element by parameter1:%s , value1:%s and parameter2:%s , value2:%s..."%(element_parameter,element_value,reference_parameter,reference_value), 3)
                    return "failed"
                else:
                    All_Elements_Found = All_Elements
            else:
                CommonUtil.ExecLog(sModuleInfo, "Could not find your element because you are missing at least one parameter", 3)
                return "failed"

        elif reference_is_parent_or_child == "parent":
            CommonUtil.ExecLog(sModuleInfo, "Locating all parents elements", 1)
            all_parent_elements = Get_All_Elements(reference_parameter,reference_value)#,"parent")
            all_matching_elements = []
            for each_parent in all_parent_elements:
                interested_elem = Get_All_Elements(element_parameter,element_value,each_parent) #can there be a problem when we send in each parent, or does this contain both param and value?
                if interested_elem != "failed":
                    for each_matching in interested_elem:
                        all_matching_elements.append(each_matching)
            All_Elements_Found = all_matching_elements

        elif reference_is_parent_or_child == "child":
            all_parent_elements = Get_All_Elements(element_parameter,element_value)
            all_matching_elements = []
            for each_parent in all_parent_elements:
                interested_elem = Get_All_Elements(reference_parameter,reference_value,each_parent)
                if interested_elem != "failed":
                    all_matching_elements.append(each_parent)
            All_Elements_Found=all_matching_elements

        elif reference_is_parent_or_child == "sibling":
            CommonUtil.ExecLog(sModuleInfo, "Locating the sibling element", 1)
#             all_sibling_elements = Get_All_Elements(reference_parameter,reference_value)
#             for each_sibling in all_sibling_elements:
#                 all_parent_elements = WebDriverWait(each_sibling, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, "..")))
#                 all_matching_elements = []
#                 for each_parent in all_parent_elements:
#                     interested_elem = Get_All_Elements(element_parameter,element_value,each_parent) #can there be a problem when we send in each parent, or does this contain both param and value?
#                     if interested_elem != "failed":
#                         for each_matching in interested_elem:
#                             all_matching_elements.append(each_matching)
#                 All_Elements_Found = all_matching_elements
###trying out list comprehension
            All_Elements_Found=[each_matching for each_sibling in Get_All_Elements(reference_parameter,reference_value) for each_parent in WebDriverWait(each_sibling, WebDriver_Wait).until(EC.presence_of_all_elements_located((By.XPATH, ".."))) for each_matching in Get_All_Elements(element_parameter,element_value,each_parent)]

        elif ((reference_is_parent_or_child!="parent") or (reference_is_parent_or_child!="child") or (reference_is_parent_or_child!=False)):
            CommonUtil.ExecLog(sModuleInfo, "Unspecified reference type; please indicate whether parent, child or leave blank", 3)
            return "failed"

        else:
            CommonUtil.ExecLog(sModuleInfo, "Unable to run based on the current inputs, please check the inputs and re-enter values", 3)
            return "failed"

        #this method returns all the elements found without validation
        if(get_all_unvalidated_elements!=False):
            return All_Elements_Found
        else:
            #can later also pass on the index of the element we want
            result = Element_Validation(All_Elements_Found)#, index)
            return result

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(),None,"Could not find your element.")
