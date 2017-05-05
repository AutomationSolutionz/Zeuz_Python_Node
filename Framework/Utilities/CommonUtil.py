# -*- coding: utf-8 -*-
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
import string
import random
temp_config=os.path.join(os.path.join(FL.get_home_folder(),os.path.join('Desktop',os.path.join('AutomationLog',ConfigModule.get_config_value('Temp','_file')))))

passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True','1','Success','success','SUCCESS']
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE','0']

global shared_variables
shared_variables = {}

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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print Error_Detail
        return False


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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        print Error_Detail
        return False

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
    passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True',True,1,'1','Success','success','SUCCESS']
    failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE',False,0,'0']
    try:
        if sTestStepReturnStatus in passed_tag_list:
            temp_q.put("passed")
            return "passed"
        elif sTestStepReturnStatus in failed_tag_list:
            temp_q.put("failed")
            return "failed"
        else:
            ExecLog(sModuleInfo,"Step return type unknown: %s" %(sTestStepReturnStatus),3)
            temp_q.put("failed")
            return "failed"
    
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        ExecLog(sModuleInfo, "Step results was not recognized:%s" %( Error_Detail), 3)
        temp_q.put("failed")
        return "failed"

def ExecLog(sModuleInfo, sDetails, iLogLevel=1, local_run=False, sStatus=""):
    try:
        local_run = ConfigModule.get_config_value('RunDefinition','local_run')
        # ";" is not supported for logging.  So replacing them
        sDetails = sDetails.replace(";", ":")
        sDetails = sDetails.replace("=", "~")
        
        
        if local_run == False or local_run == 'False':
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
            
            #conn = DB.ConnectToDataBase()
            sDetails = encode_to_exclude_symbol(to_unicode(sDetails))
            if iLogLevel == 1:
                logger.info(sModuleInfo + ' - ' + sDetails + '' + sStatus)
                #DB.InsertNewRecordInToTable(conn, 'execution_log', logid=log_id, modulename=sModuleInfo, details=sDetails, status="Passed", loglevel=iLogLevel)
                status = 'Passed'
            elif iLogLevel == 2:
                logger.warning(sModuleInfo + ' - ' + sDetails + '' + sStatus)
                #DB.InsertNewRecordInToTable(conn, 'execution_log', logid=log_id, modulename=sModuleInfo, details=sDetails, status="Warning", loglevel=iLogLevel)
                status = 'Warning'
        
            elif iLogLevel == 3:
                logger.error(sModuleInfo + ' - ' + sDetails + '' + sStatus)
                #DB.InsertNewRecordInToTable(conn, 'execution_log', logid=log_id, modulename=sModuleInfo, details=sDetails, status="Error", loglevel=iLogLevel)
                status = 'Error'
        
            elif iLogLevel == 4:
                logger.info(sModuleInfo + ' - ' + sDetails + '' + sStatus)
                status = 'Error'
            else:
                print "unknown log level"
                status = ''
            logger.removeHandler(hdlr)
            #conn.close()
            r = RequestFormatter.Get('log_execution',{'logid': log_id, 'modulename': sModuleInfo, 'details': sDetails, 'status': status,'loglevel': iLogLevel})
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
                 if sys.platform == 'linux2':
                     #mobile device connected to linux machine

                     #android working copy
                     try:
                         output = os.system("adb devices")
                         if output is not None:
                             full_location=ImageFolder+os.sep+TimeStamp("utc")+"_"+ImageName+'_android.png'
                             #os.system("adb shell screencap -p | perl -pe 's/\x0D\x0A/\x0A/g' > %s"%full_location)
                             os.system("adb shell screencap -p /sdcard/screen.png")
                             os.system("adb pull /sdcard/screen.png %s"%full_location)
                     except Exception, e:
                         print e

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
                 # windows working copy
                 from PIL import ImageGrab
                 from PIL import Image
                 path = ImageFolder + os.sep + TimeStamp("utc") + "_" + ImageName + ".jpg"
                 img = ImageGrab.grab()
                 basewidth = 1200
                 wpercent = (basewidth/float(img.size[0]))
                 hsize = int((float(img.size[1])*float(wpercent)))
                 img = img.resize((basewidth,hsize), Image.ANTIALIAS)
                 img.save(path, 'JPEG')

                 # android working copy
                 try:
                     output = os.system("adb devices")
                     if output is not None:
                         full_location = ImageFolder + os.sep + TimeStamp("utc") + "_" + ImageName + '_android.png'
                         # os.system("adb shell screencap -p | perl -pe 's/\x0D\x0A/\x0A/g' > %s"%full_location)
                         os.system("adb shell screencap -p /sdcard/screen.png")
                         os.system("adb pull /sdcard/screen.png %s" % full_location)
                 except Exception, e:
                     print e

     except Exception, e:
         print "Exception : ", e

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
            print "Exception: ", e
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

        except Exception, e:
            #incase exception happens for whatever reason.. we will return the timestamp...
            print "Exception: ", e
            print "Unable to set create a Node key.  Please check class MachineInfo() in commonutil"
            return False


