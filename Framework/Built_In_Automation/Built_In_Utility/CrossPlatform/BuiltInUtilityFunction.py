# -*- coding: cp1252 -*-
'''
Created on May 15, 2016

@author: Built_In_Automation Solutionz Inc.
'''

import sys

sys.path.append("..")
import time
import inspect
import zipfile
import string
import random
from Framework.Utilities import CommonUtil
from sys import platform as _platform

passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True','1','Success','success','SUCCESS',True]
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE','0',False]


import os,subprocess,shutil



import zipfile

add_sanitization = True

#funtion to get the path of home folder in linux
def get_home_folder():
    """

    :return: give the location of home folder
    """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get Home Folder", 1)
    return os.path.expanduser("~")

#function to create a folder
def CreateFolder(folderPath, forced=True):
    """

    :param folderPath: folderpath to create
    :param forced: if true remove the folder first, if false won't remove the folder if there exists one with same name
    :return: False if failed and exception or True if successful
    """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Create Folder", 1)
    try:
        if os.path.isdir(folderPath):
            if forced == False:
                print "folder already exists"
                CommonUtil.ExecLog(sModuleInfo, "Folder already exists", 1)
                return True
            DeleteFolder(folderPath)
        os.makedirs(folderPath)
        return True
    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#function to create a file
def CreateFile(sFilePath):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Create File", 1)
    try:
        if os.path.isfile(sFilePath):
            CommonUtil.ExecLog(sModuleInfo, "File already exists", 1)
            print "File already exists"
            return False
        else:
            print "Creating new file"
            newfile = open(sFilePath, 'w')
            newfile.close()
            CommonUtil.ExecLog(sModuleInfo, "Returning result of create file function", 1)
            return newfile
    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#function to rename file a to b
def RenameFile(a,b):
    """

        :param a: location of source file to be renamed
        :param b: location of destination file
        :return: False if Exception otherwise return result  
        """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Rename File", 1)
    try:
        result = shutil.move(a, b)
        CommonUtil.ExecLog(sModuleInfo, "Returning result of rename file function", 1)
        return result
    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#function to rename folder a to b
def RenameFolder(a,b):
    """

        :param a: location of source folder to be renamed
        :param b: full location of destination folder
        :return: False if Exception otherwise return result  
        """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Rename Folder", 1)
    try:
        result = shutil.move(a, b)
        CommonUtil.ExecLog(sModuleInfo, "Returning result of rename folder function", 1)
        return result
    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#function to unzip in linux
def UnZip(a,b):
    """

        :param a: location of source file to be unzipped
        :param b: location of destination 
        :return: False if Exception or file doesn't exist otherwise return result  
        """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Unzip", 1)
    try:
        if os.path.isfile(a):
            zip_ref = zipfile.ZipFile(a, 'r')
            zip_ref.extractall(b)
            result = zip_ref.close()
            CommonUtil.ExecLog(sModuleInfo, "Returning result of unzip  function", 1)
            return result
        else:
            CommonUtil.ExecLog(sModuleInfo,
                               "can't unzip file as it doesn't exist",
                               3)
            return False
    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#function to compare two files
def CompareFile(path1, path2):
    """

        :param path1: location of file to be compared
        :param path2: location of file to be compared
        :return: False if Exception or file doesn't exist otherwise return result  
        """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare File", 1)
    try:
        import filecmp
        result = filecmp.cmp(path1, path2)
        CommonUtil.ExecLog(sModuleInfo, "Returning result of compare file function", 1)
        return result
    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#function to zip a file for linux
def ZipFile(path1, path2):
    """

        :param path1: location of source file to be zipped
        :param path2: location of destination 
        :return: False if Exception or file doesn't exist otherwise return result  
        """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Zip File", 1)
    try:
        import zipfile
        if os.path.isfile(path1):
            list1=path1.split('/')
            list2=path2.split('/')
            value=path1[:len(path1)-len(list1[len(list1)-1])]
            os.chdir(value)
            result=zipfile.ZipFile(list2[len(list2)-1], mode='w').write(list1[len(list1)-1])
            CommonUtil.ExecLog(sModuleInfo, "Returning result of zip file function", 1)
            return result
        else:
            CommonUtil.ExecLog(sModuleInfo,
                               "can't zip file as file doesn't exist",
                               3)
            return False
    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#function to zip file for windows
