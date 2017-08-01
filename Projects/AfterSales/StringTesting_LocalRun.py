'''
Created on May 1, 2017
Updated on June 31, 2017

@author: mchowdhury
'''

import time
from Framework.Built_In_Automation.Sequential_Actions import sequential_actions as sa

dependency = {'Mobile':'Android', 'Browser':'Chrome'}

def shutdown():
    d = [ [ ( 'teardown' , 'appium action' , 'assetscience') ] ]
    sa.Sequential_Actions(d, dependency)
    print "SHUTDOWN"
    quit()

# Test-2360: After Sales Run Through - Pass All 
def AfterSaleRunThroughPassAll ():
    
#Step-1: Launch and start the AFter Sales ProD (ProD pre-installed)
#     launchAppData = [ [ ( 'app_activity' , 'element parameter' , 'com.assetscience.recell.device.android.prodiagnostics.gui.aftersalesRMA.AftersalesRMAPairingActivity' , False , False , '' ) , ( 'launch' , 'appium action' , 'com.assetscience.tauschrausch', False , False , '' )  ] ]
    launchAppData = [ [ ( 'package' , 'element parameter' , 'assetscience' , False , False , '' ) , ( 'launch' , 'appium action' , 'launch', False , False , '' )  ] ]
## Amazon Kindle
#     launchAppData = [ [ ( 'package' , 'element parameter' , 'com.amazon.kindle' , False , False , '' ) , ( 'launch' , 'appium action' , 'launch', False , False , '' )  ] ]
    if sa.Sequential_Actions(launchAppData, dependency) == 'failed': shutdown()

#Step-2(s): Compare string(s) of Disclaimer screen
#Step-2.1: Comparer partial string
#     validateDisclaimerScreenData = [ [ ( 'text' , 'element parameter' , 'Submitting Results' , False , False , '' ),( 'validate partial text' , 'appium action' , 'Submitting' , False , False , '' )] ]
## Amazon Kindle
#     validateDisclaimerScreenData = [ [ ( 'text' , 'element parameter' , 'Get Kindle for Android' , False , False , '' ),( 'validate partial text' , 'appium action' , 'Kindle' , False , False , '' )] ]

#Step-2.2: Compare full string
#     validateDisclaimerScreenData = [ [ ( 'text' , 'element parameter' , 'Submitting Results' , False , False , '' ),( 'validate full text' , 'appium action' , 'Submitting Results', False , False , '' )] ]
## Amazon Kindle
#     validateDisclaimerScreenData = [ [ ( 'text' , 'element parameter' , 'Get Kindle for Android' , False , False , '' ),( 'validate full text' , 'appium action' , 'Get Kindle for Android', False , False , '' )] ]

#Step-2.3: Comparer full screen (all strings)
    expectedDisclaimerScreenText = 'Submitting Results||By using this application, you agree to send testing results to TauschRausch.||Refuse||Accept'
## Amazon Kindle
#     expectedDisclaimerScreenText = "Read novels, children's books, comics, magazines and more on your Android device.||Kindle has something for everyone.||Get Kindle for Android||*Content availability varies by country"
#     validateDisclaimerScreenData = [ [ ( 'id' , 'element parameter' , 'parentPanel' , False , False , '' ),( 'validate screen text' , 'appium action' , expectedDisclaimerScreenText, False , False , '' )] ]
    validateDisclaimerScreenData = [ [ ( 'text' , 'element parameter' , '' , False , False , '' ),( 'validate screen text' , 'appium action' , expectedDisclaimerScreenText, False , False , '' )] ]
    if sa.Sequential_Actions(validateDisclaimerScreenData) == 'failed': shutdown()
    
#Step-3: Accept Disclaimer screen
    acceptDialogueData = [ [ ( '*resource-id' , 'element parameter' , 'button1' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) ] ]
    if sa.Sequential_Actions(acceptDialogueData) == 'failed': shutdown()
        
#Step-4(s): Comparer (all) string(s) of Pairingcode screen
    expectedPairingScreenText = 'Enter the pairing code and press Start to begin||Enter pairing code||Start'
    validatePairingScreenData = [ [ ( 'text' , 'element parameter' , '' , False , False , '' ),( 'validate screen text' , 'appium action' , expectedPairingScreenText , False , False , '' )] ]