#shared_variables

def Set_Shared_Variables(key, value):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables
        if key == '' or key == None or value == '' or value == None: #if input is invalid
            return "failed"
        else:
            shared_variables[key] = value
            ExecLog(sModuleInfo, "Variable value of '%s' is set as: %s" % (key, value), 1)
            return "passed"
    except:
        Exception_Handler(sys.exc_info())


def Set_List_Shared_Variables(list_name, key, value):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables
        if key == '' or key == None or value == '' or value == None or list_name == '' or list_name == None: #if input is invalid
            return "failed"
        else:
            if list_name in shared_variables:
                shared_variables[list_name][key] = value
                ExecLog(sModuleInfo, "In List '%s' Variable value of '%s' is set as: %s" % (list_name,key, value), 1)
                return "passed"
            else:
                ExecLog(sModuleInfo,"List named %s does not exist on shared variables, so cant insert new field to list"%list_name,3)
                return "failed"
    except:
        Exception_Handler(sys.exc_info())


def Get_Shared_Variables(key):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables
        if key == '' or key == None: #if input is invalid
            return "failed"
        else:
            if key in shared_variables:
                value = shared_variables[key]
                ExecLog(sModuleInfo,"Variable value of '%s' is: %s"%(str(key),value),1)
                return value
            else:
                ExecLog(sModuleInfo,"No Such variable named '%s' found in shared variables"%key,3)
                return "failed"
    except:
        Exception_Handler(sys.exc_info())


def Get_List_from_Shared_Variables(list_name):
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables
        if list_name == '' or list_name == None: #if input is invalid
            return "failed"
        else:
            if list_name in shared_variables:
                list = shared_variables[list_name]
                ExecLog(sModuleInfo,"List: "+list_name+" is: "+str(list),1)
                return list
            else:
                ExecLog(sModuleInfo,"List named %s does not exist on shared variables"%list_name,3)
                return "failed"
    except:
        Exception_Handler(sys.exc_info())


def Test_Shared_Variables(key):
    ''' Test if a variable already exists and return true or false '''
    
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables
        if key == '' or key == None: #if input is invalid
            return "failed"
        else: # Valid input
            if key in shared_variables: # Test if key/variable exists
                ExecLog(sModuleInfo,"Variable %s exists" % key,1)
                return True
            else:
                ExecLog(sModuleInfo,"No Such variable named '%s' found in shared variables"%key,1)
                return False
    except:
        Exception_Handler(sys.exc_info())

def Show_All_Shared_Variables():
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        global shared_variables
        if len(shared_variables) > 0:
            ExecLog(sModuleInfo, "##Shared Variable Fields with Value##", 1)
            for each in shared_variables:
                ExecLog(sModuleInfo, "%s : %s" % (each, shared_variables[each]), 1)
    except:
        Exception_Handler(sys.exc_info())

