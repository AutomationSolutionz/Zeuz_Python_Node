# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

from Framework.Built_In_Automation.XML import BuiltInFunctions_XML as bf_xml
from Framework.Built_In_Automation.new_sequential_actions2 import sequential_actions_new as sa_new

# Test-1712: android_suite-qc.xml -> target + action: 
def test_case1 ():
#     step_data1 = [ [ ( 'level 1' , 'path' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/qa_latest/android_suite-qc.xml' , False , False , '' ) , ( 'TestSuite' , 'target parameter' , 'operatorAuditThreshold' , False , False , '' ) , ( 'update' , 'xml action' , '1' , False , False , '' ) ] ]
    step_data1 = [ [ ( '/home/asci/Desktop/Testing/XMLTools/Default_XML_Files/android_suite-qc.xml' , 'path' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/qa_latest/android_suite-qc.xml' , False , False) , ( 'tag' , 'element parameter' , 'TestSuite' , False , False ) , ( 'operatorAuditThreshold' , 'target parameter' , '0' , False , False ), ( 'update' , 'xml action' , '1' , False , False ) ] ]

#     result_test_case1 = bf_xml.xml_sequential_actions(step_data1)
    result_test_case1 = sa_new.Sequential_Actions(step_data1)
    if result_test_case1 ==  "Passed":
        print "Success: Action performed successfully...."
    else:
        print "Failed: Failed to perform action...."
 
# Test-2291: serviceSuiteDefinitionFile.xml -> parent + target + action                  
def test_case2 ():
    step_data2 = [ [ ( 'filepath' , 'path' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/serviceSuiteDefinitionFile.xml' , False , False ) , ( 'identifier' , 'parent parameter' , 'DiagnosticsQuickSuite' , False , False ) , ( 'class' , 'element parameter' , 'RunDiagnostics' , False , False ) , ( 'class' , 'target parameter' , 'RunDiagnostics' , False , False ) , ( 'update' , 'xml action' , 'RunDiagnostics-update' , False , False ) ] ]

    result_test_case2 = sa_new.Sequential_Actions(step_data2)
    if result_test_case2 ==  "Passed":
        print "Success: Action performed successfully...."
    else:
        print "Failed: Failed to perform action...."

# Test-2099: serviceDefinitionFile.xml -> parent + element + target + action
def test_case3 ():
    step_data3 = [ [ ( 'filepath' , 'path' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/serviceDefinitionFile.xml' , False , False ) , ( 'identifier' , 'parent parameter' , 'ApplicationInstall' , False , False ) , ( 'name' , 'element parameter' , 'appIOS' , False , False ) , ( 'value' , 'target parameter' , 'pro-diagnostics-17.7.3.ipa' , False , False ) , ( 'update' , 'xml action' , 'pro-diagnostics-17.7.4.ipa' , False , False ) ] ]

    result_test_case3 = sa_new.Sequential_Actions(step_data3)
    if result_test_case3 ==  "Passed":
        print "Success: Action performed successfully...."
    else:
        print "Failed: Failed to perform action...."

# Test-2336: android_testdefinitions.xml -> parent + element + target + action
def test_case4 ():
    step_data4 = [ [ ( 'filepath' , 'path' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/qa_latest/android_testdefinitions.xml' , False , False ) , ( 'customerIdentifier' , 'parent parameter' , 'MainMicrophoneRecordTest' , False , False ) , ( 'mode' , 'element parameter' , 'WhiteNoise' , False , False ) , ( 'enabled' , 'target parameter' , 'true' , False , False ) , ( 'update' , 'xml action' , 'false' , False , False ) ] ]
    result_test_case4 = sa_new.Sequential_Actions(step_data4)
    if result_test_case4 ==  "Passed":
        print "Success: Action performed successfully...."
    else:
        print "Failed: Failed to perform action...."

# failcodes.xml -> parent + target + action
def test_case5 ():
    step_data5 = [ [ ( 'filepath' , 'path' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/qa_latest/failcodes.xml' , False , False ) , ( 'name' , 'parent parameter' , 'General Test Failure' , False , False ) , ( 'name' , 'element parameter' , 'ICloudTest' , False , False ) , ( 'name' , 'target parameter' , 'ICloudTest' , False , False ) , ( 'update' , 'xml action' , 'ICloudTest-update' , False , False ) ] ]
    result_test_case5 = sa_new.Sequential_Actions(step_data5)
    if result_test_case5 ==  "Passed":
        print "Success: Action performed successfully...."
    else:
        print "Failed: Failed to perform action...."

# Test- ??: Teleplan.xml -> target + action
def test_case6 ():
    step_data6 = [ [ ( 'filepath' , 'path' , '/home/asci/AssetScience/Generic/Teleplan_464646464646_20170712094915.xml' , False , False ) , ( 'read' , 'xml action' , False , False ) ] ]

    result_test_case6 = sa_new.Sequential_Actions(step_data6)
    if result_test_case6 ==  "Passed":
        print "Success: Action performed successfully...."
    else:
        print "Failed: Failed to perform action...."


# Calling the function(s)
print test_case1 ()
# print test_case2 ()
# print test_case3 ()
# print test_case4 ()
# print test_case5 ()
# print test_case6 ()