#     validatePairingScreenData = [ [ ( '*resource-id' , 'element parameter' , 'instructionsTextView' , False , False , '' ),( 'validate screen text' , 'appium action' , 'Enter the pairing code and press Start to begin' , False , False , '' )] ]
    if sa.Sequential_Actions(validatePairingScreenData) == 'failed': shutdown()
        
# #step-4.1: Login to PDM
#     loginPDMData = [ [ ( 'method' , 'element parameter' , 'post' , False , False , '' ) , ( 'password' , 'body' , 'Password1!' , False , False , '' ) , ( 'url' , 'element parameter' , 'https://pdm-qa.asci.io/api/login' , False , False , '' ) , ( 'save response' , 'rest action' , 'all' , False , False , '' ) , ( 'username' , 'body' , 'automationpdm' , False , False , '' ) ] ]
#     bfr.Sequential_Actions(loginPDMData)
    
# #Step-4.2: Save the Pairing code from PDM
#     setPairingCodeData = [ [ ( 'Authorization' , 'headers' , 'Bearer %|access_token|%' , False , False , '' ) , ( 'Content-Type' , 'headers' , 'application/json' , False , False , '' ) , ( 'save response' , 'rest action' , 'id, pairingCode, iosDownloadUrl' , False , False , '' ) , ( 'pairingCode' , 'body' , '%|random_string()|%' , False , False , '' ) , ( 'method' , 'element parameter' , 'post' , False , False , '' ) , ( 'url' , 'element parameter' , 'https://pdm-qa.asci.io/api/sessions' , False , False , '' ) ] ]
#     bfr.Sequential_Actions(setPairingCodeData)

#Step-4.3: Create and Validate Pairing Code
    loginSetPDMData = [ [ ( 'method' , 'element parameter' , 'post' , False , False ) , ( 'password' , 'body' , 'Password1!' , False , False ) , ( 'url' , 'element parameter' , 'https://pdm-qa.asci.io/api/login' , False , False ) , ( 'save response' , 'rest action' , 'all' , False , False ) , ( 'username' , 'body' , 'automationpdm' , False , False ) ]  , [ ( 'Authorization' , 'headers' , 'Bearer %|access_token|%' , False , False ) , ( 'Content-Type' , 'headers' , 'application/json' , False , False ) , ( 'save response' , 'rest action' , 'id, pairingCode, iosDownloadUrl' , False , False ) , ( 'pairingCode' , 'body' , '%|random_string("nlu")|%' , False , False ) , ( 'method' , 'element parameter' , 'post' , False , False ) , ( 'url' , 'element parameter' , 'https://pdm-qa.asci.io/api/sessions' , False , False ) ] ]
#     if bfr.Sequential_Actions(loginSetPDMData) == 'failed': shutdown()

#Step-5: Enter the pairing code into After Sales ProD
    enterPairingCodeData = [ [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/pairingCodeEditText' , False , False , '' ) , ( 'text' , 'appium action' , '%|pairingCode|%' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/startButton' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) ] ]
#     if bfr.Sequential_Actions(enterPairingCodeData) == 'failed': shutdown()
    time.sleep(3)
    
#Step-6(s): Compare (all) string(s) of Home screen
    expectedHomeScreenText = 'TauschRausch||This application will run diagnostics on the device. Some tests will run automatically. After the auto-tests, follow the instructions in the page and pass or fail the test accordingly.||Before you start, please:||Enable WiFi||Enable Bluetooth||Start Testing'
    validateHomeScreendata = [ [ ( 'text' , 'element parameter' , '' , False , False , '' ),( 'validate screen text' , 'appium action' , expectedHomeScreenText , False , False , '' )] ]
    if sa.Sequential_Actions(validateHomeScreendata) == 'failed': shutdown()

#Step-6.1: Start Auto Test (click on START Button)
    startAutoTestData = [ [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/startButton' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.android.packageinstaller:id/permission_allow_button' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.android.packageinstaller:id/permission_allow_button' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.android.packageinstaller:id/permission_allow_button' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) ] ]
    sa.Sequential_Actions(startAutoTestData)
    time.sleep(3)
    