def ZipFile_for_windows(path1, path2):
    """

        :param path1: location of source file to be zipped
        :param path2: location of destination 
        :return: False if Exception or file doesn't exist otherwise return result  
        """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Zip File for Windows", 1)
    try:
        import zipfile
        if os.path.isfile(path1):
            list1=path1.split('//')
            list2=path2.split('//')
            value=path1[:len(path1)-len(list1[len(list1)-1])]
            os.chdir(value)
            result=zipfile.ZipFile(list2[len(list2)-1], mode='w').write(list1[len(list1)-1])
            CommonUtil.ExecLog(sModuleInfo, "Returning result of zip file for windows function", 1)
            return result
        else:
            CommonUtil.ExecLog(sModuleInfo,
                               "can't zip file for windows as file doesn't exist",
                               3)
            return False
    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#funtion zip a folder
def ZipFolder(dir, zip_file):
    """
    Zips a given folder, its sub folders and files. Ignores any empty folders
    dir is the path of the folder to be zipped
    zip_file is the path of the zip file to be created
    """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Zip Folder", 1)
    try:
        import zipfile

        if os.path.exists(dir):
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

            result=zip.close()
            CommonUtil.ExecLog(sModuleInfo, "Returning result of zip folder function", 1)
            return result

        else:
            return False

    except Exception, e:
        print "Exception :", e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#function to delete a file
def DeleteFile(sFilePath):
    """

        :param sFilePath: full location of the file to be deleted
        :return: False if failed/Exection otherwise return the result
        """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Delete File", 1)
    try:
        if os.path.isfile(sFilePath):
            result=os.remove(sFilePath)
            CommonUtil.ExecLog(sModuleInfo, "Returning result of delete file function", 1)
            return result
        else:
            CommonUtil.ExecLog(sModuleInfo,
                               "can't delete file as file doesn't exist",
                               3)
            return False
    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#function to delete a folder
def DeleteFolder(sFilePath):
    """

            :param sFilePath: full location of the folder to be deleted
            :return: False if failed/Exection otherwise return the result
            """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Delete Folder", 1)
    try:
        print os.path.isdir(sFilePath)
        if os.path.isdir(sFilePath):
            shutil.rmtree(sFilePath)
        else:
            CommonUtil.ExecLog(sModuleInfo,
                               "can't delete folder as folder doesn't exist",
                               3)
            return False

    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#function to check a file exists or not
def find(sFilePath):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Find file", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Returning result of find file function", 1)
        return os.path.isfile(sFilePath)

    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#function to empty trash for linux
def empty_trash(sFilePath):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: empty trash", 1)
    try:

      #  os.chdir('/home/tazin/.local/share/Trash')
        os.chdir(sFilePath)
        if len(sys.argv) >= 2:
            if sys.argv[1] == '-t' or sys.argv[1] == '-T':
                os.system("tree ./")
            elif sys.argv[1] == '-l' or sys.argv[1] == '-L':
                os.system("ls -al")
        result = os.system("rm -rf *")



    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#function to copy a folder
def copy_folder(src, dest):

    """

    :param src: source of the folder
    :param dest: destination to be copied.
    :return:  False if Exception or otherwise return result
    """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Copy Folder", 1)
    try:

        result = shutil.copytree(src, dest)
        CommonUtil.ExecLog(sModuleInfo, "Returning result of copy folder function", 1)
        return result
    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#function to copy a file
def copy_file(src, dest):
    """

    :param src: full location of source file
    :param dest: full location of destination file
    :return: False if Exception or otherwise return result  
    """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Copy File", 1)
    try:
        result = shutil.copyfile(src, dest)
        CommonUtil.ExecLog(sModuleInfo, "Returning result of copy file function", 1)
        return result
    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

#function to empty recycle bin for windows
def empty_recycle_bin():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Empty Recycle Bin", 1)
    try:
        import winshell
        result=winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        print result
        CommonUtil.ExecLog(sModuleInfo, "Returning result of empty recycle bin function", 1)
        return result
    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