def Handle_Step_Data_Variables(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        changed_step_data = []
        for dataset in step_data:
            changed_dataset = []
            for row in dataset:
                changed_row = []
                for each in row:
                    if each == True or each == False or each == '':
                        changed_row.append(each)
                    else:
                        if '|%' in each:
                            replaced_value = get_previous_response_variables_in_strings(each)
                            if replaced_value in failed_tag_list:
                                ExecLog(sModuleInfo,"Step Data Format Not Appropriate",3)
                                return 'failed'
                            else:
                                changed_row.append(replaced_value)
                        else:
                            changed_row.append(each)
                changed_dataset.append(changed_row)
            changed_step_data.append(changed_dataset)
        return changed_step_data
    except:
        Exception_Handler(sys.exc_info())

def get_previous_response_variables_in_strings(step_data_string_input):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    ExecLog(sModuleInfo, "Function: get previous response variables in strings", 1)
    try:
        changed = False
        input = step_data_string_input
        all_parse = input.split('%|')
        output = ''
        for each in all_parse:
            if '|%' in each:
                changed = True
                parts = each.split('|%')
                if str(parts[0]).startswith('random_string'):
                    full_string = str(parts[0])
                    random_string = ''
                    if '(' in full_string:
                        temp = full_string.split('(')
                        params = temp[1].split(')')[0]
                        if ',' in params:
                            list_of_params = params.split(',')
                            random_string = random_string_generator(list_of_params[0].strip(),int(list_of_params[1].strip()))
                        else:
                            if params.strip() == '':
                                random_string = random_string_generator()
                            else:
                                random_string = random_string_generator(params.strip())
                    else:
                        return "failed"

                    if random_string in failed_tag_list:
                        return "failed"

                    output+=random_string
                    ExecLog(sModuleInfo, 'Replacing variable "%s" with its value "%s"' % (parts[0], random_string), 1)
                else:
                    var_value = Get_Shared_Variables(parts[0])
                    if var_value == 'failed':
                        ExecLog(sModuleInfo,"No such variable named '%s' in shared variables list"%parts[0],3)
                        return "failed"
                    else:
                        output += str(var_value)
                        ExecLog(sModuleInfo,'Replacing variable "%s" with its value "%s"'%(parts[0],var_value),1)
                output += parts[1]
            else:
                output += each
        if changed == True:
            ExecLog(sModuleInfo,"Input string is changed by variable substitution",1)
            ExecLog(sModuleInfo, "Input string before change: %s"%input, 1)
            ExecLog(sModuleInfo, "Input string after change: %s"%output, 1)

        return output

    except Exception:
        return Exception_Handler(sys.exc_info())


def random_string_generator(pattern='nluc', size=10):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    ExecLog(sModuleInfo, "Function: random string generator", 1)
    try:
        pattern = pattern.lower().strip()
        punctuation = '`~!@#$%^&.'
        chars = ''
        for index in range(0,len(pattern)):
            if pattern[index] == 'n':
                chars += string.digits
            if pattern[index] == 'l':
                chars += string.ascii_lowercase
            if pattern[index] == 'u':
                chars += string.uppercase
            if pattern[index] == 'c':
                chars += punctuation

        if chars == '':
            return 'failed'
        else:
            return ''.join(random.choice(chars) for _ in range(size))
    except Exception:
        return Exception_Handler(sys.exc_info())


def Clean_Up_Shared_Variables():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    ExecLog(sModuleInfo, "Function: clean up shared variables", 1)
    try:
        global shared_variables
        shared_variables = {}
        return "passed"
    except Exception:
        return Exception_Handler(sys.exc_info())

def run_cmd(command, return_status=False, is_shell=True, stdout_val=subprocess.PIPE, local_run=False):

    '''Begin Constants'''
    Passed = "Passed"
    Failed = "Failed"
    Running = 'running'
    '''End Constants'''

    # Run 'command' via command line in a bash shell, and store outputs to stdout_val
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    subprocess_dict = {}
    try:
        #global subprocess_dict
        ExecLog(sModuleInfo, "Trying to run command: %s" % command, 1, local_run)

        # open a subprocess with command, and assign a session id to the shell process
        # this is will make the shell process the group leader for all the child processes spawning from it
        status = subprocess.Popen(command, shell=is_shell, stdout=stdout_val, preexec_fn=os.setsid)
        subprocess_dict[status] = Running

        if return_status:
            return status
        else:
            return Passed

    except Exception, e:
        return Exception_Handler(sys.exc_info())


