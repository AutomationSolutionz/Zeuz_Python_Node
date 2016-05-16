# -*- coding: utf-8 -*-
import sys
from ConfigParser import NoOptionError,NoSectionError
import os, psutil
import DataBaseUtilities as DB
import logging
from Utilities import ConfigModule
import datetime
from Utilities import FileUtilities as FL
import uuid
from PIL import ImageGrab
from PIL import Image
temp_config=os.path.join(os.path.join(FL.get_home_folder(),os.path.join('Desktop',os.path.join('AutomationLog',ConfigModule.get_config_value('Temp','_file')))))

def to_unicode(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
        return obj

def ExecLog(sModuleInfo, sDetails, iLogLevel=1, local_run=False, sStatus=""):
    try:
        if local_run == False:
            print sModuleInfo, ":", sDetails
            log_id=ConfigModule.get_config_value('sectionOne','sTestStepExecLogId',temp_config)
            FWLogFile = ConfigModule.get_config_value('sectionOne','log_folder',temp_config)
            if FWLogFile=='':
                FWLogFile=ConfigModule.get_config_value('sectionOne','temp_run_file_path',temp_config)+os.sep+'execlog.log'
            else:
                FWLogFile=FWLogFile+os.sep+'temp.log'
            
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
            image_folder=ConfigModule.get_config_value('sectionOne','screen_capture_folder',temp_config)
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
                
                #linux working copy
                full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'.png'
                os.system("import -window root %s"%full_location)
                
                #mobile device working copy
                if sys.platform == 'linux2':
                    #mobile device connected to linux machine
                    
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
                    #mobile device connected to mac os x machine
                    
                    #ios device working copy
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
                    
                    #android working copy
                    output = os.system("adb devices")
                    if output is not None:
                        full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'_android.png'
                        #os.system("adb shell screencap -p | perl -pe 's/\x0D\x0A/\x0A/g' > %s"%full_location)
                        os.system("adb shell screencap -p /sdcard/screen.png")
                        os.system("adb pull /sdcard/screen.png %s"%full_location)

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
def TimeStamp(format):
    """
    :param format: name of format ex: string , integer
    :return:
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
        TimeStamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    elif format == "utc":
        TimeStamp = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S-%f')
    elif format == "utcstring":
        TimeStamp = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    else:
        TimeStamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')

    return TimeStamp

class MachineInfo():
    def getLocalIP(self):
        """
        :return: get local address of machine
        """
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("gmail.com",80))
            ip = (s.getsockname()[0])
            s.close()
            return ip
        except Exception, e:
            print "Exceptioin: ", e
            return False
    def getLocalUser(self):
        """
        :return: returns the local pc name
        """
        try:
            node_id_file_path=os.path.join(FL.get_home_folder(),os.path.join('Desktop','node_id.conf'))
            if os.path.isfile(node_id_file_path):
                unique_id=ConfigModule.get_config_value('UniqueID','id',node_id_file_path)
                if unique_id=='':
                    ConfigModule.clean_config_file(node_id_file_path)
                    ConfigModule.add_section('UniqueID', node_id_file_path)
                    unique_id = uuid.uuid4()
                    unique_id = str(unique_id)[:10]
                    ConfigModule.add_config_value('UniqueID', 'id', unique_id,node_id_file_path)
                    machine_name = ConfigModule.get_config_value('Authentication', 'username') +'_' +str(unique_id)
                    return machine_name[:100]
                machine_name = ConfigModule.get_config_value('Authentication', 'username') +'_' +str(unique_id)
            else:
                #create the file name
                f=open(node_id_file_path,'w')
                f.close()
                unique_id=uuid.uuid4()
                unique_id=str(unique_id)[:10]
                ConfigModule.add_section('UniqueID',node_id_file_path)
                ConfigModule.add_config_value('UniqueID','id',unique_id,node_id_file_path)
                machine_name = ConfigModule.get_config_value('Authentication', 'username') +'_' +str(unique_id)
            return machine_name[:100]

        except Exception, e:
            #incase exception happens for whatever reason.. we will return the timestamp...
            print "Exception: ", e
            print "Unable to set create a Node key.  Please check class MachineInfo() in commonutil"
            return False
        



