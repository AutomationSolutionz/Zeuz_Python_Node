# -*- coding: utf-8 -*-
import sys
from ConfigParser import NoOptionError
sys.path.append("..")

import time, datetime, inspect
from dateutil.relativedelta import relativedelta
import os, signal, stat
import subprocess, psutil
import string
import DataBaseUtilities as DB
import logging
import FileUtilities as FileUtil
import re
import math
import Global
import ConfigParser
if os.name == 'nt':
    from AutomationFW.PCDesktop import WinCommonFoldersPaths as ComPath
    import win32com.client
    import wmi
    import win32api
    import win32file
    from PIL import ImageGrab
    from PIL import Image
elif os.name == 'posix':
    from AutomationFW.MacDesktop import MacCommonFoldersPaths as ComPath
    import plistlib
    try:
	from appscript import *
    except:
	pass
    
def ExecLog(sModuleInfo, sDetails, iLogLevel=1, local_run=False, sStatus=""):
    """
    1- info
    2 - warning
    3 - error
    """
    try:
        if local_run == False:
            print sModuleInfo, ":", sDetails
            if Global.sTestStepExecLogId=='':
                #global_config.ini file get is dynamically
                file_path=os.getcwd()+os.sep+'global_config.ini'
                config=ConfigParser.ConfigParser()
                config.read(file_path)
                log_id=config.get('sectionOne','sTestStepExecLogId')
            else:
                log_id=Global.sTestStepExecLogId
            
            config=ConfigParser.ConfigParser()
            file_path=os.getcwd()+os.sep+'global_config.ini' 
            config.read(file_path)
            try:
                FWLogFile = config.get('sectionOne','log_folder')+os.sep+'temp.log'
            except NoOptionError,e:
                FWLogFile=config.get('sectionOne','temp_run_file_path')+os.sep+'execlog.log'
            
            logger = logging.getLogger(__name__)
            if os.name == 'posix':
                try:
                    hdlr = logging.FileHandler(FWLogFile)
                except:
                    pass
            elif os.name == 'nt':
                hdlr = logging.FileHandler(FWLogFile)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            hdlr.setFormatter(formatter)
            logger.addHandler(hdlr)
            logger.setLevel(logging.DEBUG)
            
            conn = DB.ConnectToDataBase()
            sDetails = to_unicode(sDetails)
            if iLogLevel == 1:
                logger.info(sModuleInfo + ' - ' + sDetails + '' + sStatus)
                DB.InsertNewRecordInToTable(conn, 'execution_log', logid=log_id, modulename=sModuleInfo, details=sDetails, status="Passed", loglevel=iLogLevel)
        
            elif iLogLevel == 2:
                logger.warning(sModuleInfo + ' - ' + sDetails + '' + sStatus)
                DB.InsertNewRecordInToTable(conn, 'execution_log', logid=log_id, modulename=sModuleInfo, details=sDetails, status="Warning", loglevel=iLogLevel)
        
            elif iLogLevel == 3:
                logger.error(sModuleInfo + ' - ' + sDetails + '' + sStatus)
                DB.InsertNewRecordInToTable(conn, 'execution_log', logid=log_id, modulename=sModuleInfo, details=sDetails, status="Error", loglevel=iLogLevel)
        
            elif iLogLevel == 4:
                logger.info(sModuleInfo + ' - ' + sDetails + '' + sStatus)
        
            else:
                print "unknown log level"
            
            logger.removeHandler(hdlr)
            conn.close()
        else:
            print sModuleInfo, ":", sDetails
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print Error_Detail
        

def ClearLog():
    try:
        with open(FWLogFile, 'w'):
            pass
    except Exception, e:
        print "Cannot clear log:", e

def GetAllProcesses_Mac():
    """
    This function is only for MAC
    """

    try:
        ps = subprocess.Popen("ps aux", shell=True, stdout=subprocess.PIPE)
        procList = ps.stdout.read()
#        print procList
        ps.stdout.close()
        ps.wait()
        return procList
    except Exception, e:
        print "Exception: ", e
        return False

def GetProcessID_Win(ProcessName):
    c = wmi.WMI()
    ProcessID = False
    for process in c.Win32_Process (name=ProcessName):
        ProcessID = process.ProcessId
        print process.ProcessId, process.Name
    return ProcessID

def GetProcessID_Mac(ProcessName):
    try:
        ProcessList = GetAllProcesses_Mac()
        #print ProcessList
        print "Getting Process Id for process name: " + ProcessName
        for line in ProcessList.splitlines():
            #if ProcessName in line:
            if ProcessName in line.split(None)[len(line.split(None)) - 1]:
                pid = int(line.split(None)[1])
                print "Process Id = ", pid
                return pid
            #To find process names with spaces in their name
            try:
                if ProcessName == line.split('/', 1)[1].rsplit(None, 1)[0].rsplit('/', 1)[1]:
                    pid = int(line.split(None)[1])
                    print "Process Id = ", pid
                    return pid
            except:
                pass
        return False
    except Exception, e:
        print "Exception: '%s'" % e
        return False

def GetProcessId(ProcessName):
    if os.name == 'nt':
        return GetProcessID_Win(ProcessName)
    elif os.name == 'posix':
        return GetProcessID_Mac(ProcessName)

def GetProcessName(pid):
    """
    @summary: Returns process name of a process if a matching PID is found. else return False
    """
    for proc in psutil.process_iter():
        if proc.pid == pid:
            return proc.name
    return False


def WaitForProcessToQuit(ProcessName, MaxWaitInMiliSecond=100):
    try:
        seconds = 0
        while GetProcessId(ProcessName) != False:
            print "Your Application " + ProcessName + " Is still running"
            time.sleep(0.1)
            seconds = seconds + 1
            if seconds > 1000:
                return False
            KillAllCrash()
        print "Your Application " + ProcessName + " Is NOT running now"
        return True
    except Exception, e:
        print "Exception:", e
        return False

def WaitForProcessToQuitById(ProcessId, MaxWaitInMiliSecond=100):
    """
    This fn is only for Mac. Not tested for PC
    """
    try:
        seconds = 0
        if os.name == 'posix':
            while seconds < MaxWaitInMiliSecond:
                try:
                    os.kill(ProcessId, 0)
                    print "Process: %s Is still running" % ProcessId
                except:
                    print "Process: %s Is Not running" % ProcessId
                    return True

                time.sleep(1)
                seconds = seconds + 1
                if seconds > 10:
                    return False
                KillAllCrash()
        elif os.name == 'nt':
            while seconds < MaxWaitInMiliSecond:
                try:
                    os.kill(ProcessId, 0)
                    print "Process: %s Is still running" % ProcessId
                except:
                    print "Process: %s Is Not running" % ProcessId
                    return True

                time.sleep(1)
                seconds = seconds + 1
                if seconds > 10:
                    #ExecLog(sModuleInfo,"Process by id is still running. Failed to kill : %s" %ProcessId,2)
                    return False
                KillAllCrash()

        return True
    except Exception, e:
        print "Exception:", e
        return False