def run_win_cmd(cmd):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Run Win Cmd", 1)
    try:
        import subprocess
        result = []
        process = subprocess.Popen(cmd,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        for line in process.stdout:
            result.append(line)
        errcode = process.returncode
        for line in result:
            print(line)
        if errcode is not None:
            CommonUtil.ExecLog(sModuleInfo,
                               'cmd %s failed, see above for details'%cmd,
                               3)
            raise Exception('cmd %s failed, see above for details', cmd)
    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False

def run_cmd(command, return_status=False, is_shell=True, stdout_val=subprocess.PIPE, local_run=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Run Cmd", 1)
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
        result = []
        CommonUtil.ExecLog(sModuleInfo, "Trying to run command: %s" % command, 1, local_run)

        # open a subprocess with command, and assign a session id to the shell process
        # this is will make the shell process the group leader for all the child processes spawning from it
        status = subprocess.Popen(command, shell=is_shell, stdout=stdout_val, preexec_fn=os.setsid)
        subprocess_dict[status] = Running
        for line in status.stdout:
            result.append(line)
        errcode = status.returncode
        for line in result:
            print(line)
        if return_status:
            return status
        else:
            return Passed

    except Exception, e:
        print "Error: %s" % e
        CommonUtil.ExecLog(sModuleInfo,
                           "Error: %s" % e,
                           3)
        return False


#function to generate random string
def random_string_generator(pattern='nluc', size=10):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: random string generator", 1)
    try:
        pattern = pattern.lower().strip()
        punctuation = '`~!@#$%^&.'
        chars = ''
        for index in range(0,len(pattern)):
            if pattern[index] == 'n':       #Numbers
                chars += string.digits
            if pattern[index] == 'l':       #Lowercase
                chars += string.ascii_lowercase
            if pattern[index] == 'u':       #Uppercase
                chars += string.uppercase
            if pattern[index] == 'c':       #Characters
                chars += punctuation

        if chars == '':
            return 'failed'
        else:
            return ''.join(random.choice(chars) for _ in range(size))
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

# not done properly...need more works
def change_path_for_windows(src):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Change path for Windows", 1)
    print src
    string_list=str(src).split("\\")
    print string_list
    print src
    return src

'============================= Sanitization Begins =============================='
def sanitizing_function(input_string):

    input_string = input_string.replace('_', ' ')   #replace "_" with " "

    input_string = ' '.join(input_string.split())   #Convert multiple space to single space

    input_string = input_string.lower()  #Convert to lower case
    input_string = input_string[:256]   #put a limit on string length - say 256 bytes

    return input_string

def sanitize(step_data, sanitization):
    if sanitization == True:
        for each in step_data:
            for row in each:
                i=0
                for element in row:
                    if(isinstance(element, str)):
                        if "%|" not in element or "|%" not in element:     #will not sanitize a string like %|...|%
                            row[i] = sanitizing_function(element)

                    i+=1
    return step_data
'===================== ===x=== Sanitization Ends ===x=== ======================'



'============================= Sequential Action Section Begins=============================='

#Method to copy file/folder
def Copy_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Copy File or Folder", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            print "linux"
            from_path = get_home_folder() + str(step_data[0][0][0]).strip() #location of the file/folder to be copied
            to_path = get_home_folder() + str(step_data[0][0][2]).strip() #location where to copy the file/folder
            file_or_folder = str(step_data[0][1][2]).strip()  #get if it is file/folder to copy
            if file_or_folder.lower() == 'file':
                #copy file "from_path" to "to_path"
                result = copy_file(from_path,to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,"Could not copy file '%s' to the destination '%s'"%(from_path,to_path),3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,"File '%s' copied to the destination '%s' successfully" % (from_path, to_path), 1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
                #copy folder "from_path" to "to_path"
                result = copy_folder(from_path,to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,"Could not copy folder '%s' to the destination '%s'"%(from_path,to_path),3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,"Folder '%s' copied to the destination '%s' successfully" % (from_path, to_path), 1)
                    return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
                return 'failed'
        elif _platform == "win32":
                    # linux
            print "windows"
            from_path = change_path_for_windows(str(step_data[0][0][0]).strip()) #location of the file/folder to be copied
            to_path = change_path_for_windows(str(step_data[0][0][2]).strip()) #location where to copy the file/folder
            file_or_folder = str(step_data[0][1][2]).strip()  #get if it is file/folder to copy
            if file_or_folder.lower() == 'file':
                #copy file "from_path" to "to_path"
                result = copy_file(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Could not copy file '%s' to the destination '%s'" % (
                            from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "File '%s' copied to the destination '%s' successfully" % (
                            from_path, to_path), 1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
                #copy folder "from_path" to "to_path"
                result = copy_folder(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Could not copy folder '%s' to the destination '%s'" % (
                            from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,
                                               "Folder '%s' copied to the destination '%s' successfully" % (
                                               from_path, to_path), 1)
                    return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo,
                                           "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                                           3)
                return 'failed'

        #return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Method to delete file/folder
def Delete_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Delete File or Folder", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            print "linux"
            path = get_home_folder() + str(step_data[0][0][0]).strip() # path of the file/folder to be deleted
            file_or_folder = str(step_data[0][1][2]).strip()  #get if it is file/folder to delete
            if file_or_folder.lower() == 'file':
                # delete file "path"
                result = DeleteFile(path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,"Could not delete file '%s'"%(path),3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,"File '%s' deleted successfully" % (path), 1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
                #delte folder "path"
                result = DeleteFolder(path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Could not delete folder '%s'" % (path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Folder '%s' deleted successfully" % (path), 1)
                    return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
                return 'failed'
        elif _platform == "win32":
                    # linux
            print "windows"
            path = change_path_for_windows(str(step_data[0][0][0]).strip()) #path of the file/folder to be deleted
            file_or_folder = str(step_data[0][1][2]).strip()  #get if it is file/folder to delete
            if file_or_folder.lower() == 'file':
                #delete file "path"
                result = DeleteFile(path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,"Could not delete file '%s'"%(path),3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,"File '%s' deleted successfully" % (path), 1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
                #delete folder "path"
                result = DeleteFolder(path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Could not delete folder '%s'" % (path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Folder '%s' deleted successfully" % (path), 1)
                    return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
                return 'failed'

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to find file
def Find_File(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Find File", 1)
    try:
        path = get_home_folder() + str(step_data[0][0][0]).strip()
        file_or_folder = str(step_data[0][1][2]).strip()
        if file_or_folder.lower() == 'file':
            # find file "path"
            result = find(path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Could not find file '%s'"%(path),3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"File '%s' found" % (path), 1)
                return "passed"

        else:
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return 'failed'

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to empty trash/recycle bin
def Empty_Trash(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Empty Trash Can", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            print "linux"
            path = get_home_folder() + '/.local/share/Trash' #location of trash for linux
            print path

            result = empty_trash(path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Could not empty trash '%s'"%(path),3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"trash is cleared '%s'" % (path), 1)
                return "passed"
        elif _platform == "win32":
                    # linux
            print "windows"
            result=empty_recycle_bin() #location of the recycle bin
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Could not empty recycle bin ",3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"recycle bin is cleared " , 1)
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to Get User Name
def Get_User_Name(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get User Name", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
                # linux
            print "linux"
            path = get_home_folder()   #get the path of the home directory
            list_elemnet=path.split("/")   #list the parts of path by spliting it by "/"
            name=list_elemnet[len(list_elemnet)-1]  #name of the user
            if name in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find user name '%s'" % (name), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "user name is '%s'" % (name), 1)
                return "passed"
        elif _platform == "win32":
                # linux
            print "windows"
            CommonUtil.ExecLog(sModuleInfo, "Could not find user name as it is windows" , 3)
            return "failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to Run Sudo Command
def Run_Sudo_Command(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Run Sudo Command", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
                # linux
            print "linux"
            command = str(step_data[0][0][0]).strip()
            result=run_cmd(command)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not run sudo command '%s'" % (command), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "sudo command is run properly '%s'" % (command), 1)
                return "passed"
        elif _platform == "win32":
                # linux
            print "windows"
            CommonUtil.ExecLog(sModuleInfo, "Could not run sudo command as it is windows" , 3)
            return "failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to Run Command
def Run_Command(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Run command for windows", 1)
    try:
        if _platform == "win32":
                # linux
            print "windows"
            command = str(step_data[0][0][0]).strip()
            result=run_win_cmd(command)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not run sudo command '%s'" % (command), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "sudo command is run properly '%s'" % (command), 1)
                return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to Get Home Directory
def Get_Home_Directory(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get Home Directory", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
                # linux
            print "linux"
            path = get_home_folder()
            print path
            if path in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find home directory '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "home directory is '%s'" % (path), 1)
                return "passed"
        elif _platform == "win32":
                # linux
            print "windows"
            CommonUtil.ExecLog(sModuleInfo, "Could not find home directory as it is windows" , 3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to Get Current Desktop
def Get_Current_Desktop(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get Current Desktop", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
                # linux
            print "linux"
            path = get_home_folder()+"/Desktop" #concate home folder path with "/Desktop"
            print path
            if path in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find desktop '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "desktop path is '%s'" % (path), 1)
                return "passed"
        elif _platform == "win32":
                # linux
            print "windows"
            path = os.path.join(os.environ["HOMEPATH"], "Desktop")
            print path
            if path in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find desktop '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "desktop path is '%s'" % (path), 1)
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to Get Current Documents
def Get_Current_Documents(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get Current Documents", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
                # linux
            print "linux"
            path = get_home_folder() + "/Documents" #concate home folder path with "/Documents"
            print path
            if path in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find Documents '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Documents path is '%s'" % (path), 1)
                return "passed"
        elif _platform == "win32":
                # linux
            print "windows"
            path = os.path.join(os.environ["HOMEPATH"], "Documents")
            print path
            if path in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find Documents '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Documents path is '%s'" % (path), 1)
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to create file
def Create_File(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Create File", 1)
    try:
        path = get_home_folder() + str(step_data[0][0][2]).strip()
        file_or_folder = str(step_data[0][1][2]).strip()
        if file_or_folder.lower() == 'file':
            # create file "path"
            result = CreateFile(path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Could not create file '%s'"%(path),3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"File '%s' created" % (path), 1)
                return "passed"

        else:
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return 'failed'

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to compare file
def Compare_File(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare File", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            print "linux"
            from_path = get_home_folder() + str(step_data[0][0][0]).strip() #location of file path to be compared
            to_path = get_home_folder() + str(step_data[0][0][2]).strip() #location of file path to be compared
            file_or_folder = str(step_data[0][1][2]).strip()
            if file_or_folder.lower() == 'file':
                # compare file "from_path" and "to_path"
                result = CompareFile(from_path,to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,"Could not create file '%s'"%(to_path),3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,"File '%s' created" % (to_path), 1)
                    return "passed"

            else:
                CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
                return 'failed'
        elif _platform == "win32":
            # linux
            print "windows"
            print step_data[0][0][0]
            print str(step_data[0][0][0])
            from_path = change_path_for_windows(str(step_data[0][0][0]).strip()) #location of file path to be compared
            print  from_path
            to_path = change_path_for_windows(str(step_data[0][0][2]).strip()) #location of file path to be compared
            print to_path
            file_or_folder = str(step_data[0][1][2]).strip()
            if file_or_folder.lower() == 'file':
                #compare file "from_path" and "to_path"
                result = CompareFile(from_path,to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,"Could not create file '%s'"%(to_path),3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,"equal %s and %s" % (to_path,from_path), 1)
                    return "passed"

            else:
                CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
                return 'failed'

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to rename file/folder
def Rename_File_or_Folder(step_data):
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        CommonUtil.ExecLog(sModuleInfo, "Function: Rename File or Folder", 1)
        try:
            if _platform == "linux" or _platform == "linux2":
                # linux
                print "linux"
                from_path = get_home_folder() + str(step_data[0][0][0]).strip() #location of the file/folder to be renamed
                to_path = get_home_folder() + str(step_data[0][0][2]).strip() #location where to rename the file/folder
                file_or_folder = str(step_data[0][1][2]).strip() #get if it is file/folder to rename
                if file_or_folder.lower() == 'file':
                    # rename file "from_path" to "to_path"
                    result = RenameFile(from_path, to_path)
                    if result in failed_tag_list:
                        CommonUtil.ExecLog(sModuleInfo,
                                       "Could not rename file '%s' to '%s'" % (from_path, to_path), 3)
                        return "failed"
                    else:
                        CommonUtil.ExecLog(sModuleInfo,
                                       "File '%s' renamed to '%s' successfully" % (from_path, to_path),
                                       1)
                        return "passed"
                elif file_or_folder.lower() == 'folder':
                    #rename folder "from_path" to "to_path"
                    result = RenameFolder(from_path, to_path)
                    if result in failed_tag_list:
                        CommonUtil.ExecLog(sModuleInfo,
                                       "Could not rename folder '%s' to '%s'" % (from_path, to_path), 3)
                        return "failed"
                    else:
                        CommonUtil.ExecLog(sModuleInfo,
                                       "Folder '%s' renamed to '%s' successfully" % (from_path, to_path),
                                       1)
                        return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,
                                   "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                                   3)
                    return 'failed'
            elif _platform == "win32":
                # linux
                print "windows"
                from_path = str(step_data[0][0][0]).strip() #location of the file/folder to be renamed
                to_path = str(step_data[0][0][2]).strip() #location where to rename the file/folder
                file_or_folder = str(step_data[0][1][2]).strip() #get if it is file/folder to rename
                if file_or_folder.lower() == 'file':
                    #rename file "from_path" to "to_path"
                    result = RenameFile(from_path, to_path)
                    if result in failed_tag_list:
                        CommonUtil.ExecLog(sModuleInfo,
                                       "Could not rename file '%s' to '%s'" % (from_path, to_path), 3)
                        return "failed"
                    else:
                        CommonUtil.ExecLog(sModuleInfo,
                                       "File '%s' renamed to '%s' successfully" % (from_path, to_path),
                                       1)
                        return "passed"
                elif file_or_folder.lower() == 'folder':
                    #rename folder 'from_path" to "to_path"
                    result = RenameFolder(from_path, to_path)
                    if result in failed_tag_list:
                        CommonUtil.ExecLog(sModuleInfo,
                                       "Could not rename folder '%s' to '%s'" % (from_path, to_path), 3)
                        return "failed"
                    else:
                        CommonUtil.ExecLog(sModuleInfo,
                                       "Folder '%s' renamed to '%s' successfully" % (from_path, to_path),
                                       1)
                        return "passed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,
                                   "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                                   3)
                    return 'failed'

        except Exception:
            return CommonUtil.Exception_Handler(sys.exc_info())

#Method to zip file/folder
def Zip_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Zip File or Folder", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            print "linux"
            from_path = get_home_folder() + str(step_data[0][0][0]).strip() #location of the file/folder to be zipped
            to_path = get_home_folder() + str(step_data[0][0][2]).strip() #location where to zip the file/folder
            file_or_folder = str(step_data[0][1][2]).strip() #get if it is file/folder to zip
            if file_or_folder.lower() == 'file':
                result = ZipFile(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,
                                   "Can't not zip file '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,
                                   "File '%s' renamed to '%s' successfully" % (from_path, to_path),
                                   1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
                result = ZipFolder(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,
                                   "Can't not zip folder '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,
                                   "Folder '%s' zipped to '%s' successfully" % (from_path, to_path),
                                   1)
                    return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
                return 'failed'
        elif _platform == "win32":
            # linux
            print "windows"
            from_path = str(step_data[0][0][0]).strip() #location of the file/folder to be zipped
            to_path = str(step_data[0][0][2]).strip() #location where to zip the file/folder
            file_or_folder = str(step_data[0][1][2]).strip() #get if it is file/folder to zip
            if file_or_folder.lower() == 'file':
                result = ZipFile_for_windows(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,
                                   "Can't not zip file '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,
                                   "File '%s' zipped to '%s' successfully" % (from_path, to_path),
                                   1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
                result = ZipFolder(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,
                                   "Could not zip folder '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,
                                   "Folder '%s' zipped to '%s' successfully" % (from_path, to_path),
                                   1)
                    return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
                return 'failed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to unzip
def Unzip_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Unzip File or Folder", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            print "linux"
            from_path = get_home_folder() + str(step_data[0][0][0]).strip() #location of the file/folder to be unzipped
            to_path = get_home_folder() + str(step_data[0][0][2]).strip() #location where to unzip the file/folder

            result = UnZip(from_path, to_path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,
                                   "Can't not unzip '%s' to '%s'" % (from_path, to_path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,
                                   "'%s' is unzipped to '%s' successfully" % (from_path, to_path),
                                   1)
                return "passed"



        elif _platform == "win32":
                    # linux
            print "windows"
            from_path = str(step_data[0][0][0]).strip() #location of the file/folder to be unzipped
            to_path = str(step_data[0][0][2]).strip() #location where to unzip the file/folder

            result = UnZip(from_path, to_path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,
                                   "Can't not unzip '%s' to '%s'" % (from_path, to_path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,
                                   "'%s' is unzipped to '%s' successfully" % (from_path, to_path),
                                   1)
                return "passed"




    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to move file/folder
def Move_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Move File or Folder", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            print "linux"
            from_path = get_home_folder() + str(step_data[0][0][0]).strip() #location of the file/folder to be moved
            to_path = get_home_folder() + str(step_data[0][0][2]).strip() #location where to move the file/folder
            file_or_folder = str(step_data[0][1][2]).strip() #get if it is file/folder to move
            if file_or_folder.lower() == 'file':
                # move file "from_path to "to_path"
                result = RenameFile(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,
                                           "Could not move file '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,
                                           "File '%s' moved to '%s' successfully" % (from_path, to_path),
                                           1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
                # move folder "from_path" to "to_path"
                result = RenameFolder(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,
                                           "Could not move folder '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,
                                           "Folder '%s' moved to '%s' successfully" % (from_path, to_path),
                                           1)
                    return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo,
                                       "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                                       3)
                return 'failed'
        elif _platform == "win32":
            # linux
            print "windows"
            from_path = str(step_data[0][0][0]).strip() #location of the file/folder to be moved
            to_path = str(step_data[0][0][2]).strip() #location where to move the file/folder
            file_or_folder = str(step_data[0][1][2]).strip() #get if it is file/folder to move
            if file_or_folder.lower() == 'file':
                # move file "from_path" to "to_path"
                result = RenameFile(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,
                                           "Could not move file '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,
                                           "File '%s' moved to '%s' successfully" % (from_path, to_path),
                                           1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
                #move folder "from_path" to "to_path"
                result = RenameFolder(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,
                                           "Could not move folder '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,
                                           "Folder '%s' moved to '%s' successfully" % (from_path, to_path),
                                           1)
                    return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo,
                                       "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                                       3)
                return 'failed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to sleep for a particular duration
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
            CommonUtil.ExecLog(sModuleInfo,"Sleeping for %s seconds"%seconds,1)
            time.sleep(seconds)
            return "passed"
        #return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

# Handles actions for the sequential logic, based on the input from the mentioned function
def Action_Handler(action_step_data, action_name):
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        CommonUtil.ExecLog(sModuleInfo, "Function: Action_Handler", 1)
        try:
            if action_name == "skip":
                # skip the sanitization
                return "passed"
            elif action_name == "copy":
                result = Copy_File_or_Folder(action_step_data)  # copy file/folder
                if result == "failed":
                    return "failed"
            elif action_name == "delete":
                result = Delete_File_or_Folder(action_step_data)  # delete file/folder
                if result == "failed":
                    return "failed"
            elif action_name == "create":
                result = Create_File(action_step_data)  # create file
                if result == "failed":
                    return "failed"
            elif action_name == "find":
                result = Find_File(action_step_data)  # find file
                if result == "failed":
                    return "failed"
            elif action_name == "rename":
                result = Rename_File_or_Folder(action_step_data)  # rename file/folder
                if result == "failed":
                    return "failed"
            elif action_name == "move":
                result = Move_File_or_Folder(action_step_data)  # move file/folder
                if result == "failed":
                    return "failed"
            elif action_name == "zip":
                result = Zip_File_or_Folder(action_step_data)  # zip file/folder
                if result == "failed":
                    return "failed"
            elif action_name == "unzip":
                result = Unzip_File_or_Folder(action_step_data)  # unzip
                if result == "failed":
                    return "failed"
            elif action_name == "compare":
                result = Compare_File(action_step_data)  # compare file
                if result == "failed":
                    return "failed"
            elif action_name == "empty":
                result = Empty_Trash(action_step_data)  # empty trash/recycle bin
                if result == "failed":
                    return "failed"
            elif action_name == "user name":
                result = Get_User_Name(action_step_data)  # get user name
                if result == "failed":
                    return "failed"
            elif action_name == "current documents":
                result = Get_Current_Documents(action_step_data)  # get current documents
                if result == "failed":
                    return "failed"
            elif action_name == "current desktop":
                result = Get_Current_Desktop(action_step_data)  # get current desktop
                if result == "failed":
                    return "failed"
            elif action_name == "home directory":
                result = Get_Home_Directory(action_step_data)  # get home directory
                if result == "failed":
                    return "failed"
            elif action_name == "run sudo":
                result = Run_Sudo_Command(action_step_data)  # run sudo command
                if result == "failed":
                    return "failed"
            elif action_name == "run command":
                result = Run_Command(action_step_data)  # run admin command
                if result == "failed":
                    return "failed"
            elif action_name == "sleep":
                result = Sleep(action_step_data)
                if result == "failed":
                    return "failed"

            else:
                CommonUtil.ExecLog(sModuleInfo,
                                   "The action you entered is incorrect. Please provide accurate information on the data set(s).",
                                   3)
                return "failed"

        except Exception:
            return CommonUtil.Exception_Handler(sys.exc_info())

#return only the path step data
def Get_Path_Step_Data(step_data):
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        CommonUtil.ExecLog(sModuleInfo, "Function: Get_Element_Step_Data", 1)
        try:
            element_step_data = []
            for each in step_data[0]:
                # if each[1]=="":
                #             if (each[1]!="action" or each[1]!="logic"):
                #                 element_step_data.append(each)
                #             else:
                #                 CommonUtil.ExecLog(sModuleInfo, "End of element step data", 2)
                #                 break
                if (each[1] == "action" or each[1] == "conditional action"):
                    CommonUtil.ExecLog(sModuleInfo, "Not a part of element step data", 2)
                    continue
                else:
                    element_step_data.append(each)

            return element_step_data

        except Exception:
            return CommonUtil.Exception_Handler(sys.exc_info())

#return validated path data with path1 and path2
def Validate_Path_Step_Data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Validate_Step_Data", 1)
    try:
        path1=get_home_folder()+str(step_data[0][0]).strip()
        path2=get_home_folder()+str(step_data[0][2]).strip()
        validated_data = (path1, path2
        )
        return validated_data
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find the new page element requested.  Error: %s" % (Error_Detail), 3)
        return "failed"

#Performs a series of action or conditional logical action decisions based on user input
def Sequential_Actions(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Sequential_Actions", 1)
    try:
        '''global add_sanitization
        if step_data[0][0][0]=="skip" and step_data[0][0][1]=="action":
            add_sanitization = False
        print step_data
        sanitize(step_data,add_sanitization)
        print step_data'''
        for each in step_data:
            logic_row=[]
            for row in each:
                #finding what to do for each dataset
                #if len(row)==5 and row[1] != "":     ##modifying the filter for changes to be made in the sub-field of the step data. May remove this part of the if statement
                if ((row[1] == "path")):     ##modifying the filter for changes to be made in the sub-field of the step data. May remove this part of the if statement
                    continue

                elif row[1]=="action":
                    #finding the action to be performed
                    CommonUtil.ExecLog(sModuleInfo, "Checking the action to be performed in the action row", 1)
                    #handle the action
                    result = Action_Handler([each],row[0])
                    if result == [] or result == "failed":
                        return "failed"
                elif row[1]=="conditional action":
                    CommonUtil.ExecLog(sModuleInfo, "Checking the logical conditional action to be performed in the conditional action row", 1)
                    logic_decision=""
                    logic_row.append(row)
                    if len(logic_row)==2:
                        #element_step_data = each[0:len(step_data[0])-2:1]
                        path_step_data = Get_Path_Step_Data([each])
                        returned_step_data_list = Validate_Path_Step_Data(path_step_data)
                        if ((returned_step_data_list == []) or (returned_step_data_list == "failed")):
                            return "failed"
                        else:
                            try:
                                Element = find(returned_step_data_list[0])
                                if Element == False:
                                    logic_decision = "false"
                                else:
                                    logic_decision = "true"
                            except Exception, errMsg:
                                errMsg = "Could not find element in the by the criteria..."
                                return CommonUtil.Exception_Handler(sys.exc_info(),None,errMsg)
                    else:
                        #continue until length  of logic_row is 2
                        continue

                    #handle the conditional action
                    for conditional_steps in logic_row:
                        if logic_decision in conditional_steps:
                            print conditional_steps[2]
                            list_of_steps = conditional_steps[2].split(",")
                            for each_item in list_of_steps:
                                data_set_index = int(each_item) - 1
                                cond_result = Sequential_Actions([step_data[data_set_index]])
                                if cond_result == "failed":
                                    return "failed"
                            return "passed"

                else:
                    CommonUtil.ExecLog(sModuleInfo, "The sub-field information is incorrect. Please provide accurate information on the data set(s).", 3)
                    return "failed"
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

'===================== ===x=== Sequential Action Section Ends ===x=== ======================'