#Step-7(s): Compare (all) string(s) of Auto Run Test screen
    expectedAutoTestScreenText = 'Auto-Run Tests||Device Protection||Battery Health||IMEI/MEID||WiFi||Bluetooth||Continue||Repeat||Skip'
    validateAutoTestScreenData = [ [ ( 'text' , 'element parameter' , '' , False , False , '' ),( 'validate screen text' , 'appium action' , expectedAutoTestScreenText , False , False , '' )] ]
    if sa.Sequential_Actions(validateAutoTestScreenData) == 'failed': shutdown()
    time.sleep(3)

#Step-7.1: Start ProD Test (click on CONTINUE Button)
#     startProdTestData = [ [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/continueButton' , False , False , '' ) , ( 'sleep' , 'appium action' , '30' , False , False , '' )  , ( 'click' , 'appium action' , 'click' , False , False , '' ) ] ]
    startProdTestData = [ [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/continueButton' , False , False ) , ( 'wait' , 'appium action' , '30' , False , False ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/continueButton' , False , False ) , ( 'click' , 'appium action' , 'click' , False , False ) ] ]
    if sa.Sequential_Actions(startProdTestData) == 'failed': shutdown()
    time.sleep(3)

#Step-7.2: Permission request
    permissionData = [ [ ( 'id' , 'element parameter' , 'com.android.packageinstaller:id/permission_allow_button' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) ] ]
    sa.Sequential_Actions(permissionData)

#Step-8(s): Compare (all) string(s) of Main Microphone Record test
    expectedMainMicRecordScreenText = 'Main Microphone Record||Record for 3 second(s) then play it back.||Start Recording||Cover the top microphone with your finger. Press Start when ready.||Pass||Repeat||Fail'
    validateMainMicRecordScreenData = [ [ ( 'text' , 'element parameter' , '' , False , False , '' ),( 'validate screen text' , 'appium action' , expectedMainMicRecordScreenText , False , False , '' )] ]
    if sa.Sequential_Actions(validateMainMicRecordScreenData) == 'failed': shutdown()
    
#Step-8.1: Main Microphone Record test
#     mainMicRecordData = [ [ ( 'text' , 'element parameter' , 'Main Microphone Record' , False , False , '' ) , ( 'true' , 'appium conditional action' , '2,3,4,1' , False , False , '' ) , ( 'false' , 'appium conditional action' , '5' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/passButtonTextView' , False , False , '' ) , ( 'get location' , 'appium action' , 'coordinates' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/startButton' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) ]  , [ ( 'sleep' , 'appium action' , '10' , False , False , '' ) ]  , [ ( 'tap location' , 'appium action' , '%|coordinates|%' , False , False , '' ) , ( 'step result' , 'appium action' , 'pass' , False , False , '' ) ]  , [ ( 'step result' , 'appium action' , 'fail' , False , False , '' ) ] ]
#     mainMicRecordData = [ [ ( 'text' , 'element parameter' , 'Main Microphone Record' , False , False , '' ) , ( 'true' , 'appium conditional action' , '2,3,1' , False , False , '' ) , ( 'false' , 'appium conditional action' , '4' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/startButton' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) ]  , [ ( 'sleep' , 'appium action' , '10' , False , False , '' ) , ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/passButtonTextView' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) , ( 'step result' , 'appium action' , 'pass' , False , False , '' ) ]  , [ ( 'step result' , 'appium action' , 'fail' , False , False , '' ) ] ]
    mainMicRecordData = [ [ ( 'text' , 'element parameter' , 'Main Microphone Record' , False , False ) , ( 'true' , 'appium conditional action' , '2,3,4,5' , False , False ) , ( 'false' , 'appium conditional action' , '6' , False , False ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/passButtonTextView' , False , False ) , ( 'get location' , 'appium action' , 'coordinates' , False , False ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/startButton' , False , False ) , ( 'click' , 'appium action' , 'click' , False , False ) ]  , [ ( 'sleep' , 'appium action' , '10' , False , False ) ]  , [ ( 'tap location' , 'appium action' , '%|coordinates|%' , False , False ) , ( 'step result' , 'appium action' , 'pass' , False , False ) ]  , [ ( 'step result' , 'appium action' , 'fail' , False , False ) ] ]
    if sa.Sequential_Actions(mainMicRecordData) == 'failed': shutdown()
    time.sleep(3)