def WaitForProcessToStart(ProcessName, MaxWaitInMiliSecond):
    try:
        seconds = 0
        while GetProcessID(ProcessName) != True:
            print "Your Application " + ProcessName + " is NOT started"
            time.sleep(0.1)
            seconds = seconds + 1
            if seconds > 1000:
                return False
            KillAllCrash()
        print "Your Application " + ProcessName + " is Started"
        return True
    except Exception, e:
        print "Exception:", e
        return False

def KillProcessByName_Win(ProcessName):
        c = wmi.WMI()
        print "looking to kill process name: " + ProcessName
        try:
            for process in c.Win32_Process(name=ProcessName):
                process.Terminate ()
                print "Killed process name: " + ProcessName
        except Exception, e:
             print "Exception: '%s'" % e

def KillProcessByName_Mac(ProcessName):
#    c = wmi.WMI()
    try:
        ProcessList = GetAllProcesses_Mac()
        print "looking to kill process name: " + ProcessName
        for line in ProcessList.splitlines():
            if ProcessName in line.split(None)[len(line.split(None)) - 1]:
                pid = int(line.split(None)[1])
#                print pid
                os.kill(pid, signal.SIGKILL)
                print "Killed process name: " + ProcessName
                print "Killed process pid: %i" % pid
                return True
            #For processes with space in their name
            try:
                if ProcessName == line.split('/', 1)[1].rsplit(None, 1)[0].rsplit('/', 1)[1]:
                    pid = int(line.split(None)[1])
                    os.kill(pid, signal.SIGKILL)
                    print "Killed process name: " + ProcessName
                    return True
            except:
                pass

        return False
    except Exception, e:
        print "Exception: '%s'" % e
        return False

def KillProcessByName(ProcessName):
    if os.name == 'nt':
        return KillProcessByName_Win(ProcessName)
    elif os.name == 'posix':
        return KillProcessByName_Mac(ProcessName)

def FindingProcess(sProName):
    try:
        if os.name == 'nt':
            proAvailable = False
            strComputer = "."
            objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            objSWbemServices = objWMIService.ConnectServer(strComputer, "root\cimv2")
            colItems = objSWbemServices.ExecQuery("Select * from Win32_Product")
            for objItem in colItems:
                if str(objItem.Caption).find(sProName) == 0:
                    proAvailable = True
                    break
            return proAvailable
        elif os.name == 'posix':
            #terminal command to get all apps
            command = ["system_profiler", "-xml", "SPApplicationsDataType"]
            task = subprocess.Popen(command, stdout=subprocess.PIPE)
            (stdout, unused_stderr) = task.communicate()

            apps = plistlib.readPlistFromString(stdout)[0]["_items"]

            for app in apps:
                if app["_name"] == sProName:
                    print "App found: ", app["_name"]
                    return True
                    break
            print "App not found: ", sProName
            return False
    except Exception, e:
        print "Exception: ", e
        return False

def TimeStamp(format):
    """

    ========= Instruction: ============

    Function Description:
    This function is used to create a Time Stamp.
    It will return current Day-Month-Date-Hour:Minute:Second-Year all in one string
    OR
    It will return current YearMonthDayHourMinuteSecond all in a integer.

    Parameter Description:

    - string: this returns a readable string for the current date and time format
        Example:
        TimeStamp = TimeStamp("string") = Fri-Jan-20-10:20:31-2012

    - integer: this returns a readable string for the current date and time format
        Example:
        TimeStamp = TimeStamp("integer") = 2012120102051
    ======= End of Instruction: =========

    """
    if format == "string":
        TimeStamp = datetime.datetime.now().ctime().replace(' ', '-').replace('--', '-')
    elif format == "integer":
        #TimeStamp = int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        TimeStamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        #print TimeStamp
#        now = datetime.datetime.now()
#        year = "%d" % now.year
#        month = "%d" % now.month
#        day = "%d" % now.day
#        hour = "%d" % now.hour
#        minute = "%d" % now.minute
#        second = "%d" % now.second
#        TimeStamp = year + month + day + hour + minute + second
        #TimeStamp = int (TimeStamp)
    elif format == "utc":
        TimeStamp = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S-%f')
    elif format == "utcstring":
        TimeStamp = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    else:
        TimeStamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')

    return TimeStamp

def IncrementLocalDateByDays(numDays):

    """
    Description: This function will increment the windows date by the specified
                number of days. Accounts for month and year as well.
    """

    try:
        #Getting Current System Time
        current_time = win32api.GetSystemTime()

        #Assigning current_time to new_time as a list
        new_time = list(current_time)

        """new_time variable will have following items in the form of list
         Year(YYYY), Month(MO), Day Of Week(DW), Day(DD), Hour(HH), Minutes(MM), Seconds(SE), MiliSecond(MS)
        """

        # Increment days one at a time. This way we can increment the month/year if necessary
        # Only works for positive dats
        while (numDays != None) and (numDays > 0) :
            new_time[3] += 1
            numDays -= 1

            if ((new_time[1] == 2) and (new_time[3] > 28)):
                new_time[1] += 1
                new_time[3] = 1

            elif (((new_time[1] == 4) or (new_time[1] == 6) or (new_time[1] == 9) or (new_time[1] == 11)) and new_time[3] > 30):
                new_time[1] += 1
                new_time[3] = 1

            elif (new_time[3] > 31):
                new_time[1] += 1
                new_time[3] = 1

                if (new_time[1] > 12):
                    new_time[1] = 1
                    new_time[0] += 1

        YYYY, MO, DW, DD, HH, MM, SE, MS = new_time
        win32api.SetSystemTime(YYYY, MO, DW, DD, HH, MM, SE, MS)
        return True

    except Exception, e:
        print "Exception: CommonUtil > IncrementSystemDateByDays  had an error (%s) " % e
        return False

def SetLocalDateTime(YYYY=None, MO=None, DW=None, DD=None, HH=None, MM=None, SE=None, MS=None):

    """
    Description: SetLocalDateTime() takes int as input for Data or time to add or subtract
    Example: 1) If you want set the day ahead 2 days from today
                Today's Date = 27/07/2012
                SetLocalDateTime(DD=2)
                Now Today's Data = 29/07/2012

            2) if you want set the day back 2 days from today
                Today's Date = 27/07/2012
                SetLocalDateTime(DD= -2)
                Now Today's Data = 25/07/2012

    Similar pattern will work for year, month, day of week, hour, minute, second, miliSecond


    """
    try:
        #Getting Current System Time
        current_time = win32api.GetSystemTime()

        #Assigning current_time to new_time as a list
        new_time = list(current_time)

        """new_time variable will have following items in the form of list
         Year(YYYY), Month(MO), Day Of Week(DW), Day(DD), Hour(HH), Minutes(MM), Seconds(SE), MiliSecond(MS)
        """

        #Changing Year
        if YYYY != None:
            new_time[0] += YYYY

        #Changing Month
        if MO != None:
            new_time[1] += MO

        #Changing Day Of Week
        if DW != None:
            new_time[2] += DW

        #Changing Day
        if DD != None:
            new_time[3] += DD

        #Changing Hour
        if HH != None:
            new_time[4] += HH

        #Changing Minutes
        if MM != None:
            new_time[5] += MM

        #Changing Seconds
        if SE != None:
            new_time[6] += SE

        #Changing MiliSeconds
        if MS != None:
            new_time[7] += MS

        YYYY, MO, DW, DD, HH, MM, SE, MS = new_time


        win32api.SetSystemTime(YYYY, MO, DW, DD, HH, MM, SE, MS)

        return True

    except Exception, e:
        print "Exception: CommonUtil > SetLocalDataTime  had an error (%s) " % e
        return False

