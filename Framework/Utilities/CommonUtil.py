# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

import sys
import inspect
import os, psutil
import logging
from Framework.Utilities import ConfigModule
import datetime
from Framework.Utilities import FileUtilities as FL
import uuid
from Framework.Utilities import RequestFormatter
import subprocess

temp_config=os.path.join(os.path.join(FL.get_home_folder(),os.path.join('Desktop',os.path.join('AutomationLog',ConfigModule.get_config_value('Temp','_file')))))

passed_tag_list = ['Pass', 'pass', 'PASS', 'PASSED', 'Passed', 'passed', 'true', 'TRUE', 'True', '1', 'Success','success', 'SUCCESS', True]
failed_tag_list = ['Fail', 'fail', 'FAIL', 'Failed', 'failed', 'FAILED', 'false', 'False', 'FALSE', '0', False]
skipped_tag_list=['skip','SKIP','Skip','skipped','SKIPPED','Skipped']



def to_unicode(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
        return obj

def encode_to_exclude_symbol(sDetails):
    replace_dict={
        '#': '||6||',
        '=': '||5||'
    }
    for e in replace_dict.keys():
        sDetails = sDetails.replace(e, replace_dict[e])
    return sDetails

def Add_Folder_To_Current_Test_Case_Log(src):
    try:
        #get the current test case locations
        dest_folder = ConfigModule.get_config_value('sectionOne', 'test_case_folder',temp_config)
        folder_name = filter(lambda x:x!='', src.split('/'))[-1]
        if folder_name:
            des_path = os.path.join(dest_folder, folder_name)
            FL.copy_folder(src, des_path)
            return True
        else:
            return False

    except Exception, e:
        return Exception_Handler(sys.exc_info())


def Add_File_To_Current_Test_Case_Log(src):
    try:
        #get the current test case locations
        dest_folder = ConfigModule.get_config_value('sectionOne', 'test_case_folder',temp_config)
        file_name = filter(lambda x:x!='', src.split('/'))[-1]
        if file_name:
            des_path = os.path.join(dest_folder, file_name)
            FL.copy_file(src, des_path)
            return True
        else:
            return False

    except Exception, e:
        return Exception_Handler(sys.exc_info())

def Exception_Handler(exec_info, temp_q=None,UserMessage=None):

    try:
        sModuleInfo_Local = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        exc_type, exc_obj, exc_tb = exec_info
        Error_Type = (str(exc_type).replace("type ", "")).replace("<", "").replace(">", "").replace(";", ":")
        Error_Message = str(exc_obj)
        File_Name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Function_Name = os.path.split(exc_tb.tb_frame.f_code.co_name)[1]
        Line_Number = str(exc_tb.tb_lineno)
        Error_Detail = "Error Type ~ %s: Error Message ~ %s: File Name ~ %s: Function Name ~ %s: Line ~ %s"%(Error_Type, Error_Message, File_Name, Function_Name,Line_Number)
        sModuleInfo = Function_Name + ":" +File_Name
        ExecLog(sModuleInfo, "Following exception occurred: %s" %( Error_Detail), 3)
        TakeScreenShot(Function_Name+"~"+File_Name)
        if UserMessage != None:
                ExecLog(sModuleInfo, "Following error message is custom: %s" %(UserMessage), 3)
        if temp_q != None:
            temp_q.put("failed")

        return "failed"

    except Exception:
        exc_type_local, exc_obj_local, exc_tb_local = sys.exc_info()
        fname_local = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail_Local = ((str(exc_type_local).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj_local) +";" + "File Name: " + fname_local + ";" + "Line: "+ str(exc_tb_local.tb_lineno))
        ExecLog(sModuleInfo_Local, "Following exception occurred: %s" %( Error_Detail_Local), 3)
        return "failed"


def Result_Analyzer(sTestStepReturnStatus,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

    try:
        if sTestStepReturnStatus in passed_tag_list:
            temp_q.put("passed")
            return "passed"
        elif sTestStepReturnStatus in failed_tag_list:
            temp_q.put("failed")
            return "failed"
        elif sTestStepReturnStatus in skipped_tag_list:
            temp_q.put("skipped")
            return "skipped"
        else:
            ExecLog(sModuleInfo,"Step return type unknown: %s" %(sTestStepReturnStatus),3)
            temp_q.put("failed")
            return "failed"


    except Exception, e:
        return Exception_Handler(sys.exc_info())

def ExecLog(sModuleInfo, sDetails, iLogLevel=1, local_run=False, sStatus=""):
    try:
        local_run = ConfigModule.get_config_value('RunDefinition','local_run')
        debug_mode = ConfigModule.get_config_value('RunDefinition', 'debug_mode')
        
        # ";" is not supported for logging.  So replacing them
        sDetails = sDetails.replace(";", ":")
        sDetails = sDetails.replace("=", "~")
        sDetails = encode_to_exclude_symbol(to_unicode(sDetails))
        
        #Convert logLevel from int to string for clarity
        if iLogLevel == 0:
            if debug_mode.lower() == 'true':
                status = 'Debug' # This is not displayed on the server log, just in the console
            else: # Do not display this log line anywhere
                return
        elif iLogLevel == 1:
            status = 'Passed'
        elif iLogLevel == 2:
            status = 'Warning'
        elif iLogLevel == 3:
            status = 'Error'
        else:
            print "*** Unknown log level- Set to Warning ***"
            status = 'Warning'

        # Display on console
        print "%s - %s\n\t%s" % (status.upper(), sModuleInfo, sDetails)

        # Upload logs to server if local run is not set to False
        if (local_run == False or local_run == 'False') and iLogLevel > 0:
            log_id=ConfigModule.get_config_value('sectionOne','sTestStepExecLogId',temp_config)
            FWLogFile = ConfigModule.get_config_value('sectionOne','log_folder',temp_config)
            if FWLogFile=='':
                FWLogFile=ConfigModule.get_config_value('sectionOne','temp_run_file_path',temp_config)+os.sep+'execlog.log'
            else:
                FWLogFile=FWLogFile+os.sep+'temp.log'
            
            logger = logging.getLogger(__name__)
            
            hdlr = None
            if os.name == 'posix':
                try:
                    hdlr = logging.FileHandler(FWLogFile)
                except:
                    pass
            elif os.name == 'nt':
                hdlr = logging.FileHandler(FWLogFile)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            if hdlr != None:
                hdlr.setFormatter(formatter)
                logger.addHandler(hdlr)
            
            logger.setLevel(logging.DEBUG)
            logger.info(sModuleInfo + ' - ' + sDetails + '' + sStatus)
            logger.removeHandler(hdlr)

            # Write log line to server
            r = RequestFormatter.Get('log_execution',{'logid': log_id, 'modulename': sModuleInfo, 'details': sDetails, 'status': status,'loglevel': iLogLevel})

    except Exception, e:
        return Exception_Handler(sys.exc_info())

def FormatSeconds(sec):
        hours, remainder = divmod(sec, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_formatted = '%d:%02d:%02d' % (hours, minutes, seconds)
        return duration_formatted

def PhysicalAvailableMemory():
    try:
        return (int(str(psutil.virtual_memory().available))) / (1024 * 1024)

    except Exception, e:
        return Exception_Handler(sys.exc_info())

#####New screenshot testing
#!!! STATUS: UNTESTED. NEED TO KNOW HOW TO DECIDE IF DESKTOP OR MOBILE SCREENSHOT
#sudo pip install pyscreenshot

from PIL import Image # Picture quality
try: from PIL import ImageGrab as ImageGrab_Mac_Win # Screen capture for Mac and Windows
except: pass
try: import pyscreenshot as ImageGrab_Linux # Screen capture for Linux/Unix
except: pass

temp_config=os.path.join(os.path.join(FL.get_home_folder(),os.path.join('Desktop',os.path.join('AutomationLog',ConfigModule.get_config_value('Temp','_file')))))

def TakeScreenShot(ImageName,local_run=False):
    ''' Capture screen of mobile or desktop '''
    
    # Define variables
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    chars_to_remove = ["?","*","\"","<",">","|","\\","\/",":"] # Symbols that can't be used in filename
    picture_quality = 4 # Quality of picture
    picture_size = 800, 600 # Size of image (for reduction in file size)

    # Read values from config file
    take_screenshot_settings = ConfigModule.get_config_value('RunDefinition', 'take_screenshot') # True/False to take screenshot from settings.conf
    local_run = ConfigModule.get_config_value('RunDefinition', 'local_run') # True/False to run only locally, in which case we do not take screenshot from settings.conf
    image_folder=ConfigModule.get_config_value('sectionOne','screen_capture_folder', temp_config) # Get screen capture directory from temporary config file that is dynamically created

    # Decide if screenshot should be captured
    if take_screenshot_settings.lower() == 'false' or local_run.lower() == 'false':
        return

    # Adjust filename and create full path (remove invalid characters, convert spaces to underscore, remove leading and trailing spaces)
    ImageName=os.path.join(image_folder, TimeStamp("utc") + "_" + (ImageName.translate(None,''.join(chars_to_remove))).strip().replace(" ","_") + ".jpg")

    # Capture screenshot of desktop
    if sys.platform == 'linux2':
        image = ImageGrab_Linux.grab()
    elif sys.platform  == 'win32' or sys.platform  == 'darwin':
        image = ImageGrab_Mac_Win.grab()
    image.save(ImageName, format = "JPEG") # Save to disk

    # Capture screenshot of mobile
    #??? Where do we get this? How to get from Zeuz ??? Do we need to pass the driver?
    #How to get driver?: driver.save_screenshot(ImageName)
    
    # Lower the picture quality
    image = Image.open(ImageName) # Re-open in standard format
    image.thumbnail(picture_size, Image.ANTIALIAS) # Resize picture to lower file size
    image.save(ImageName, format = "JPEG", quality = picture_quality) # Change quality to reduce file size


def TakeScreenShot_old(ImageName,local_run=False):

    """
    Takes screenshot and saves it as jpg file
    name is the name of the file to be saved appended with timestamp
    #TakeScreenShot("TestStepName")
    """
    #file Name don't contain \/?*"<>|
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    take_screenshot_settings = ConfigModule.get_config_value('RunDefinition', 'take_screenshot')
    if take_screenshot_settings == 'True':
        local_run = ConfigModule.get_config_value('RunDefinition', 'local_run')
        chars_to_remove=["?","*","\"","<",">","|","\\","\/",":"]
        ImageName=(ImageName.translate(None,''.join(chars_to_remove))).replace(" ","_").strip()
        print ImageName
        try:
            if local_run == 'False':
                image_folder=ConfigModule.get_config_value('sectionOne','screen_capture_folder',temp_config)
                #ImageFolder = Global.TCLogFolder + os.sep + "Screenshots"
                ImageFolder=image_folder
                if sys.platform == 'posix':
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
                    #os.system("import -window root %s"%full_location)
                     
                    try:
                        from gi.repository import Gdk
 
                    except ImportError:
                        print 'could not import python package needed for screenshot...installing package "gi"'
                        os.system('pip install gi')
                # set the root window as the window we want for screenshot
                    window = Gdk.get_default_root_window()
                    # get dimensions of the window
                    x, y, width, height = window.get_geometry()
                     
                    print 'taking screenshot...'
                    # take screenshot
                    img = Gdk.pixbuf_get_from_window(window, x, y, width, height)
                     
                    if img:
                        from PIL import Image
                        img.savev(full_location, "png", (), ())
                        file1 = full_location
                        file2 = full_location
                        size = 800, 450
                     
                        im = Image.open(file1)
                        im.thumbnail(size, Image.ANTIALIAS)
                        im.save(file2, "JPEG")
                        print 'screenshot saved as: "%s"' % full_location
                    else:
                        print "unable to take screenshot..."
 
                #mobile device working copy
                elif sys.platform == 'linux2':
                    #mobile device connected to linux machine
                     
                    #android working copy
                    '''
                    try:
                        output = os.system("adb devices")
                        if output is not None:
                            full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'_android.png'
                            #os.system("adb shell screencap -p | perl -pe 's/\x0D\x0A/\x0A/g' > %s"%full_location)
                            os.system("adb shell screencap -p /sdcard/screen.png")
                            os.system("adb pull /sdcard/screen.png %s"%full_location)
                            from PIL import Image
                            im = Image.open(full_location)
                            im.save(full_location, format="JPEG", quality=4)
 
                    except Exception, e:
                        return Exception_Handler(sys.exc_info())
 
                    #ios device working copy
                    full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'_ios.tiff'
                    os.system("idevicescreenshot %s"%full_location)
                    '''
 
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
                        from PIL import Image
                        im = Image.open(full_location)
                        im.save(full_location, format="JPEG", quality=4)
 
                    #iphone working copy
                    output = os.system("ioreg -w -p IOUSB | grep -w iPhone")
                    if output is not None:
                        full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'_ios.tiff'
                        os.system("idevicescreenshot %s"%full_location)
 
                    #ipad working copy
                    output = os.system("ioreg -w -p IOUSB | grep -w iPad")
                    if output is not None:
                        full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'_ios.tiff'
                        os.system("idevicescreenshot %s"%full_location)
 
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
                            from PIL import Image
                            im = Image.open(full_location)
                            im.save(full_location, format="JPEG", quality=4)
 
            elif os.name == 'nt':
                #windows working copy


                from PIL import ImageGrab
                from PIL import Image
                path = ImageFolder + os.sep + TimeStamp("utc") + "_" + ImageName + ".jpg"
                print path
                img = ImageGrab.grab()
                basewidth = 1200
                wpercent = (basewidth/float(img.size[0]))
                hsize = int((float(img.size[1])*float(wpercent)))
                img = img.resize((basewidth,hsize), Image.ANTIALIAS)
                img.save(path, 'JPEG')

                # android working copy
                try:
                    '''
                    @sreejoy please make sure this is handled nicely.  This is very much hard coded. and causing a lot of issues.
                    we should also consider iOS as well.
                    right now returning pass so i can run test cases
                    '''
                    return 'passed' 
                    output = os.system("adb devices")
                    if output is not None:
                        full_location = ImageFolder + os.sep + TimeStamp("utc") + "_" + ImageName + '_android.png'
                        # os.system("adb shell screencap -p | perl -pe 's/\x0D\x0A/\x0A/g' > %s"%full_location)
                        os.system("adb shell screencap -p /sdcard/screen.png")
                        os.system("adb pull /sdcard/screen.png %s" % full_location)
                        from PIL import Image
                        im = Image.open(full_location)
                        im.save(full_location, format="JPEG", quality=4)

                except Exception, e:
                    return Exception_Handler(sys.exc_info())
            else:
                ExecLog(sModuleInfo,"OS is unknown: %s" %(os.name),3)
                return Exception_Handler(sys.exc_info())
                
 
        except Exception, e:
            return Exception_Handler(sys.exc_info())

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
            return Exception_Handler(sys.exc_info())

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


        except Exception:
            ErrorMessage =  "Unable to set create a Node key.  Please check class MachineInfo() in commonutil"
            return Exception_Handler(sys.exc_info(), None, ErrorMessage)
    def getUniqueId(self):
        """
        :return: returns the local pc unique ID
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
                    machine_name = str(unique_id)
                    return machine_name[:100]
                machine_name = str(unique_id)
            else:
                #create the file name
                f=open(node_id_file_path,'w')
                f.close()
                unique_id=uuid.uuid4()
                unique_id=str(unique_id)[:10]
                ConfigModule.add_section('UniqueID',node_id_file_path)
                ConfigModule.add_config_value('UniqueID','id',unique_id,node_id_file_path)
                machine_name = str(unique_id)
            return machine_name[:100]


        except Exception:
            ErrorMessage =  "Unable to set create a Node key.  Please check class MachineInfo() in commonutil"
            return Exception_Handler(sys.exc_info(), None, ErrorMessage)





