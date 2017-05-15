# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

from Framework.Built_In_Automation.XML import BuiltInFunctions_XML as bf_xml


# Test-1712: android_suite-qc.xml -> target + action: 
def test_case1 ():
    step_data1 = [ [ ( 'level 1' , 'filepath' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/qa_latest/android_suite-qc.xml' , False , False , '' ) , ( 'TestSuite' , 'target parameter' , 'operatorAuditThreshold' , False , False , '' ) , ( 'update' , 'action' , '1' , False , False , '' ) ] ]

    result_test_case1 = bf_xml.xml_sequential_actions(step_data1)
    if result_test_case1 ==  "Passed":
        print "Success: Action performed successfully...."
    else:
        print "Failed: Failed to perform action...."
 
# Test-2291: serviceSuiteDefinitionFile.xml -> reference + target + action                  
def test_case2 ():
    step_data2 = [ [ ( 'level 2' , 'filepath' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/serviceSuiteDefinitionFile.xml' , False , False , '' ) , ( 'identifier' , 'reference parameter' , 'DiagnosticsQuickSuite' , False , False , '' ) , ( 'class' , 'target parameter' , 'RunDiagnostics' , False , False , '' ) , ( 'update' , 'action' , 'RunDiagnostics-update' , False , False , '' ) ] ]

    result_test_case2 = bf_xml.xml_sequential_actions(step_data2)
    if result_test_case2 ==  "Passed":
        print "Success: Action performed successfully...."
    else:
        print "Failed: Failed to perform action...."

# Test-2099: serviceDefinitionFile.xml -> reference + element + target + action
def test_case3 ():
    step_data3 = [ [ ( 'level 2' , 'filepath' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/serviceDefinitionFile.xml' , False , False , '' ) , ( 'identifier' , 'reference parameter' , 'ApplicationInstall' , False , False , '' ) , ( 'name' , 'element parameter' , 'appIOS' , False , False , '' ) , ( 'Argument' , 'target parameter' , 'value' , False , False , '' ) , ( 'update' , 'action' , 'pro-diagnostics-17.3.4.ipa' , False , False , '' ) ] ]

    result_test_case3 = bf_xml.xml_sequential_actions(step_data3)
    if result_test_case3 ==  "Passed":
        print "Success: Action performed successfully...."
    else:
        print "Failed: Failed to perform action...."

# Test-2336: android_testdefinitions.xml -> reference + element + target + action
def test_case4 ():
    step_data4 = [ [ ( 'level 3' , 'filepath' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/qa_latest/android_testdefinitions.xml' , False , False , '' ) , ( 'customerIdentifier' , 'reference parameter' , 'HeadsetStereoTest' , False , False , '' ) , ( 'mode' , 'element parameter' , 'MuteBothChannel' , False , False , '' ) , ( 'AuditMode' , 'target parameter' , 'enabled' , False , False , '' ) , ( 'update' , 'action' , 'false' , False , False , '' ) ] ]
    result_test_case4 = bf_xml.xml_sequential_actions(step_data4)
    if result_test_case4 ==  "Passed":
        print "Success: Action performed successfully...."
    else:
        print "Failed: Failed to perform action...."

# failcodes.xml -> reference + target + action
def test_case5 ():
    step_data5 = [ [ ( 'level 3' , 'filepath' , '/home/asci/AssetScience/recell_dse-candidate/Launcher/resource/configurations/qa_latest/failcodes.xml' , False , False , '' ) , ( 'name' , 'reference parameter' , 'General Test Failure' , False , False , '' ) , ( 'name' , 'target parameter' , 'ICloudTest' , False , False , '' ) , ( 'update' , 'action' , 'ICloudTest-update' , False , False , '' ) ] ]
    result_test_case5 = bf_xml.xml_sequential_actions(step_data5)
    if result_test_case5 ==  "Passed":
        print "Success: Action performed successfully...."
    else:
        print "Failed: Failed to perform action...."

# Test- ??: Teleplan.xml -> target + action
def test_case6 ():
    step_data6 = [ [ ( 'level 3' , 'filepath' , '/home/asci/AssetScience/Generic/Teleplan_21212121212122_20170228083953.xml' , False , False , '' ) , ( 'read' , 'action' , False , False , False , '' ) ] ]

    result_test_case6 = bf_xml.xml_sequential_actions(step_data6)
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