#Step-9(s): Compare (all) string(s) of Main Microphone Loopback test
    expectedMainMicLoopbackScreenText = 'Main Microphone Loopback||Speak into the bottom microphone and confirm that your voice is played back clearly in the receiver speaker.||Confirm Pass, Fail or press the menu button for more options.||Pass||Repeat||Fail'
    validateMainMicLoopbackScreenData = [ [ ( 'text' , 'element parameter' , '' , False , False , '' ),( 'validate screen text' , 'appium action' , expectedMainMicLoopbackScreenText , False , False , '' )] ]
    if sa.Sequential_Actions(validateMainMicLoopbackScreenData) == 'failed': shutdown()
    
#Step-9.1: Main Microphone Loopback test
    mainMicLoopbackData = [ [ ( 'text' , 'element parameter' , 'Main Microphone Loopback' , False , False , '' ) , ( 'true' , 'appium conditional action' , '2' , False , False , '' ) , ( 'false' , 'appium conditional action' , '3' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/passButtonTextView' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) , ( 'step result' , 'appium action' , 'pass' , False , False , '' ) ]  , [ ( 'step result' , 'appium action' , 'fail' , False , False , '' ) ] ]
    if sa.Sequential_Actions(mainMicLoopbackData) == 'failed': shutdown()
    time.sleep(3)

#Step-10(s): Compare (all) string(s) of Secondary Microphone Record test
    expectedSecMicRecordScreenText = 'Secondary Microphone Record||Record for 3 second(s) then play it back.||Start Recording||Cover the bottom microphone with your finger. Press Start when ready.||Pass||Repeat||Fail'
    validateSecMicRecordScreenData = [ [ ( 'text' , 'element parameter' , '' , False , False , '' ),( 'validate screen text' , 'appium action' , expectedSecMicRecordScreenText , False , False , '' )] ]
    if sa.Sequential_Actions(validateSecMicRecordScreenData) == 'failed': shutdown()
    
#Step-10.1: Secondary Microphone Record test
    secMicRecordData =     [ [ ( 'text' , 'element parameter' , 'Secondary Microphone Record' , False , False , '' ) , ( 'true' , 'appium conditional action' , '2,3,4,5' , False , False , '' ) , ( 'false' , 'appium conditional action' , '6' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/passButtonTextView' , False , False , '' ) , ( 'get location' , 'appium action' , 'coordinates' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/startButton' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) ]  , [ ( 'sleep' , 'appium action' , '10' , False , False , '' ) ]  , [ ( 'tap location' , 'appium action' , '%|coordinates|%' , False , False , '' ) , ( 'step result' , 'appium action' , 'pass' , False , False , '' ) ]  , [ ( 'step result' , 'appium action' , 'fail' , False , False , '' ) ] ]
    if sa.Sequential_Actions(secMicRecordData) == 'failed': shutdown()
    time.sleep(3)

#Step-11(s): Compare (all) string(s) of Secondary Microphone Loopback test
    expectedSecMicLoopbackScreenText = 'Secondary Microphone Loopback||Speak into the top microphone and confirm that your voice is played back clearly in the loudspeaker.||Confirm Pass, Fail or press the menu button for more options.||Pass||Repeat||Fail'
    validateSecMicLoopbackScreenData = [ [ ( 'text' , 'element parameter' , '' , False , False , '' ),( 'validate screen text' , 'appium action' , expectedSecMicLoopbackScreenText , False , False , '' )] ]
    if sa.Sequential_Actions(validateSecMicLoopbackScreenData) == 'failed': shutdown()

#Step-11.1: Secondary Microphone Loopback test
    secMicLoopbackData = [ [ ( 'text' , 'element parameter' , 'Secondary Microphone Loopback' , False , False , '' ) , ( 'true' , 'appium conditional action' , '2' , False , False , '' ) , ( 'false' , 'appium conditional action' , '3' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/passButtonTextView' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) , ( 'step result' , 'appium action' , 'pass' , False , False , '' ) ]  , [ ( 'step result' , 'appium action' , 'fail' , False , False , '' ) ] ]
    if sa.Sequential_Actions(secMicLoopbackData) == 'failed': shutdown()
    time.sleep(3)

#Step-12(s): Compare (all) string(s) of Loudspeaker test
    expectedLoudspeakerScreenText = 'Loudspeaker||Playing audio sample through loudspeaker.||Start Playing||Press Start Playing button when ready.||Pass||Repeat||Fail'
    validateLoudspeakerScreenData = [ [ ( 'text' , 'element parameter' , '' , False , False , '' ),( 'validate screen text' , 'appium action' , expectedLoudspeakerScreenText , False , False , '' )] ]
    if sa.Sequential_Actions(validateLoudspeakerScreenData) == 'failed': shutdown()

#Step-12.1: Loudspeaker test
    loudSpeakerData = [ [ ( 'text' , 'element parameter' , 'Loudspeaker' , False , False , '' ) , ( 'true' , 'appium conditional action' , '2,3,4,5' , False , False , '' ) , ( 'false' , 'appium conditional action' , '6' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/passButtonTextView' , False , False , '' ) , ( 'get location' , 'appium action' , 'coordinates' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/startButton' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) ]  , [ ( 'sleep' , 'appium action' , '5' , False , False , '' ) ]  , [ ( 'tap location' , 'appium action' , '%|coordinates|%' , False , False , '' ) , ( 'step result' , 'appium action' , 'pass' , False , False , '' ) ]  , [ ( 'step result' , 'appium action' , 'fail' , False , False , '' ) ] ]
    if sa.Sequential_Actions(loudSpeakerData) == 'failed': shutdown()
    time.sleep(3)
    
#Step-13(s): Compare (all) string(s) of Receiver Speaker test
    expectedReceiverSpeakerScreenText = 'Receiver Speaker||Play sample through receiver speaker.||Start Playing||Press Start Playing button when ready.||Pass||Repeat||Fail'
    validateReceiverSpeakerScreenData = [ [ ( 'text' , 'element parameter' , '' , False , False , '' ),( 'validate screen text' , 'appium action' , expectedReceiverSpeakerScreenText , False , False , '' )] ]
    if sa.Sequential_Actions(validateReceiverSpeakerScreenData) == 'failed': shutdown()

#Step-13.18: Receiver Speaker test
    receiverSpeakerData = [ [ ( 'text' , 'element parameter' , 'Receiver Speaker' , False , False , '' ) , ( 'true' , 'appium conditional action' , '2,3,4,5' , False , False , '' ) , ( 'false' , 'appium conditional action' , '6' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/passButtonTextView' , False , False , '' ) , ( 'get location' , 'appium action' , 'coordinates' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/startButton' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) ]  , [ ( 'sleep' , 'appium action' , '5' , False , False , '' ) ]  , [ ( 'tap location' , 'appium action' , '%|coordinates|%' , False , False , '' ) , ( 'step result' , 'appium action' , 'pass' , False , False , '' ) ]  , [ ( 'step result' , 'appium action' , 'fail' , False , False , '' ) ] ]
    if sa.Sequential_Actions(receiverSpeakerData) == 'failed': shutdown()
    time.sleep(3)

#Step-14(s): Compare (all) string(s) of LCD Paint test
    expectedLCDPaintScreenText = 'LCD Paint||Paint the screen with your finger.||Start||Press start to begin. Press the back button to exit.||Pass||Repeat||Fail'
    validateLCDPaintScreenData = [ [ ( 'text' , 'element parameter' , '' , False , False , '' ),( 'validate screen text' , 'appium action' , expectedLCDPaintScreenText , False , False , '' )] ]
    if sa.Sequential_Actions(validateLCDPaintScreenData) == 'failed': shutdown()

#Step-14.1: LCD Paint test
    lcdPaintData = [ [ ( 'text' , 'element parameter' , 'LCD Paint' , False , False , '' ) , ( 'true' , 'appium conditional action' , '2,3,4' , False , False , '' ) , ( 'false' , 'appium conditional action' , '5' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/startButton' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) ]  , [ ( 'swipe' , 'appium action' , 'left-right, top-bottom, small' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/passButtonTextView' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) , ( 'step result' , 'appium action' , 'pass' , False , False , '' ) ]  , [ ( 'step result' , 'appium action' , 'fail' , False , False , '' ) ] ]
    if sa.Sequential_Actions(lcdPaintData) == 'failed': shutdown()
    time.sleep(3)

#Step-15(s): Compare (all) string(s) of LCD Fill test
    expectedLCDFillScreenText = 'LCD Fill||Look for missing pixels.||Swipe right to examine the different screens.||Pass||Repeat||Fail'
    validateLCDFillScreenData = [ [ ( 'text' , 'element parameter' , '' , False , False , '' ),( 'validate screen text' , 'appium action' , expectedLCDFillScreenText , False , False , '' )] ]
    if sa.Sequential_Actions(validateLCDFillScreenData) == 'failed': shutdown()

#Step-15.1: LCD Fill test
    lcdFillData = [ [ ( 'text' , 'element parameter' , 'LCD Fill' , False , False , '' ) , ( 'true' , 'appium conditional action' , '2,3' , False , False , '' ) , ( 'false' , 'appium conditional action' , '4' , False , False , '' ) ]  , [ ( 'swipe' , 'appium action' , 'right,3' , False , False , '' ) ]  , [ ( 'id' , 'element parameter' , 'com.assetscience.tauschrausch:id/passButtonTextView' , False , False , '' ) , ( 'click' , 'appium action' , 'click' , False , False , '' ) , ( 'step result' , 'appium action' , 'pass' , False , False , '' ) ]  , [ ( 'step result' , 'appium action' , 'fail' , False , False , '' ) ] ]
    if sa.Sequential_Actions(lcdFillData) == 'failed': shutdown()
    time.sleep(3)

#Step-16(s): Compare (all) string(s) of Result Sent screen
#     expectedResultScreenText = 'Test Results||Sending results||LCD Paint||Bluetooth||Device Protection||LCD Fill||Receiver Speaker||Secondary Microphone Loopback||Secondary Microphone Record||Loudspeaker||Battery Health||Main Microphone Loopback||Main Microphone Record||IMEI/MEID||WiFi'
    expectedResultScreenText = 'Your test results have been submitted'
    validateResultScreenData = [ [ ( 'text' , 'element parameter' , expectedResultScreenText , False , False , '' ),( 'validate full text' , 'appium action' , expectedResultScreenText , False , False , '' )] ]
    if sa.Sequential_Actions(validateResultScreenData) == 'failed': shutdown()

#Step-16.1: Result Sent
    resultSentData = [ [ ( 'text' , 'element parameter' , 'Your test results have been submitted' , False , False ) , ( 'wait' , 'appium optional action' , '10' , False , False ) ] ]
    if sa.Sequential_Actions(resultSentData) == 'failed': shutdown()
    time.sleep(3)

#Step-17.1:Clear Cache
    clearCache = [ [ ( 'reset' , 'appium action' , 'reset' , False , False ) ] ]
    sa.Sequential_Actions(clearCache)
    
# #step17.x: Close the session
#     closeSessionData = [ [ ( 'Authorization' , 'headers' , 'Bearer %|access_token|%' , False , False , '' ) , ( 'method' , 'element parameter' , 'put' , False , False , '' ) , ( 'status' , 'body' , 'closed' , False , False , '' ) , ( 'Content-Type' , 'headers' , 'application/json' , False , False , '' ) , ( 'save response' , 'appium action' , 'none' , False , False , '' ) , ( 'url' , 'element parameter' , 'https://pdm-qa.asci.io/api/sessions/%|id|%' , False , False , '' ) ] ]
#     bfr.Sequential_Actions(closeSessionData)

#Step-17.2: Close Mobile Application
    closeAppData = [ [ ( 'close' , 'appium action' , 'close' , False , False , '' ) ] ]
    sa.Sequential_Actions(closeAppData)
    
#Step-17.3: Teardown
    tearDownData = [ [ ( 'teardown' , 'appium action' , 'teardown' , False , False , '' ) ] ]
    sa.Sequential_Actions(tearDownData)
    
# Calling the function(s) locally
AfterSaleRunThroughPassAll ()


