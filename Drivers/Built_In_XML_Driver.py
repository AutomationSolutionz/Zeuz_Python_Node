'''
Created on Apr 20, 2017

@author: mchowdhury
Comment: Not published yet
'''

import sys, inspect
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.XML import BuiltInFunctions_XML

'''Constants'''
passed_tag_list = ['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True',True,1,'1','Success','success','SUCCESS']
failed_tag_list = ['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE',False,0,'0']

local_run = True

##
# Driver function to perform the sequential actions on step-data(s) of XML file
# @param step_data is a set of user data provided in the Test case 
# @return the function result 'pass' or 'fail'
def sequential_actions_xml(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo,"Function: sequential_actions_xml",1,local_run)
    try:
        sTestStepReturnStatus = BuiltInFunctions_XML.xml_sequential_actions(step_data)
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

sequential_actions_xml(step_data)