def ReadFile(filename):
    print "reading file from ", filename
    with open(filename, 'r') as fileObj:
        x = fileObj.read()
        fileObj.close()
    print "File Object Closed: ", fileObj.closed
    return(x)

def WriteToFile(fileName, cont):
    fileObj = open(fileName, 'w')     # Writing permission
    fileObj.write(cont)
    fileObj.close()


def GetDictFromTuples(tuples, inputLabels):
    dict = {}

    for importKey in inputLabels.keys():

        matchList = [item for item in tuples if item[0] == inputLabels[importKey]]

        dict[importKey] = k.missing_value

        if len(matchList) == 1 and matchList[0] != None and matchList[0][1] != None:
            dict[importKey] = matchList[0][1]

    return dict


def GetRegistryValue(sRegistryPath, sValueName):
    """
    GetProductVersion takes two arguments for HKEY_LOCAL_MACHINE
    sRegistryPath: Registry path of required folder
    sValueName:  Name of required value

    """
    import _winreg as WinReg
    #aReg = WinReg.ConnectRegistry(None,HKEY_LOCAL_MACHINE)
    aKey = WinReg.OpenKey(WinReg.HKEY_LOCAL_MACHINE, r"%s" % sRegistryPath)
    return WinReg.QueryValueEx(aKey, sValueName)[0]

def GetLocalOS():
    import platform
    if os.name == 'nt':
        return platform.system() + " " + platform.release()
    elif os.name == 'posix':
        return platform.system() + " " + platform.mac_ver()[0]

def GetLocalUser():
    if os.name == 'nt':
        return os.getenv("USERNAME")
    elif os.name == 'posix':
        #return pwd.getpwuid( os.getuid() )[ 0 ]
        #For Mac, machines hostname will be used as User Id
        #Get a userid from automation team and set it as your mac machine host name
        #run this command in terminal
        #sudo scutil --set HostName new_hostname
        import socket
        return socket.gethostname()


def GetLocalUserHomePath():
    if os.name == 'nt':
        return os.getenv("USERNAME")
    elif os.name == 'posix':
        return os.getenv("HOME")


def GetOSBit():
    if os.name == 'nt':
        if 'PROGRAMFILES(X86)' in os.environ:
            return '64'
        else:
            return '32'
    elif os.name == 'posix':
        import platform
        if '64' in platform.mac_ver()[2]:
            return '64'
        else:
            return '32'

