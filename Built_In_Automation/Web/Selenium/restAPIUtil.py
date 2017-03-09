import sys, os, re, inspect
import json
import requests
from datetime import datetime
from Utilities import CommonUtil
from Built_In_Automation.Web.Selenium import BuiltInFunctions

sys.path.append("..")



# Basic API Helper methods. Currently supporting GET and POST calls
## Need to add more functionality later
def rest_API_Helper(rest_call_type,url,headers=False,payload_type=False,body=False, extraction_fields=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: rest_API_Helper", 1)
    try:
        if ((rest_call_type == "") or (url == "")):
                CommonUtil.ExecLog(sModuleInfo, "Please enter a valid REST call type and a valid URL!", 3)
                return "failed"
        else:                     
            #For GET calls
            if rest_call_type=="GET":
                #Payload type: json
                if payload_type == "json":
                    response = requests.get(url, json=body, headers=headers)
                #Payload type: data
                elif payload_type == "data":
                    response = requests.get(url, data=body, headers=headers)
            
            #For POST calls
            elif rest_call_type=="POST":
                #Payload type: json
                if payload_type == "json":
                    response = requests.post(url, json=body, headers=headers)
                #Payload type: data
                elif payload_type == "data":
                    response = requests.post(url, data=body, headers=headers)            
            
            #For PUT calls
            elif rest_call_type=="PUT":
                #Payload type: json
                if payload_type == "json":
                    response = requests.put(url, json=body, headers=headers)
                #Payload type: data
                elif payload_type == "data":
                    response = requests.put(url, data=body, headers=headers)
            
            #For PATCH calls
            elif rest_call_type=="PATCH":
                #Payload type: json
                if payload_type == "json":
                    response = requests.patch(url, json=body, headers=headers)
                #Payload type: data
                elif payload_type == "data":
                    response = requests.patch(url, data=body, headers=headers)
            
            
            #If response is successful (i.e. code 200)
            if response.status_code == 200:
                CommonUtil.ExecLog(sModuleInfo, "Successful REST request. Status Code: %s"%response.status_code, 1)
                if payload_type == "json":
                    return response.json()
                else:
                    validation_result = _response_Validation(payload_type, response, extraction_fields) 
                    return validation_result
            else:
                CommonUtil.ExecLog(sModuleInfo, "Error in REST request. Status Code: %s"%response.status_code, 3)
                
    except Exception, e:
        errMsg = "rest_API_Helper not successful in returning data. Please check the data entered."
        Exception_Info(sModuleInfo, errMsg)


# Internal method
## Will be improved upon in the future 
def _response_Validation(payload_type, response, extraction_data=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: _response_Validation", 1)
    try:
#         extraction_fields = extraction_data.split(',')
        
        master_container = []
        #For payload body type: data
        if payload_type == "data":
            extraction_fields = extraction_data.split(',')
            for each in response.json():
                ##Will need to send required_data through step data
                container = []
                for each_data in extraction_fields:
                    for each_item in each:
                        if each_data in each_item:
                            item = each.get(each_data)
                            container.append(str(item))
                master_container.append(container)
            print master_container
            return master_container    
        
        #For payload body type: json
        elif payload_type == "json":
            CommonUtil.ExecLog(sModuleInfo, "Specific validation not provided. Will need to be implemented in the future.", 2)
            results=response.json()
            return results            
            #CommonUtil.ExecLog(sModuleInfo, "Validation not yet implemented. Failing validation step.", 2)  
            #return "failed"
            
    except Exception, e:
        errMsg = "Unable to validate response."
        Exception_Info(sModuleInfo, errMsg)

        
def Exception_Info(sModuleInfo, errMsg):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
    CommonUtil.ExecLog(sModuleInfo, errMsg + ".  Error: %s"%(Error_Detail), 3)
    return "failed"    