def GetProductVersion():
    if os.name == 'nt':
        import _winreg as WinReg
        aKey = WinReg.OpenKey(WinReg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ProductRegPath")
        return str(WinReg.QueryValueEx(aKey, "Version")[0])
    elif os.name == 'posix':
        return FileUtil.getFileVersion('ProductName')

def GetProductBundle():
    if os.name == 'nt':
        import _winreg as WinReg
        #aReg = WinReg.ConnectRegistry(None,HKEY_LOCAL_MACHINE)
        aKey = WinReg.OpenKey(WinReg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ProductRegPath")
        return str(WinReg.QueryValueEx(aKey, "BundleNumber")[0])
    elif os.name == 'posix':
        return 'NA'

def GetProductLogFile():
    """
    returns path of the DTS desktop.log file path
    """
    try:
        return False
    except Exception, e:
        print "Exception : ", e
        return False

def FormatSeconds(sec):
        hours, remainder = divmod(sec, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_formatted = '%d:%02d:%02d' % (hours, minutes, seconds)
        return duration_formatted

def PhysicalAvailableMemory():
    try:
        return (int(str(psutil.virtual_memory().available))) / (1024 * 1024)
    except Exception, e:
        print "Exception %s" % e
        return 0

def SendEmail(ToEmailAddress, Subject, Body=None , type=None):
    from mailer import Mailer
    from mailer import Message
    

    ToAddr = ToEmailAddress.split(',')
    message = Message(From="automation.solutionz@gmail.com",
                      To=ToAddr,
                      charset="utf-8")
    if type == 'Daily_Build':
        Conn = DB.ConnectToDataBase()
        EnvInfo = DB.GetData(Conn, "Select machine_os,client,test_run_type,test_objective from test_run_env where run_id = '%s'" % Subject, False)
        DesktopInfo = ''
        DeviceInfo = ''
        #Branch bundle info
        BranchInfo = ''
        BundleInfo = ''
        for eachitem in EnvInfo[0][1].split(','):
            if 'branch' in eachitem.lower():
                if len(eachitem.split(':')) > 0:
                    BranchInfo = eachitem.split(':')[1]
                    #break
            elif 'bundle' in eachitem.lower():
                if len(eachitem.split(':')) > 1:
                    BundleInfo = eachitem.split(':')[1]

        BuildPath = DB.GetData(Conn, "Select build_path from daily_build_status where run_id = '%s' limit 1" % Subject, False)
        if len(BuildPath) > 0:
            BuildPath = BuildPath[0][0]
            if 'http://' in BuildPath:
                BuildPath = BuildPath
            else:
                BuildPath = "file:///" + BuildPath
        else:
            BuildPath = ""
        Run_TestCases = DB.GetData(Conn, "select "
                                            "tr.tc_id, "
                                            "tc.tc_name "
                            " from test_run tr, test_cases tc "
                           "where tr.run_id = '%s' and "
                           "tr.tc_id = tc.tc_id order by tc.tc_id" % (Subject), False)

        if EnvInfo[0][0].lower().startswith('win'):
            SubjectLine = "PC %s Test - %s - %s" % (EnvInfo[0][5], BranchInfo, BundleInfo)
        else:
            SubjectLine = "Mac %s Test - %s - %s" % (EnvInfo[0][5], BranchInfo, BundleInfo)
        message.Subject = "Started %s" % SubjectLine
        message.Html = """<strong>Starting Test Run with id <a href="http://%s/Search/RunID/%s">%s</a>.</strong>! Click on the link for details.""" % (Global.go_url, Subject, Subject)

        # Environmnet Details Section
        Body = """<Body>
                        <br><br>
                            <table border = 1 width="500"><caption style="background-color:#56BAEC;font-weight:bold;font-size:18.0pt">Environment Details</caption>
                                <tr><td style="font-weight:bold;">OS</td><td>%s</td></tr>
                """ % (EnvInfo[0][0])
        #If BuildPath is found for the Daily Build, then use it to create a link. Otherwise just display the Build number
        if str(BuildPath) == "":
            Body = Body + """
                                <tr><td style="font-weight:bold;">Desktop</td><td>%s</td></tr>
                """ % (DesktopInfo)
        else:
            Body = Body + """
                                <tr><td style="font-weight:bold;">Desktop</td><td><a href="%s">%s</a></td></tr>
                """ % (BuildPath, DesktopInfo)

        Body = Body + """
                                <tr><td style="font-weight:bold;">Device</td><td>%s</td></tr>
                                <tr><td style="font-weight:bold;">Client</td><td>%s</td></tr>
                            </table>
                                """ % (DeviceInfo, EnvInfo[0][3])

        #Running Test Cases Section
        #If the test run has any test cases to Run, then add Run Test Cases section to the email body
        if len(Run_TestCases) > 0:
            #beginning of Run test cases table
            Body = Body + """
                        <br><br>
                            <table border = 1 width="500"><caption style="background-color:#56BAEC;font-weight:bold;font-size:18.0pt">Running Test Cases</caption>
                                <tr style="font-weight:bold" align=center><td>ID</td><td>Name</td></tr>
                        """
            #for each test case, add a row to the table 
            for eachitem in Run_TestCases:
                Body = Body + """
                                    <tr><td>%s</td><td>%s</td></tr>

                            """ % (eachitem[0], eachitem[1])
            #End of current Table
            Body = Body + """
                            </table>
                        """
        #End of Email Body                
        Body = Body + """
                            </Body>
                    """

        message.Html = message.Html + Body



    else:
        Conn = DB.ConnectToDataBase()
        TotalTestCase = DB.GetData(Conn, "Select count(*) as TotalTests from test_run_env te, test_run tr where te.run_id = '%s' and te.run_id = tr.run_id" % Subject)
        #TotalRun = DB.GetData(Conn,"Select count(*) as TotalRun from test_case_results where run_id = '%s' and status in ('Passed', 'Failed')"%Subject)
        Passed = DB.GetData(Conn, "Select count(*) as Passed from test_case_results where run_id = '%s' and status = 'Passed'" % Subject)
        Failed = DB.GetData(Conn, "Select count(*) as Passed from test_case_results where run_id = '%s' and status = 'Failed'" % Subject)
        EnvInfo = DB.GetData(Conn, "Select machine_os,client,test_run_type,rundescription from test_run_env where run_id = '%s'" % Subject, False)
        #Branch bundle info
        BranchInfo = ''
        BundleInfo = ''
        for eachitem in EnvInfo[0][1].split(','):
            if 'branch' in eachitem.lower():
                if len(eachitem.split(':')) > 0:
                    BranchInfo = eachitem.split(':')[1]
                    #break
            elif 'bundle' in eachitem.lower():
                if len(eachitem.split(':')) > 0:
                    BundleInfo = eachitem.split(':')[1]
                    break

        BuildPath = DB.GetData(Conn, "Select build_path from daily_build_status where run_id = '%s' limit 1" % Subject, False)
        if len(BuildPath) > 0:
            BuildPath = BuildPath[0][0]
        else:
            BuildPath = ""
        Pass_TestCases = DB.GetData(Conn, "select "
                                            "tc.tc_id, "
                                            "tc.tc_name "
                            " from test_case_results tr, test_cases tc "
                           "where tr.run_id = '%s' and tr.status = 'Passed' and "
                           "tr.tc_id = tc.tc_id order by tr.id" % (Subject), False)
        Fail_TestCases = DB.GetData(Conn, "select "
                                            "tc.tc_id, "
                                            "tc.tc_name, "
                                            "tr.failreason "
                            " from test_case_results tr, test_cases tc "
                           "where tr.run_id = '%s' and tr.status = 'Failed' and "
                           "tr.tc_id = tc.tc_id order by tr.id" % (Subject), False)
        Fail_TCIds = []
        Fail_RelatedItems = []
        for eachTC in Fail_TestCases:
            Fail_TCIds.append(eachTC[0])

        if len(Fail_TCIds) > 0:
            Fail_RelatedItems = MKS.Find_DevTask(Fail_TCIds)
            if Fail_RelatedItems != False:
                if len(Fail_TCIds) != len(Fail_RelatedItems):
                    print "Mismatch between number of test cases failed and related items list from MKS"
                    Fail_RelatedItems = []
            elif Fail_RelatedItems == False:
                print "Cant find Related items from MKS or some exception like Integrity not installed"
                Fail_RelatedItems = []

        if EnvInfo[0][3] == "Daily_Build":
            if EnvInfo[0][0].lower().startswith('win'):
                SubjectLine = "PC %s Test - %s - %s" % (EnvInfo[0][5], BranchInfo, BundleInfo)
            else:
                SubjectLine = "Mac %s Test - %s - %s" % (EnvInfo[0][5], BranchInfo, BundleInfo)

            message.Subject = "Completed %s" % SubjectLine
        else:
            message.Subject = "Completed %s" % EnvInfo[0][1]
        message.Html = """<strong>Test Run with id <a href="http://%s/Search/RunID/%s">%s</a> is completed.</strong>! Click on the link for details.""" % (Global.go_url, Subject, Subject)
        #message.Body = """%s""" %Body

        #Start building the body of the email
        # Results Summary Section 
        Body = """<Body><br><br>
                            <table border = 1 width="500"><caption style="background-color:#56BAEC;font-weight:bold;font-size:18.0pt">Results Summary</caption>
                                <tr style="background-color:#E0F8F7;font-weight:bold;"><td>Total Tests</td><td align=center>%s</td></tr>
                                <tr style="background-color:#9FDA58;font-weight:bold;"><td>Total Passed</td><td align=center>%s</td></tr>
                                <tr style="background-color:#F5A9A9;font-weight:bold;"><td>Total Failed</td><td align=center>%s</td></tr>
                            </table>
                """ % (TotalTestCase[0], Passed[0], Failed[0])

        #Display each item of desktop & device info on separate lines; so replace commas with new lines
        DesktopInfo = ''
        DeviceInfo = ''

        # Environmnet Details Section
        Body = Body + """
                        <br><br>
                            <table border = 1 width="500"><caption style="background-color:#56BAEC;font-weight:bold;font-size:18.0pt">Environment Details</caption>
                                <tr><td style="font-weight:bold;">OS</td><td>%s</td></tr>
                    """ % (EnvInfo[0][0])

        #If BuildPath is found for the Daily Build, then use it to create a link. Otherwise just display the Build number
        if str(BuildPath) == "":
            Body = Body + """
                                <tr><td style="font-weight:bold;">Build</td><td>%s</td></tr>
                """ % (DesktopInfo)
        else:
            Body = Body + """
                                <tr><td style="font-weight:bold;">Build</td><td><a href="file:///%s">%s</a></td></tr>
                """ % (BuildPath, DesktopInfo)

        Body = Body + """
                                
                                <tr><td style="font-weight:bold;">Client</td><td>%s</td></tr>
                            </table>
                                """ % (EnvInfo[0][3])

        #If the test run has any failed test case, then add Failed Test Cases section to the email body
        if len(Fail_TestCases) > 0:
            #beginning of failed test cases table
            Body = Body + """
                        <br><br>
                            <table border = 1><caption style="background-color:#F5A9A9;font-weight:bold;font-size:18.0pt">Failed Test Cases</caption>
                                <tr style="font-weight:bold" align=center><td rowspan=2 style="width:20px">ID</td><td rowspan=2 style="width:75px">Name</td><td rowspan=2 style="width:125px">Reason for Failure</td><td colspan=3 style="width:200px">Related MKS Defects</td></tr>
                                <tr style="font-weight:bold" align=center><td style="width:25px">MKS Id</td><td style="width:125px">Defect Title</td><td style="width:25px">Defect Status</td></tr>
                        """
            #for each failed test case, add a row to the table
            Fail_Index = 0
            for eachitem in Fail_TestCases:
                if len(Fail_RelatedItems) > 0:
                    if len(Fail_RelatedItems[Fail_Index]) > 0:
                        NumRelItems = len(Fail_RelatedItems[Fail_Index])
                        Rel_Index = 0
                        for eachRelItem in Fail_RelatedItems[Fail_Index]:
                            if Rel_Index == 0:
                                Body = Body + """
                                                    <tr><td rowspan=%s><a href="http://mksintegrity:7001/im/issues?selection=%s">%s</a></td><td rowspan=%s>%s</td><td rowspan=%s>%s</td><td><a href="http://mksintegrity:7001/im/issues?selection=%s">%s</a></td><td colspan=1>%s</td><td>%s</td></tr>

                                            """ % (NumRelItems, eachitem[0], eachitem[0], NumRelItems, eachitem[1], NumRelItems, eachitem[2], eachRelItem[0], eachRelItem[0], eachRelItem[1], eachRelItem[2])
                            else:
                                Body = Body + """
                                                    <tr><td><a href="http://mksintegrity:7001/im/issues?selection=%s">%s</a></td><td>%s</td><td>%s</td></tr>

                                            """ % (eachRelItem[0], eachRelItem[0], eachRelItem[1], eachRelItem[2])
                            Rel_Index = Rel_Index + 1

                    else:
                        NumRelItems = 1

                        Body = Body + """
                                            <tr><td><a href="http://mksintegrity:7001/im/issues?selection=%s">%s</a></td><td>%s</td><td>%s</td><td colspan=3></td></tr>

                                    """ % (eachitem[0], eachitem[0], eachitem[1], eachitem[2])
                    Fail_Index = Fail_Index + 1
                else:
                    Body = Body + """
                                        <tr><td><a href="http://mksintegrity:7001/im/issues?selection=%s">%s</a></td><td>%s</td><td>%s</td><td colspan=3></td></tr>

                                """ % (eachitem[0], eachitem[0], eachitem[1], eachitem[2])

            #End of current Table
            Body = Body + """
                            </table>
                        """

        #If the test run has any passed test case, then add Passed Test Cases section to the email body
        if len(Pass_TestCases) > 0:
            #beginning of Passed test cases table
            Body = Body + """
                        <br><br>
                            <table border = 1 width="500"><caption style="background-color:#9FDA58;font-weight:bold;font-size:18.0pt">Passed Test Cases</caption>
                                <tr style="font-weight:bold;" align=center><td>ID</td><td>Name</td></tr>
                        """
            #for each Passed test case, add a row to the table 
            for eachitem in Pass_TestCases:
                Body = Body + """
                                    <tr><td><a href="http://mksintegrity:7001/im/issues?selection=%s">%s</a></td><td>%s</td></tr>

                            """ % (eachitem[0], eachitem[0], eachitem[1])
            #End of current table
            Body = Body + """
                            </table>
                        """
        #End of Email Body                
        Body = Body + """
                            </Body>
                    """

        message.Html = message.Html + Body
    username = "AutomationReport@automationsolutionz.com"
    password = "te@mWork"

    sender = Mailer('smtp.automationsolutionz.com','25', True, username, password)
    sender.send(message)


def InstallUninstallBuild(installLocation):
    try:
        process = subprocess.Popen(installLocation, shell=True)
        #print process
        process.wait()
        time.sleep(4)
        return 1
    except Exception, e:
        print "Exception %s" % e
        return 0

def TakeScreenShot(ImageName,local_run=False):
    """
    Takes screenshot and saves it as jpg file
    name is the name of the file to be saved appended with timestamp
    #TakeScreenShot("TestStepName")
    """
    #file Name don't contain \/?*"<>|
    chars_to_remove=["?","*","\"","<",">","|","\\","\/",":"]
    ImageName=(ImageName.translate(None,''.join(chars_to_remove))).replace(" ","_").strip()
    print ImageName
    try:
        if local_run == False:
            config=ConfigParser.ConfigParser()
            config.read(os.getcwd()+os.sep+'global_config.ini')
            image_folder=config.get('sectionOne','screen_capture_folder')
            #ImageFolder = Global.TCLogFolder + os.sep + "Screenshots"
            ImageFolder=image_folder
            if os.name == 'posix':
                """
                ImageFolder = FileUtil.ConvertWinPathToMac(ImageFolder)
                path = ImageFolder + os.sep + TimeStamp("utc") + "_" + ImageName + ".png"
    
                newpath = ImageFolder + os.sep + TimeStamp("utc") + "_" + ImageName + ".jpg"
                path = path.replace(" ", "_")
                newpath = newpath.replace(" ", "_")
                os.system("screencapture \"" + path + "\"")
                #reduce size of image
                os.system("sips -s format jpeg -s formatOptions 30 " + path + " -o " + newpath)
                os.system("rm " + path)
                """
                if sys.platform == 'linux2':
                    #linux working copy
                    full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'.png'
                    os.system("import -window root %s"%full_location)
                
                    #android working copy
                    output = os.system("adb devices")
                    if output is not None:
                        full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'_android.png'
                        #os.system("adb shell screencap -p | perl -pe 's/\x0D\x0A/\x0A/g' > %s"%full_location)
                        os.system("adb shell screencap -p /sdcard/screen.png")
                        os.system("adb pull /sdcard/screen.png %s"%full_location)
                        
                    #ios device working copy
                    full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'_ios.tiff'
                    os.system("idevicescreenshot"%full_location)
                        
                elif sys.platform == 'darwin':
                    #mac working copy
                    full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'.png'
                    os.system("screencapture ~%s"%full_location)
                
                    #android working copy
                    output = os.system("adb devices")
                    if output is not None:
                        full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'_android.png'
                        #os.system("adb shell screencap -p | perl -pe 's/\x0D\x0A/\x0A/g' > %s"%full_location)
                        os.system("adb shell screencap -p /sdcard/screen.png")
                        os.system("adb pull /sdcard/screen.png %s"%full_location)
                        
                    #iphone working copy
                    output = os.system("ioreg -w -p IOUSB | grep -w iPhone")
                    if output is not None:
                        full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'_ios.tiff'
                        os.system("idevicescreenshot %s"%full_location)
                    
                    #ipad working copy
                    output = os.system("ioreg -w -p IOUSB | grep -w iPad")
                    if output is not None:
                        full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'_ios.tiff'
                        os.system("idevicescreenshot"%full_location)
                        
                else:
                    #linux working copy
                    full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'.png'
                    os.system("import -window root %s"%full_location)

            elif os.name == 'nt':
                path = ImageFolder + os.sep + TimeStamp("utc") + "_" + ImageName + ".jpg"
                img = ImageGrab.grab()
                basewidth = 1200
                wpercent = (basewidth/float(img.size[0]))
                hsize = int((float(img.size[1])*float(wpercent)))
                img = img.resize((basewidth,hsize), Image.ANTIALIAS)
                img.save(path, 'JPEG')
    except Exception, e:
        print "Exception : ", e


def ZipFolder(dir, zip_file):
    """
    Zips a given folder, its sub folders and files. Ignores any empty folders
    dir is the path of the folder to be zipped
    zip_file is the path of the zip file to be created
    """
    try:
        import zipfile
        zip = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED)
        root_len = len(os.path.abspath(dir))
        for root, dirs, files in os.walk(dir):
            archive_root = os.path.abspath(root)[root_len:]
            for f in files:
                fullpath = os.path.join(root, f)
                archive_name = os.path.join(archive_root, f)
                #print f
                if f not in zip_file:
                    zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)

        zip.close()
        return zip_file
    except Exception, e:
        print "Exception :", e
        return False

def GetProductLog_Win():
    """
    Function will collect .log and .dmp files in specified locations and copies it to network test case folder
    """
    try:
        pass
        #FileUtil.CopyFile(eachfile, Global.TCLogFolder + "\\ProductLog\\")
    except Exception, e:
        print "Exception:", e

def GetProductLog_Mac():
    """
    Function will collect Desktop.log and .dmp files in specified locations and copies it to network test case folder
    """
    try:
        pass
    except Exception, e:
        print "Exception:", e

def GetProductLog():
    if os.name == 'nt':
        return GetProductLog_Win()
    elif os.name == 'posix':
        return GetProductLog_Mac()

def isAvailable(path):
    winCMD = 'IF EXIST ' + chr(34) + path + chr(34) + ' echo YES'
    cmdOutPut = subprocess.Popen(winCMD, stdout=subprocess.PIPE, shell=True).communicate()
    return string.find(str(cmdOutPut), 'YES',)

def mapNetworkDrive(drive, networkPath, user, password):
    try:

        #Check for network resource availability
        if isAvailable(networkPath) == -1:
            print "Path not accessible: ", networkPath
            #Network path is not reachable
            #return -1
        else:
            print "Path accessible. No need to map: ", networkPath
            return True

        #Check for drive availability
        if isAvailable(drive) > -1:
            #Drive letter is already in use
            #return False
            if unmapNetworkDrive(drive) == False:
                return False

        #Prepare 'NET USE' commands
        #winCMD = """NET USE %s %s "%s" /User:%s""" %(drive,networkPath,password,user)
        winCMD = "NET USE %s " % drive + chr(34) + networkPath + chr(34) + " " + chr(34) + password + chr(34) + " /User:%s" % (user)

        #print "winCMD = ", winCMD
        #Execute 'NET USE' command with authentication
        cmdOutPut = subprocess.Popen(winCMD, stdout=subprocess.PIPE, shell=True).communicate()
        #print "Executed: ", winCMD
        if string.find(str(cmdOutPut), 'successfully',) == -1:
            "print Mapping drive FAILED"
            #print winCMD, " FAILED"
            return False
        #Mapped with first try
        return True
    except Exception, e:
        print "Exception:", e
        return False

def unmapNetworkDrive(drive):
    try:
        #Check if the drive is in use
        if isAvailable(drive) == -1:
            #Drive is not in use
            return False

        #Prepare 'NET USE' command
        winCMD = 'net use ' + drive + ' /DELETE'
        cmdOutPut = subprocess.Popen(winCMD, stdout=subprocess.PIPE, shell=True).communicate()
        if string.find(str(cmdOutPut), 'successfully',) == -1:
            #Could not UN-MAP, this might be a physical drive
            "print UnMapping drive FAILED"
            return False
        #UN-MAP successful
        return True
    except Exception, e:
        print "Exception:", e
        return False

def to_unicode(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
        return obj

class LocalInfo():
    """
    gets local machine info and uploads it to database
    """
    def getInstalledClients_Win(self):
        
        '''
            In future we should collect this list from the dependency clients.  Any run time settings that would have version
            should fall under "Clients".  This would help us maintain the code better and dynamically manage what type of application run manager
            collects.  This list will define what the version we should collect when run manager runs
        '''
                
        try:

            list_of_clients = ["Chrome","FireFox","IE"]
            Clients = []
            #FireFox
            if "FireFox" in list_of_clients:
                try:
                    OLPath = False
                    allFiles = FileUtil.SearchFiles(ComPath.Get_Program_Files_Path() + os.sep + "Mozilla Firefox", "firefox.exe")
                    #print allFiles
                
                    for eachFile in allFiles:
                        if os.path.basename(eachFile) == 'firefox.exe':
                            OLPath = eachFile
                            break
                    if OLPath == False:
                        allFiles = FileUtil.SearchFiles("C:\\Program Files\\Mozilla Firefox", "firefox.exe")
                        for eachFile in allFiles:
                            if os.path.basename(eachFile) == 'firefox.exe':
                                OLPath = eachFile
                                break
                    if OLPath:
                        if os.path.isfile(OLPath):
                            #Version
                            fileVer = "Unknown Version"
                            fileVer = FileUtil.getFileVersion(OLPath)
                
                
                                #fileVer = fileVer[0:4]
                            #Bitness
                            fileBit = win32file.GetBinaryType(OLPath)
                            if fileBit == 0:
                                fileBit = "32"
                            elif fileBit == 6:
                                fileBit = "64"
                            else:
                                fileBit = ""
                            Clients.append("FireFox(" +"V" + str(fileVer) +";"+ fileBit +"Bit)")
                except Exception, e:
                    print "Error getting FireFox information:", e
            #IE
            if "IE" in list_of_clients:
                try:
                    OLPath = False
                    allFiles = FileUtil.SearchFiles(ComPath.Get_Program_Files_Path() + os.sep + "Internet Explorer", "iexplore.exe")
                    #print allFiles
                
                    for eachFile in allFiles:
                        if os.path.basename(eachFile) == 'iexplore.exe':
                            OLPath = eachFile
                            break
                    if OLPath == False:
                        allFiles = FileUtil.SearchFiles("C:\\Program Files\\Internet Explorer", "iexplore.exe")
                        for eachFile in allFiles:
                            if os.path.basename(eachFile) == 'iexplore.exe':
                                OLPath = eachFile
                                break
                    if OLPath:
                        if os.path.isfile(OLPath):
                            #Version
                            fileVer = "Unknown Version"
                            fileVer_ = FileUtil.getFileVersion(OLPath)
                            #fileVer = fileVer_.split(".")[0] +"."+ fileVer_.split(".")[1]+ "."+ fileVer_.split(".")[2]
                            fileVer = fileVer_.split(".")[0] 
                            #fileVer = fileVer[0:4]
                            #Bitness
                            fileBit = win32file.GetBinaryType(OLPath)
                            if fileBit == 0:
                                fileBit = "32"
                            elif fileBit == 6:
                                fileBit = "64"
                            else:
                                fileBit = ""
                            Clients.append("IE(" +"V" + str(fileVer) +";"+ fileBit +"Bit)")
                except Exception, e:
                    print "Error getting IE information:", e
                
            #Chrome
            if "Chrome" in list_of_clients:
                try:
                    OLPath = False
                    allFiles = FileUtil.SearchFiles(ComPath.Get_Program_Files_Path() + os.sep + "Google\\Chrome\\Application", "chrome.exe")
                    #print allFiles
                
                    for eachFile in allFiles:
                        if os.path.basename(eachFile) == 'chrome.exe':
                            OLPath = eachFile
                            break
                    if OLPath == False:
                        allFiles = FileUtil.SearchFiles("Google\\Chrome\\Application", "chrome.exe")
                        for eachFile in allFiles:
                            if os.path.basename(eachFile) == 'chrome.exe':
                                OLPath = eachFile
                                break
                    if OLPath:
                        if os.path.isfile(OLPath):
                            #Version
                            fileVer = "Unknown Version"
                            fileVer_ = FileUtil.getFileVersion(OLPath)
                            #fileVer = fileVer_.split(".")[0] +"."+ fileVer_.split(".")[1]+ "."+ fileVer_.split(".")[2]
                            fileVer = fileVer_.split(".")[0] 
                            #fileVer = fileVer[0:4]
                            #Bitness
                            fileBit = win32file.GetBinaryType(OLPath)
                            if fileBit == 0:
                                fileBit = "32"
                            elif fileBit == 6:
                                fileBit = "64"
                            else:
                                fileBit = ""
                            Clients.append("Chrome(" +"V" + str(fileVer) +";"+ fileBit +"Bit)")
                except Exception, e:
                    print "Error getting Chrome information:", e

            if "iTunes" in list_of_clients:
            #iTunes
                if os.path.isfile(ComPath.Get_Program_Files_Path() + "\\iTunes\\iTunes.exe"):
                    fileVer = FileUtil.getFileVersion(ComPath.Get_Program_Files_Path() + "\\iTunes\\iTunes.exe")
                    if fileVer != False:
                        fileVer = fileVer[0:4]
                    Clients.append("iTunes:" + str(fileVer))

            #WMP
            if "WMP" in list_of_clients:
                if os.path.isfile(ComPath.Get_Program_Files_Path() + "\\Windows Media Player\\wmplayer.exe"):
                    fileVer = FileUtil.getFileVersion(ComPath.Get_Program_Files_Path() + "\\Windows Media Player\\wmplayer.exe")
                    if fileVer != False:
                        fileVer = fileVer[0:4]
                    Clients.append("WMP:" + str(fileVer))

            #Outlook
            if "Outlook" in list_of_clients:
                try:
                    OLPath = False
                    allFiles = FileUtil.SearchFiles(ComPath.Get_Program_Files_Path() + os.sep + "Microsoft Office", "OUTLOOK.EXE")
                    for eachFile in allFiles:
                        if os.path.basename(eachFile) == 'OUTLOOK.EXE':
                            OLPath = eachFile
                            break
                    if OLPath == False:
                        allFiles = FileUtil.SearchFiles("C:\\Program Files\\Microsoft Office", "OUTLOOK.EXE")
                        for eachFile in allFiles:
                            if os.path.basename(eachFile) == 'OUTLOOK.EXE':
                                OLPath = eachFile
                                break
                    if OLPath:
                        if os.path.isfile(OLPath):
                            #Version
                            fileVer = FileUtil.getFileVersion(OLPath)
                            if fileVer != False:
                                if fileVer.startswith('15'):
                                    fileVer = "2013"
                                elif fileVer.startswith('14'):
                                    fileVer = "2010"
                                elif fileVer.startswith('12'):
                                    fileVer = "2007"
                                elif fileVer.startswith('11'):
                                    fileVer = "2003"
                                else:
                                    fileVer = ""
    
                                #fileVer = fileVer[0:4]
                            #Bitness
                            fileBit = win32file.GetBinaryType(OLPath)
                            if fileBit == 0:
                                fileBit = "32"
                            elif fileBit == 6:
                                fileBit = "64"
                            else:
                                fileBit = ""
    
                            Clients.append("Outlook:" + str(fileVer) + " " + fileBit)
                except Exception, e:
                    print "Error getting Outlook information:", e

            rVal = ",".join(Clients)
            return rVal
        except Exception, e:
            print "Exceptioin: ", e
            return False

    def getInstalledClients_Mac(self):
        """
        gets Installed clients such as iTunes / iPhoto, iMovie etc
        """
        try:
            Clients = []
            #iTunes
            fileVer = FileUtil.getFileVersion('iTunes')
            if fileVer != False:
                fileVer = fileVer[0:4]
                Clients.append("iTunes:" + str(fileVer))

            #iPhoto
            fileVer = FileUtil.getFileVersion('iPhoto')
            if fileVer != False:
                fileVer = fileVer[0:4]
                Clients.append("iPhoto:" + str(fileVer))

            #iTunes
            fileVer = FileUtil.getFileVersion('iMovie')
            if fileVer != False:
                fileVer = fileVer[0:4]
                Clients.append("iMovie:" + str(fileVer))

            rVal = ",".join(Clients)
            return rVal
        except Exception, e:
            print "Exceptioin: ", e
            return False

    def getInstalledClients(self):
        if os.name == 'nt':
            return self.getInstalledClients_Win()
        elif os.name == 'posix':
            return self.getInstalledClients_Mac()

    def getLocalOS(self):
        """
        gets os info for eg Win 7 32
        """
        #OS
        try:
            return GetLocalOS() + " - " + GetOSBit()
        except Exception, e:
            print "Exceptioin: ", e
            return False

    def getProductInfo(self):
        """
        gets DTS version info and other components
        """
        try:
            rVal = ""
            return rVal

        except Exception, e:
            print "Exceptioin: ", e
            return False


    def getLocalIP(self):
        """
        gets local ip address (public)
        """
        try:
            #Local IP Address
            import socket
            #print socket.gethostbyname(socket.gethostname())
            return socket.gethostbyname_ex(socket.gethostname())[2][0]

        except Exception, e:
            print "Exceptioin: ", e
            return False

    def getLocalUser(self):
        """
        gets local User
        """
        try:
            return GetLocalUser()

        except Exception, e:
            print "Exceptioin: ", e
            return False


    def getMachineName(self):
        import socket
        return socket.gethostname()

def FindTestCaseFailedReason(conn, run_id, tc_id):
    sqlQuery = ("select details from execution_log el, test_step_results tsr"
                 " where el.logid = tsr.logid"
                 " and tsr.run_id = '%s' and tsr.tc_id = '%s' and tsr.status = 'Failed' and el.loglevel = 3" % (run_id, tc_id))
    DataQuery = DB.GetData(conn, sqlQuery, False)
    IgnoreKeywordList = ['Test Case', 'Test Step', 'Test Set']
    Reason = []
    for eachData in DataQuery:
        KWFound = False
        for KW in IgnoreKeywordList:
            if KW in str(eachData):
                KWFound = True
                break
        if KWFound == False:
            Reason.append(to_unicode(eachData[0]))
    print "Failure Reason for Test case: %s - %s" % (tc_id, Reason)
    ReasonStr = ','.join(Reason)
    ReasonStr = (ReasonStr[:100] + '..') if len(ReasonStr) > 100 else ReasonStr
    return ReasonStr


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)

    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse

    fromString = dict((key, value) for key, value in enums.iteritems())
    enums['from_string'] = fromString

    return type('Enum', (), enums)

def Get_ListDifferences(List1, List2):
    #This function will return a list which contains differences between two lists (list1, & List2)
    #This is used mainly in edit scenarios where List1 contains all the fields of an original appointment. List2 also contains
    #fields which are getting edited, deleted, added etc in addition to the fields which are not getting modified. The return
    #list will remove all the fields which are not getting modified
    try:
        diff1 = list(set(List1) - set(List2))
        diff2 = list(set(List2) - set(List1))
        editlist = []
        for eachitem1 in diff1:
            ItemFound = False
            for eachitem2 in diff2:
                if eachitem1[0] == eachitem2[0]:
                   ItemFound = True
                   if eachitem2[1] != '':
                       edititem = (eachitem1[0], eachitem1[1], eachitem2[1], 'Edit')
                   else:
                       edititem = (eachitem1[0], eachitem1[1], eachitem2[1], 'Del')
                   editlist.append(edititem)
                   break
            if ItemFound == False:
                edititem = (eachitem1[0], eachitem1[1], '', 'Del')
                editlist.append(edititem)

        for eachitem2 in diff2:
            ItemFound = False
            for eachitem1 in diff1:
                if eachitem1[0] == eachitem2[0]:
                    ItemFound = True
                    break
                elif eachitem1[1] == eachitem2[1]:
                    ItemFound = True
                    edititem = (eachitem1[0], eachitem1[1], eachitem2[0], 'Swap')
                    editlist.append(edititem)
                    break
            if ItemFound == False:
                edititem = (eachitem2[0], '', eachitem2[1], 'Add')
                editlist.append(edititem)
        return editlist
    except Exception, e:
        return LogFailedException(sModuleInfo, e)



def NormalizeTimeInputs(tupleList):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

    regexTimeValue = re.compile(".*(Months|Years)\s(From|Before).*")
    regexTimeInPast = re.compile(".*(Months|Years)\sBefore.*")
    regexTimeInFuture = re.compile(".*(Months|Years)\sFrom.*")

    returnList = []

    try:

        for i in range(len(tupleList)):
            if (tupleList[i] == None):
                returnList.append(tupleList[i])
                continue

            # All of our time tuples have one label and one value (i.e. 2 values) 
            elif isinstance(tupleList[i][1], basestring):

                if regexTimeValue.match(tupleList[i][1]):
                    # We caught one!
                    if (regexTimeInPast.match(tupleList[i][1]) or
                        regexTimeInFuture.match(tupleList[i][1])):
                        returnList.append(NormalizeTime(tupleList[i]))

                    else:
                        print "Failed failure occurred normalizing time value of %s" % (tupleList[i])
                        ExecLog(sModuleInfo, "Failed failure occurred normalizing time value of %s" % (tupleList[i], 4))
                        return tupleList

                else:
                    returnList.append(tupleList[i])

            else: #isinstance(tupleList[i], (list, tuple))
                # As far as I know, all datasets should contain lists, tuples, or strings and no other types
                # So, if it isn't a string and it isn't none, it must be another list
                if isinstance(tupleList[i], list):
                    returnList.append(NormalizeTimeInputs(tupleList[i]))
                else:
                    assert isinstance(tupleList[i][1], list)
                    returnList.append((tupleList[i][0], NormalizeTimeInputs(tupleList[i][1])))

        return returnList

    except Exception, e:
        print "%s > Exception happened: (%s) " % (sModuleInfo, e)
        ExecLog(sModuleInfo, "Exception: (%s)" % e, 4)
        return tupleList

def NormalizeTime(tuple):
    # All our time strings are the second value in a tuple  with 2 values
    timeString = tuple[1]
    newTuple = None

    regexMonthsBeforeStringBit = re.compile("Months Before Today")
    regexYearsBeforeStringBit = re.compile("Years Before Today")
    regexMonthsFromStringBit = re.compile("Months From Today")
    regexYearsFromStringBit = re.compile("Years From Today")
    daysBefore = "Days Before Today"
    daysFrom = "Days From Today"
    newString = None

    stringBits = timeString.split(":")

    for i in range(len(stringBits)):

        dateOfInterest = None

        if regexMonthsBeforeStringBit.match(stringBits[i]):
            intBit = int(stringBits[i - 1])
            dateOfInterest = datetime.datetime.now() - relativedelta(months=intBit)
            newString = daysBefore
        elif regexYearsBeforeStringBit.match(stringBits[i]):
            intBit = int(stringBits[i - 1])
            dateOfInterest = datetime.datetime.now() - relativedelta(years=intBit)
            newString = daysBefore
        elif regexMonthsFromStringBit.match(stringBits[i]):
            intBit = int(stringBits[i - 1])
            dateOfInterest = datetime.datetime.now() + relativedelta(months=intBit)
            newString = daysFrom
        elif regexYearsFromStringBit.match(stringBits[i]):
            intBit = int(stringBits[i - 1])
            dateOfInterest = datetime.datetime.now() + relativedelta(years=intBit)
            newString = daysFrom

        if dateOfInterest != None:
            delta = datetime.datetime.now() - dateOfInterest

            stringBits[i - 1] = math.fabs(delta.days)
            stringBits[i] = newString

            newTuple = (tuple[0], "%d:%s" % (stringBits[i - 1], stringBits[i]))

    return newTuple

def LogFailedException(sModuleInfo, e):
    print "%s > Exception happened:%s" % (sModuleInfo, e)
    ExecLog(sModuleInfo, "Exception:%s" % e, 2)
    ExecLog(sModuleInfo, "Framework Error", 3)
    return "Failed"
