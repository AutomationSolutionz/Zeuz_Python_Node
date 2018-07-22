# -*- coding: cp1252 -*-
'''
    Created on May 15, 2016

    @author: Built_In_Automation Solutionz Inc.
    Name: Built In Functions - Utility
    Description: OS and file utitlies
'''

#########################
#                       #
#        Modules        #
#                       #
#########################


import sys, datetime, time, inspect, zipfile, string, filecmp, random, requests, math, re, os, subprocess, shutil, ast,hashlib
sys.path.append("..")
from sys import platform as _platform
from Framework.Utilities import ConfigModule
from Framework.Utilities import CommonUtil
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list, skipped_tag_list
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources

#########################
#                       #
#    Helper Functions   #
#                       #
#########################

# funtion to get the path of home folder in linux
def get_home_folder():
    """
    :return: give the path of home folder
    """

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
            path = os.getenv('HOME') 
        elif _platform == "win32":
            path = os.getenv('USERPROFILE')
            
        if path in failed_tag_list:
            return 'failed'
        return path
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# function to create a folder
def CreateFolder(folderPath, forced=True):
    """
        :param folderPath: folder path to be created
        :param forced: if true remove the folder first, if false won't remove the folder if there exists one with same name
        :return: Exception if Exception occurs or True if successful
    """
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Creating Folder %s" % folderPath, 1)
        if os.path.isdir(folderPath):
            if forced == False:
                # print "folder already exists"
                CommonUtil.ExecLog(sModuleInfo, "Folder already exists. Not doing", 1)
                return "passed"
            DeleteFolder(folderPath)
        
        os.makedirs(folderPath) # Create the directory
        
        # after performing os.makedirs() we have to check that if the folder with new name exists in correct location.
        # if the folder exists in correct position then return passed
        # if the folder doesn't exist in correct position then return failed
        if os.path.isdir(folderPath):
            CommonUtil.ExecLog(sModuleInfo, "Folder created successfully", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Could not create folder", 3)
            return "failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error creating folder")


# function to create a file
def CreateFile(sFilePath, data = '', overwrite = False):
    """
        :param sFilePath: file path to be created
        :param data: Write data to the file
        :param overwrite: if true overwrite the current file
        :return: Exception if Exception occurs or True if successful or False if file already exists
    """
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Creating file %s" % sFilePath, 1)
        if os.path.isfile(sFilePath):
            CommonUtil.ExecLog(sModuleInfo, "File already exists", 1)
            if not overwrite:
                return 'passed' # Passed because the file does exist. User is responsible for ensuring file does not already exist

        # Create file
        with open(sFilePath, 'w') as newfile:
            if data != '': newfile.write(data)
            
        CommonUtil.ExecLog(sModuleInfo, "File created successfully", 1)
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error writing to %s:" % sFilePath)


# function to move file a to b
def MoveFile(file_to_be_moved, new_name_of_the_file):
    """
        :param file_to_be_moved: location of source file to be renamed
        :param new_name_of_the_file: location of destination file
        :return: Exception if Exception occurs otherwise return result  
    """
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Moving file %s to %s" % (file_to_be_moved, new_name_of_the_file), 0)
        shutil.move(file_to_be_moved, new_name_of_the_file)
        
        # after performing shutil.move() we have to check that if the file with new name exists in correct location.
        # if the file exists in correct position then return passed
        # if the file doesn't exist in correct position then return failed
        if os.path.isfile(new_name_of_the_file):
            CommonUtil.ExecLog(sModuleInfo, "File moved successfully", 0)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "File failed to move", 3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error moving file")

# function to rename file a to b
def RenameFile(file_to_be_renamed, new_name_of_the_file):
    """
        Wrapper for MoveFile
    """
    
    result = MoveFile(file_to_be_renamed, new_name_of_the_file)
    return result


# function to move folder a to b
def MoveFolder(folder_to_be_moved, new_name_of_the_folder):
    """
        :param folder_to_be_moved: location of source folder to be renamed
        :param new_name_of_the_folder: full location of destination folder
        :return: Exception if Exception occurs otherwise return result  
    """
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Moving folder from %s to %s" % (folder_to_be_moved, new_name_of_the_folder), 1)
        shutil.move(folder_to_be_moved, new_name_of_the_folder)
        
        # after performing shutil.move() we have to check that if the folder with new name exists in correct location.
        # if the folder exists in correct position then return passed
        # if the folder doesn't exist in correct position then return failed
        if os.path.isdir(new_name_of_the_folder):
            CommonUtil.ExecLog(sModuleInfo, "Folder moved successfully", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Folder failed to move", 3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error while moving folder")


# function to rename folder a to b
def RenameFolder(folder_to_be_renamed, new_name_of_the_folder):
    """
        Wrapper for MoveFolder
    """
    
    result = MoveFolder(folder_to_be_renamed, new_name_of_the_folder)
    return result

# function to unzip in linux
def UnZip(file_to_be_unzipped, location_where_to_unzip):
    """
        :param file_to_be_unzipped: location of source file to be unzipped
        :param location_where_to_unzip: location of destination 
        :return: Exception if Exception occurs or False if file doesn't exist otherwise return result  
    """
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Unzipping file %s to %s" % (file_to_be_unzipped, location_where_to_unzip), 1)
        if os.path.isfile(file_to_be_unzipped): # If zip file exists
            if not os.path.isdir(location_where_to_unzip): # If destination directory does not exist, create it
                CommonUtil.ExecLog(sModuleInfo, "Directory doesn't exist, creating", 1)
                if CreateFolder(location_where_to_unzip) in failed_tag_list: # Create directory, but if it fails, exit
                    CommonUtil.ExecLog(sModuleInfo, "Couldn't create directory, so can't unzip", 3)
                    return 'failed'
            
            # Unzip file
            zip_ref = zipfile.ZipFile(file_to_be_unzipped, 'r')
            zip_ref.extractall(location_where_to_unzip)
            result = zip_ref.close()
            if result in failed_tag_list:
                return 'failed'
            else:
                return 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Zip file doesn't exist", 3)
            return "failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error unzipping file")

def md5(fname):
    """
    calculates checksum of a file which can be used to compare to different files, If file is big then it will can be difficult to
    put the whole file on memory so we will read 4096 byte chunks and calculate checksum
    :param fname: location of the file
    :return: Exception if any problem occurs in hashing else return the checksum
    """
    try:
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return 'failed'

# function to compare two files
def CompareFile(file_to_be_compared1, file_to_be_compared2):
    """
        :param file_to_be_compared1: location of file to be compared
        :param file_to_be_compared2: location of file to be compared
        :return: Exception if Exception occurs otherwise return result  
    """
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Comparing %s with %s" % (file_to_be_compared1, file_to_be_compared2), 1)
        if md5(file_to_be_compared1) == md5(file_to_be_compared2):
            return 'passed'
        else:
            return 'failed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error comparing files")


# function to zip a file
def ZipFile(source, destination):
    """
        :param source: location of source file to be zipped (file or directory - directories are recursively zipped)
        :param destination: location of destination and filename
        :return: passed or failed
    """
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Zipping file %s to %s" % (source, destination), 0)
        path = os.path.dirname(destination) # Get path to destination
        
        # Create Zip archive
        if os.path.exists(source): # Verify source exists
            if os.path.isdir(path): # Verify destination directory exists
                with zipfile.ZipFile(destination, 'w') as z: # Create new Zip archive
                    # Write single file to archive
                    if os.path.isfile(source):
                        z.write(source)
                    
                    # Write directory and all contents recursively to archive
                    else:
                        for root, subdirs, files in os.walk(source):
                            for subdir in subdirs:
                                z.write(os.path.join(root, subdir)) # Write sub-directories (used when sub-directories are empty
                            for filename in files:
                                z.write(os.path.join(root, filename)) # Write all files and sub-directories

            # Verify result
            if os.path.isfile(destination):
                CommonUtil.ExecLog(sModuleInfo, "Zip archive successful", 0)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Could not create Zip archive", 0)
                return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "%s does not exist" % source, 3)
            return "failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error creating Zip archive")


# function to delete a file
def DeleteFile(sFilePath):
    """
        :param sFilePath: full location of the file to be deleted
        :return: Exception if Exception or False if file doesn't exist otherwise return the result
    """
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Deleting file %s" % sFilePath, 0)
        if os.path.isfile(sFilePath):
            os.remove(sFilePath)
            # after performing os.remove() we have to check that if the file still exists in that location.
            # if the file exists in that position then return failed as it is not deleted
            # if the file doesn't exist in that position then return passed
            if os.path.isfile(sFilePath):
                CommonUtil.ExecLog(sModuleInfo, "file exists... delete function is not done properly", 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "file doesn't exist... delete function is done properly", 0)
                return "passed"

        else:
            CommonUtil.ExecLog(sModuleInfo, "can't delete file as file doesn't exist", 3)
            return False
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# function to delete a folder
def DeleteFolder(sFolderPath): #!!! Needs to be updated to handle deleting of directories which contain files and sub-directories
    """
        :param sFolderPath: full location of the folder to be deleted
        :return: Exception if Exception or False if folder doesn't exist otherwise return the result
    """
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Deleting folder %s" % sFolderPath, 0)
        # print os.path.isdir(sFolderPath)
        if os.path.isdir(sFolderPath):
            shutil.rmtree(sFolderPath)
            # after performing os.remove() we have to check that if the folder still exists in that location.
            # if the folder exists in that position then return failed as it is not deleted
            # if the folder doesn't exist in that position then return passed
            if os.path.isdir(sFolderPath):
                CommonUtil.ExecLog(sModuleInfo, "folder exists... delete function is not done properly", 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "folder doesn't exist... delete function is done properly", 0)
                return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "can't delete folder as folder doesn't exist", 3)
            return False

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())



# function to check a file exists or not
def find(sFilePath): #!!!Needs to be updated to either return true/false or actually try to find a file in a file system
    """
        :param sFilePath: location of source folder to be found
        :return: Exception if Exception occurs otherwise return result  
    """
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Finding file %s is complete" % sFilePath, 1)
        return os.path.isfile(sFilePath)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# function to empty trash for linux
def empty_trash(trash_path): # !!! Change this so that it's a general recursive delete of all files and sub-directories. shouldn't limit to trash can, then have a smaller empty trash function
    """
        :param trash_path: path of the trash
        :return: Exception if Exception occurs or "falied" if trash is already empty
    """
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Starting to empty trash %s" % trash_path, 1)
        #  os.chdir('/home/tazin/.local/share/Trash')
        os.chdir(trash_path)
        if len(sys.argv) >= 2: # !!!this is all wrong
            if sys.argv[1] == '-t' or sys.argv[1] == '-T':
                os.system("tree ./")
            elif sys.argv[1] == '-l' or sys.argv[1] == '-L':
                os.system("ls -al")
        flag = 0
        for dir, sub_dirs, files in os.walk(trash_path):  # checking if trash is empty or not
            if not files:
                CommonUtil.ExecLog(sModuleInfo, "Trying to find files/folders in trash", 0)
            else:
                flag = 1  # Trash is not empty. Trash will be cleared if flag is changed to 1
        if flag == 1:
            result = os.system("rm -rf *")  # Empty Trash

        else:
            CommonUtil.ExecLog(sModuleInfo, "------Trash is empty already------", 1)
            return "passed"  # return "failed" if trash is already cleared

        CommonUtil.ExecLog(sModuleInfo, "Emptying trash %s is complete" % trash_path, 1)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# function to copy a folder
def copy_folder(src, dest):
    """
        :param src: source of the folder to be copied
        :param dest: destination where to be copied
        :return:  Exception if Exception occurs otherwise return result
    """
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Coping folder %s to %s" % (src, dest), 0)
        shutil.copytree(src, dest)
        # after performing shutil.copytree() we have to check that if the folder is created correct location.
        # if the folder exists in correct position then return passed
        # if the folder doesn't exist in correct position then return failed
        if os.path.isdir(dest):
            CommonUtil.ExecLog(sModuleInfo, "folder exists... copy function is done properly", 0)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "folder doesn't exist... copy function is not done properly", 3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# function to copy a file
def copy_file(src, dest): #!!!merge with copy_folder, just check if src is a file or not
    """
        :param src: source of the file to be copied
        :param dest: destination where to be copied
        :return:  Exception if Exception occurs otherwise return result  
    """
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        CommonUtil.ExecLog(sModuleInfo, "Coping file %s to %s" % (src, dest), 0)
        shutil.copyfile(src, dest)
        # after performing shutil.copyfile() we have to check that if the file with new name exists in correct location.
        # if the file exists in correct position then return passed
        # if the file doesn't exist in correct position then return failed
        if os.path.isfile(dest):
            CommonUtil.ExecLog(sModuleInfo, "file exists... copy function is done properly", 0)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "file doesn't exist... copy function is not done properly", 3)
            return "failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# function to empty recycle bin for windows
def empty_recycle_bin():
    """
        :return: Exception if Exception occurs or "failed if bin is empty otherwise return the result
    """
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        import winshell
        CommonUtil.ExecLog(sModuleInfo, "Staring to empty recycle bin", 0)
        recycle_bin = winshell.recycle_bin()
        List_recycle = list(recycle_bin)
        flag = 0
        if len(List_recycle) > 0:  # checking if trash is empty or not
            flag = 1  # Trash is not empty. Trash will be cleared if flag is changed to 1
        if flag == 1:
            result = winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)  # Empty Trash

        else:
            CommonUtil.ExecLog(sModuleInfo, "------Recycle Bin is empty already------", 1)
            return "passed"  # return "failed" if trash is already cleared

        CommonUtil.ExecLog(sModuleInfo, "Emptying recycle bin is complete", 1)
        return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# def run_win_cmd(cmd): #!!!!merge with run_cmd
#     """
#         :param cmd: admin command to run
#         :return: Exception if Exception occurs 
#     """
#     
#     sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
#     CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
#     
#     try:
#         result = []
#         process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#         for line in process.stdout:
#             result.append(line)
#         errcode = process.returncode
#         for line in result:
#             # print(line)
#             CommonUtil.ExecLog(sModuleInfo, "%s" % line, 1)
#         if errcode is not None:
#             CommonUtil.ExecLog(sModuleInfo, 'cmd %s failed, see above for details' % cmd, 3)
#             raise Exception('cmd %s failed, see above for details', cmd)
#     except Exception:
#         return CommonUtil.Exception_Handler(sys.exc_info())
# 
# 
# def run_win_cmd_and_save_in_shared_var(cmd,Save_in_var):  # !!!!merge with run_cmd
#     """
#         :param cmd: admin command to run
#         :return: Exception if Exception occurs 
#     """
# 
#     sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
#     CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
# 
#     try:
#         result = []
#         process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#         for line in process.stdout:
#             result.append(line)
#         errcode = process.returncode
#         Shared_Resources.Set_Shared_Variables(Save_in_var, result)
#         if errcode is not None:
#             CommonUtil.ExecLog(sModuleInfo, 'cmd %s failed, see above for details' % cmd, 3)
#             raise Exception('cmd %s failed, see above for details', cmd)
#     except Exception:
#         return CommonUtil.Exception_Handler(sys.exc_info())

# def run_cmd(command, return_status=False, is_shell=True, stdout_val=subprocess.PIPE, local_run=False):
#     """
#         :param command: sudo command to run
#         :return: Exception if Exception occurs otherwise return result 
#     """
#     
#     sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
#     CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
#     
#     '''Begin Constants'''
#     Passed = "Passed" # !!!remove this nad use passed_tag_list,e tc
#     Failed = "Failed"
#     Running = 'running'
#     '''End Constants'''
# 
#     # Run 'command' via command line in a bash shell, and store outputs to stdout_val
#     sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
#     subprocess_dict = {}
#     try:
#         # global subprocess_dict
#         result = []
# 
#         # open a subprocess with command, and assign a session id to the shell process
#         # this is will make the shell process the group leader for all the child processes spawning from it
#         status = subprocess.Popen(command, shell=is_shell, stdout=stdout_val, preexec_fn=os.setsid)
#         subprocess_dict[status] = Running
#         status.wait() # Wait for process to complete, and populate returncode
#         errcode = status.returncode
#         
#         for line in status.stdout:
#             result.append(line)
#         
#         for line in result:
#             CommonUtil.ExecLog(sModuleInfo, "%s" % line, 1)
#         
#         if return_status:
#             return errcode, result
#         elif errcode == 0:
#             return Passed
#         else:
#             return Failed
# 
#     except Exception:
#         return CommonUtil.Exception_Handler(sys.exc_info())
# 
# def run_cmd_and_save_in_Shared_var(Save_in_var, command, return_status=False, is_shell=True, stdout_val=subprocess.PIPE, local_run=False):
#     """
#         :param command: sudo command to run
#         :return: Exception if Exception occurs otherwise return result 
#     """
# 
#     sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
#     CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
# 
#     '''Begin Constants'''
#     Passed = "Passed" # !!!remove this nad use passed_tag_list,e tc
#     Failed = "Failed"
#     Running = 'running'
#     '''End Constants'''
# 
#     # Run 'command' via command line in a bash shell, and store outputs to stdout_val
#     sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
#     subprocess_dict = {}
#     try:
#         # global subprocess_dict
#         result = []
# 
#         # open a subprocess with command, and assign a session id to the shell process
#         # this is will make the shell process the group leader for all the child processes spawning from it
#         status = subprocess.Popen(command, shell=is_shell, stdout=stdout_val, preexec_fn=os.setsid)
#         subprocess_dict[status] = Running
#         status.wait() # Wait for process to complete, and populate returncode
#         errcode = status.returncode
# 
#         for line in status.stdout:
#             result.append(line)
# 
#         Shared_Resources.Set_Shared_Variables(Save_in_var, result)
# 
#         if return_status:
#             return errcode, result
#         elif errcode == 0:
#             return Passed
#         else:
#             return Failed
# 
#     except Exception:
#         return CommonUtil.Exception_Handler(sys.exc_info())


# function to generate random string
def random_string_generator(pattern='nluc', size=10):
    ''' Generates a random string '''
    # pattern: At least one or more of the following: n l u c (number, lowercase, uppercase, characters)
    # size: Length of string
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        pattern = pattern.lower().strip()
        punctuation = '`~!@#$%^&.'
        chars = ''
        for index in range(0, len(pattern)):
            if pattern[index] == 'n':  # Numbers
                chars += string.digits
            if pattern[index] == 'l':  # Lowercase
                chars += string.ascii_lowercase
            if pattern[index] == 'u':  # Uppercase
                chars += string.uppercase
            if pattern[index] == 'c':  # Characters
                chars += punctuation

        if chars == '':
            return 'failed'
        else:
            return ''.join(random.choice(chars) for _ in range(size))
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to download file using url
def download_file_using_url(file_url, location_of_file):
    ''' Download a file and save to disk '''
    # file_url: URL of file
    # location_of_file: Where to save file on disk
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        ''' Setting stream parameter to True will cause the download of response headers only and the connection remains open.
          This avoids reading the content all at once into memory for large responses.
         A fixed chunk will be loaded each time while r.iter_content is iterated.'''
        r = requests.get(file_url, stream=True) # Open connection

        # Download file and save to disk
        file_name = os.path.join(location_of_file , str(file_url.split("/")[-1:][0])) #complete file location
        CommonUtil.ExecLog(sModuleInfo, "Path of file to download: %s" % file_name, 0)
        with open(file_name, "wb") as f: # Open new binary file
            for chunk in r.iter_content(chunk_size=1048576): # Grab chunk of received data
                if chunk: f.write(chunk) # Write chunk of data to disk
        
        # Verify file exists
        if os.path.isfile(file_name):
            return file_name
        else:
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error downloading file")

#Method to download and unzip file
# def download_and_unzip_file(file_url, location_of_file): #!!!change this to call download_file_using_url instead of duplicating work, or just remove download part, and whatever is calling this can call the two pieces separately
#     
#     sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
#     CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
#     
#     try:
#         ''' Setting stream parameter to True will cause the download of response headers only and the connection remains open.
#           This avoids reading the content all at once into memory for large responses.
#          A fixed chunk will be loaded each time while r.iter_content is iterated.'''
#         r = requests.get(file_url, stream=True)
# 
#         list_the_parts_of_url = file_url.split("/") #get file name from the url
#         file_name = os.path.join(location_of_file, list_the_parts_of_url[len(list_the_parts_of_url) - 1])
#         actual_file_name = list_the_parts_of_url[len(list_the_parts_of_url) - 1]
#         with open(file_name, "wb") as f:
#             for chunk in r.iter_content(chunk_size=1024):
# 
#             # writing one chunk at a time to pdf file
#                 if chunk:
#                     f.write(chunk)
#         # after performing the download operation we have to check that if the file with new name exists in correct location.
#         # if the file exists in correct position then return passed
#         # if the file doesn't exist in correct position then return failed
#         if os.path.isfile(file_name):
#             CommonUtil.ExecLog(sModuleInfo, "file exists... downloading file using url function is done properly", 0)
#         else:
#             CommonUtil.ExecLog(sModuleInfo, "file doesn't exist... downloading file using url function is not done properly", 3)
#             return "failed"
#         unzip_location = os.path.join(location_of_file,"latest_directory" )
#         CommonUtil.ExecLog(sModuleInfo, "Creating the directory '%s' " % unzip_location, 0)
#         result1 = CreateFolder(unzip_location)
#         if result1 in failed_tag_list:
#             CommonUtil.ExecLog(sModuleInfo, "Can't not create folder '%s' " % unzip_location, 3)
#             return "failed"
#         CommonUtil.ExecLog(sModuleInfo, "Folder '%s' is created " % unzip_location, 1)
#         result = UnZip(file_name,unzip_location)
#         if result in failed_tag_list:
#             CommonUtil.ExecLog(sModuleInfo, "Can't not unzip file '%s' to '%s'" % (file_name, unzip_location), 3)
#             return "failed"
#         CommonUtil.ExecLog(sModuleInfo, "Unzipping file '%s' to '%s' is complete" % (file_name, unzip_location), 0)
#         CommonUtil.ExecLog(sModuleInfo, "Saving directory location to shared resources" , 1)
#         #Shared_Resources.Set_Shared_Variables("latest_directory", unzip_location)
#         downloaded_file = os.path.join(unzip_location,actual_file_name )
#         Shared_Resources.Set_Shared_Variables("downloaded_file", downloaded_file)
#         Shared_Resources.Show_All_Shared_Variables()
#         return "passed"
# 
# 
#     except Exception:
#         return CommonUtil.Exception_Handler(sys.exc_info())


# not done properly...need more works
'''def change_path_for_windows(src):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Change path for Windows", 1)
    print src
    string_list = str(src).split("\\")
    print string_list
    print src
    return src
'''

'============================= Sanitization Begins =============================='


def sanitize_step_data(step_data, valid_chars = '', clean_whitespace_only = False, column = ''):
    ''' Sanitize step data Field and Sub-Field '''
    ''' Usage:
            Is to be used to allow users flexibility in their step data input, but allow the program to find key words
            :valid_chars: By default this function removes all characters. Specifying a string of characters here will skip removing them
            :clean_whitespace_only: If your function uses several characters, you can set this to True, to only clean up white space
            :column: Leave blank for default Field and Sub-Field (1,2). Set as a comma separated string to indicate columns to be cleaned (eg: 2,3 or just 3)
            If the user surrounds their input with double quotes, all sanitizing will be skipped, and the surrounding quotes will be removed
    '''
    
    # Set columns in the step data to sanitize (default is Field and Sub-Field only)
    if column == '': # By default, sanitize the first and second columns (Field and Sub-Field)
        column = [0,1]
    else:
        column = str(column).replace(' ', '') # Remove spaces
        column = column.split(',') # Put into list
        column = map(int, column) # Convert numbers in list into integers, so they can be used to address tuple elements
    
    new_step_data = [] # Create empty list that will contain the data sets
    for data_set in step_data: # For each data set within step data
        new_data_set = [] # Create empty list that will have new data appended
        for row in data_set: # For each row of the data set
            new_row = list(row) # Copy tuple of row as list, so we can change it
            for i in column: # Sanitize the specified columns
                if str(new_row[i])[:1] == '"' and str(new_row[i])[-1:] == '"': # String is within double quotes, indicating it should not be changed
                    new_row[i] = str(new_row[i])[1:len(new_row[i]) - 1] # Remove surrounding quotes
                    continue # Do not change string
                
                # Sanitize the column for this row
                new_row[i] = sanitize_string(new_row[i], valid_chars, clean_whitespace_only, maxLength = None)

            new_data_set.append(tuple(new_row)) # Append list as tuple to data set list
        new_step_data.append(new_data_set) # Append data set to step data
    return new_step_data # Step data is now clean and in the same format as it arrived in

def sanitize_string(strg, valid_chars = '', clean_whitespace_only = False, maxLength = None):
    ''' Sanitize string '''
    ''' Usage:
            By default returns the string without special characters, in lower case, underscore replaced with space, and surrounding whitespace removed
            :valid_chars: By default this function removes all characters. Specifying a string of characters here will skip removing them
            :clean_whitespace_only: If your function uses several characters, you can set this to True, to only clean up white space
    '''
    
    # Invalid character list (space and underscore are handle separately)
    invalid_chars = '!"#$%&\'()*+,-./:;<=>?@[\]^`{|}~'

    # Adjust invalid character list, based on function input
    for j in range(len(valid_chars)): # For each valid character
        invalid_chars = invalid_chars.replace(valid_chars[j], '') # Remove valid character from invalid character list
    
    if clean_whitespace_only == False:
        for j in range(0,len(invalid_chars)): # For each invalid character (allows us to only remove those the user hasn't deemed valid)
            strg = strg.replace(invalid_chars[j], '') # Remove invalid character
            strg = strg.lower() # Convert to lower case
        if '_' not in valid_chars: strg = strg.replace('_', ' ') # Underscore to space (unless user wants to keep it)

    strg = strg.replace('  ', ' ') # Double space to single space
    strg = strg.strip() # Remove leading and trailing whitespace

    # Truncate if maximum length specified
    if maxLength != None:
        strg = strg[:maxLength]
        
    return strg



'===================== ===x=== Sanitization Ends ===x=== ======================'

'============================= Raw String Generation Begins=============================='

# code to generate raw string
def raw(text):
    """Returns a raw string representation of text"""
    
    escape_dict = {
        '\b': r'\b',
        '\c': r'\c',
        '\f': r'\f',
        '\n': r'\n',
        '\r': r'\r',
        '\t': r'\t',
        '\v': r'\v',
        '\'': r'\'',
        '\"': r'\"',
        '\0': r'\0',
        '\1': r'\1',
        '\2': r'\2',
        '\3': r'\3',
        '\4': r'\4',
        '\5': r'\5',
        '\6': r'\6',
        '\7': r'\7',
        '\8': r'\8',
        '\9': r'\9',
        '\a': r'\a',
    }

    new_string = ''
    for char in text:
        try:
            new_string += escape_dict[char]
        except KeyError:
            new_string += char
    return new_string


'============================= Raw String Generation Ends=============================='

#########################
#                       #
#   Sequential Actions  #
#                       #
#########################

# Method to copy file/folder
def Copy_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

    # Recall file attachment, if not already set
    file_attachment = []
    if Shared_Resources.Test_Shared_Variables('file_attachment'):
        file_attachment = Shared_Resources.Get_Shared_Variables('file_attachment')

    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
            from_path = str(step_data[0][2]).strip()  # location of the file/folder to be copied
            if from_path[0]=="/": from_path=from_path.lstrip('/')
            to_path = str(step_data[1][2]).strip()
            if to_path[0] == "/": to_path=to_path.lstrip('/')
            to_path =os.path.join( get_home_folder() , to_path)  # location where to copy the file/folder
        elif _platform == "win32":
            from_path = raw(str(step_data[0][2]).strip())  # location of the file/folder to be copied
            to_path = os.path.join(get_home_folder(),raw(str(step_data[1][2]).strip()))  # location where to copy the file/folder
        file_or_folder = str(step_data[2][2]).strip()  # get if it is file/folder to copy
        # Try to find the file
        if from_path not in file_attachment and os.path.exists(os.path.join(get_home_folder(), from_path)) == False:
            CommonUtil.ExecLog(sModuleInfo,
                               "Could not find file attachment called %s, and could not find it locally" % from_path, 3)
            return 'failed'
        if from_path in file_attachment: from_path = file_attachment[from_path]  # In file is an attachment, get the full path

        if from_path not in file_attachment:
            from_path = os.path.join(get_home_folder(), from_path)
        if file_or_folder.lower() == 'file':
                # copy file "from_path" to "to_path"
            result = copy_file(from_path, to_path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Could not copy file '%s' to the destination '%s'" % (from_path, to_path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"File '%s' copied to the destination '%s' successfully" % (from_path, to_path), 1)
                return "passed"
        elif file_or_folder.lower() == 'folder':
            # copy folder "from_path" to "to_path"
            result = copy_folder(from_path, to_path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Could not copy folder '%s' to the destination '%s'" % (from_path, to_path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"Folder '%s' copied to the destination '%s' successfully" % (from_path, to_path),1)
                return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return 'failed'

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

# Method to unzip
def Unzip_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

    # Recall file attachment, if not already set
    file_attachment = []
    if Shared_Resources.Test_Shared_Variables('file_attachment'):
        file_attachment = Shared_Resources.Get_Shared_Variables('file_attachment')

    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
            from_path = str(step_data[0][2]).strip()  # location of the file/folder to be copied
            if from_path[0]=="/": from_path=from_path.lstrip('/')

        elif _platform == "win32":
            from_path = raw(str(step_data[0][2]).strip())  # location of the file/folder to be copied


        # Try to find the file
        if from_path not in file_attachment and os.path.exists(os.path.join(get_home_folder(), from_path)) == False:
            CommonUtil.ExecLog(sModuleInfo,"Could not find file attachment called %s, and could not find it locally" % from_path, 3)
            return 'failed'
        if from_path not in file_attachment:
            from_path = os.path.join(get_home_folder(), from_path)
            if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
                to_path = str(step_data[1][2]).strip()
                if to_path[0] == "/": to_path = to_path.lstrip('/')
                to_path = os.path.join(get_home_folder(), to_path)  # location where to copy the file/folder
            elif _platform == "win32":
                to_path = os.path.join(get_home_folder(),raw(str(step_data[1][2]).strip()))  # location where to copy the file/folder
        if from_path in file_attachment:
            file_name = from_path
            from_path = file_attachment[from_path]  # In file is an attachment, get the full path
            to_path = from_path[0 : len(from_path)-(len(file_name)+1)]
            Save_in_variable = step_data[1][2]




        result = UnZip(from_path, to_path)
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Can't not unzip '%s' to '%s'" % (from_path, to_path), 3)
            return "failed"
        else:
            Shared_Resources.Set_Shared_Variables(Save_in_variable, to_path)
            CommonUtil.ExecLog(sModuleInfo, "'%s' is unzipped to '%s' successfully" % (from_path, to_path), 1)
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Get_Attachment_Path(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

        # Recall file attachment, if not already set
    file_attachment = []
    if Shared_Resources.Test_Shared_Variables('file_attachment'):
        file_attachment = Shared_Resources.Get_Shared_Variables('file_attachment')

    try:
        for row in step_data:

            if row[1] == 'path':
                from_path = row[2]
            if row[1] == 'value':
                Save_in_variable = row[2]


            # Try to find the file
        if from_path not in file_attachment :
            CommonUtil.ExecLog(sModuleInfo,
                                   "Could not find file attachment called %s, " % from_path,
                                   3)
            return 'failed'
        if from_path in file_attachment: from_path = file_attachment[from_path]  # In file is an attachment, get the full path

        Shared_Resources.Set_Shared_Variables(Save_in_variable, from_path)

        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to delete file/folder
def Delete_File_or_Folder(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    # Parse data set
    try:
        filename = ''
        path = ''
        for row in data_set:
            if row[1] == 'action':
                if row[2] in ('file', 'folder'): continue # Skip these old methods
                filename = row[2].strip()
            elif row[1] in ('path', 'element paraneter') and filename == '': # Just in case someone used a second row to specify the filename, we'll use that
                filename = row[2].strip()
        
        if filename == '':
            CommonUtil.ExecLog(sModuleInfo,"Could not find filename or path to file in Value field of action line", 3)
            return 'failed'
        
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")
    
    # Perform action
    try:
        if os.path.exists(filename) == False: # Check if file exists as it is (local directory or fully specified), if not...
            tmp = filename # Save copy of filename to work with it
            if tmp[:1] == os.sep: tmp = tmp[1:] # If it has a leading slash, remove it
            tmp = os.path.join(get_home_folder(), tmp)  # path of the file/folder to be deleted, in case user specified path relative to home directory
            if os.path.exists(tmp) == False: # Check if file is in home directory, or path is partially specified, we'll complete it with the home directory
                CommonUtil.ExecLog(sModuleInfo,"Could not find file in attachments, home directory or in the local directory: %s" % filename, 3)
                return 'failed'
            else:
                filename = tmp # Save the constructed path
        # Should now have a full path to the filename
            

        # Delete file/directory
        if os.path.isfile(filename):
            result = DeleteFile(filename)
        elif os.path.isdir(filename):
            result = DeleteFolder(filename)
        else:
            CommonUtil.ExecLog(sModuleInfo, "File/directory specified does exist, but is neither a file nor a directory. It could not be deleted", 3)
            return 'failed'
        
        # Verify result
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not delete file '%s'" % (filename), 3)
            return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "File '%s' deleted successfully" % (filename), 1)
            return "passed"


    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

# Method to create file/folder
def Create_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
            path = get_home_folder() + str(step_data[0][2]).strip()  # path of the file/folder to be created
            file_or_folder = str(step_data[1][2]).strip()  # get if it is file/folder to create
        elif _platform == "win32":
            path = raw(str(step_data[0][2]).strip())  # path of the file/folder to be created
            file_or_folder = str(step_data[1][2]).strip()  # get if it is file/folder to create


        if file_or_folder.lower() == 'file':
                # create file "path"
            result = CreateFile(path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not create file '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "File '%s' created successfully" % (path), 1)
                return "passed"
        elif file_or_folder.lower() == 'folder':
                # create folder "path"
            result = CreateFolder(path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not create folder '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Folder '%s' created successfully" % (path), 1)
                return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return 'failed'


    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())




# Method to find file
def Find_File(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        path = get_home_folder() + str(step_data[0][0]).strip()
        file_or_folder = str(step_data[1][2]).strip()
        if file_or_folder.lower() == 'file':
            # find file "path"
            result = find(path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find file '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "File '%s' is found" % (path), 1)
                return "passed"

        else:
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return 'failed'

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to empty trash/recycle bin
def Empty_Trash(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            path = get_home_folder() + '/.local/share/Trash'  # location of trash for linux
            # print path

            result = empty_trash(path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not empty trash '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "trash is cleared '%s'" % (path), 1)
                return "passed"
        elif _platform == "win32":
            # windows
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            result = empty_recycle_bin()  # location of the recycle bin
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not empty recycle bin ", 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "recycle bin is cleared ", 1)
                return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to Get User Name
def Get_User_Name(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
            path = get_home_folder()  # get the path of the home directory
            list_elemnet = path.split("/")  # list the parts of path by splitting it by "/"
            name = list_elemnet[len(list_elemnet) - 1]  # name of the user
            if name in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find user name '%s'" % (name), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "user name is '%s'" % (name), 1)
                return "passed"
        elif _platform == "win32":
            # windows
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            CommonUtil.ExecLog(sModuleInfo, "Could not find user name as it is windows", 3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to add log
def Add_Log(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        log_info = str(step_data[0][0]).strip() #get the log level info from the step data
        list = log_info.split(" ") # log level in step data is given as log_1/log_2/log_3 , so to get the level split it by "_"
        Comment = str(step_data[0][2]).strip()  # get the comment
        LogLevel = int(list[1]) #get the level
        CommonUtil.ExecLog(sModuleInfo, "%s" % Comment, LogLevel)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to Calculate
def Calculate(step_data):
    ''' Perform any mathematical calculation exactly as written by the user '''
    # Format: shared_var_name=1+(2*3)....etc
     
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        # Prepare data
        statement = str(step_data[0][2]).strip().replace(' ', '')  # get the statement for math function
        params_list = statement.split("=") # list the parts of statement by splitting it by "="
        var_name = params_list[0] # Save name of shared variable
        math_string = params_list[1] # Save mathematical calculation
        
        # Calculate and save result
        result = eval(math_string) # eval()  does the auto calculation from a string.
        CommonUtil.ExecLog(sModuleInfo, "Calculation: %s = %s" % (math_string, result), 1)
        Shared_Resources.Set_Shared_Variables(var_name, result)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to Run Command
def Run_Command(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

    # Parse data set
    try:
        commands = [] # Need at least one command, multiple commands will be executed in order
        shared_var = '' # Optional - store output of command in shared variable
        for row in data_set:
            op = row[0].lower().strip()
            cmd = row[2].strip()
            if op == 'command':
                commands.append(cmd)
            elif op in ('shared var', 'shared variable', 'var', 'variable', 'save'):
                shared_var = cmd.replace('%|', '').replace('|%', '') # Save variable name, remove identifying characters if accidentally provided
        if len(commands) == 0:
            CommonUtil.ExecLog(sModuleInfo, "No commands specified. Expected at least one row to contain 'command' in the Field, and the command to execute in the Value field", 3)
            return 'failed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    # Execute command    
    try:
        # Set command deliminator
        if _platform == 'win32': delim = '&'
        else: delim = ';'
        
        # Execute commands as a single command line command, separated by the OS's shell deliminator. This allows us to maintain a shell history, so all commands work as expected
        h = subprocess.Popen(delim.join(commands), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) # Execute commands, collect STDERR and redirect it to STDOUT, so it's all together
        h.wait() # Wait for process to complete
        result = h.returncode # Get last command result
        output = ''
        for line in h.stdout: output += line # Get command output from STDOUT and STDERR
        
        CommonUtil.ExecLog(sModuleInfo, "Command output: %s" % output, 1) # Write output to log
        if shared_var:
            output = output.replace('\n', '')  # replace any new line in string that may have came from terminal
            Shared_Resources.Set_Shared_Variables(shared_var, output) # Save command output to shared variable, if user specified it
        
        # Exit
        if result != 0:
            CommonUtil.ExecLog(sModuleInfo, "Command failed. See above for command output", 3)
            return 'failed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Command executed successfully", 1)
            return 'passed'
        
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error executing command")


# def Run_Command(step_data):
#     sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
#     CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
#     try:
#         if step_data[0][0] == "run command":
#             if _platform == "win32":
#                 # windows
#                 command = str(step_data[0][2]).strip()
#                 result = run_win_cmd(command)
#                 if result in failed_tag_list:
#                     CommonUtil.ExecLog(sModuleInfo, "Could not run sudo command '%s'" % (command), 3)
#                     return "failed"
#                 else:
#                     CommonUtil.ExecLog(sModuleInfo, "sudo command is run properly '%s'" % (command), 1)
#                     return "passed"
#             elif _platform == "linux" or _platform == "linux2" or _platform == "darwin":
# 
#                 CommonUtil.ExecLog(sModuleInfo, "Could not run admin command for linux/mac", 3)
#                 return "failed"
#         elif step_data[0][0] == "run sudo":
#             if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
#                 command = str(step_data[0][2]).strip()
#                 result = run_cmd(command)
#                 if result in failed_tag_list:
#                     CommonUtil.ExecLog(sModuleInfo, "Could not run sudo command '%s'" % (command), 3)
#                     return "failed"
#                 else:
#                     CommonUtil.ExecLog(sModuleInfo, "sudo command is run properly '%s'" % (command), 1)
#                     return "passed"
#             elif _platform == "win32":
#                 # windows
#                 CommonUtil.ExecLog(sModuleInfo, "Could not run sudo command as it is windows", 3)
#                 return "failed"
#     except Exception:
#         return CommonUtil.Exception_Handler(sys.exc_info())
# 
# # Method to Run Command
# def Run_Command_and_Save(step_data):
#     sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
#     CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
#     try:
# 
#             if _platform == "win32":
#                 # windows
#                 command = str(step_data[0][2]).strip()
#                 Shared_var= str(step_data[1][2]).strip()
#                 result = run_win_cmd_and_save_in_shared_var(command,Shared_var)
#                 if result in failed_tag_list:
#                     CommonUtil.ExecLog(sModuleInfo, "Could not run sudo command '%s'" % (command), 3)
#                     return "failed"
#                 else:
#                     CommonUtil.ExecLog(sModuleInfo, "sudo command is run properly '%s'" % (command), 1)
#                     return "passed"
# 
# 
#             elif _platform == "linux" or _platform == "linux2" or _platform == "darwin":
#                 command = str(step_data[0][2]).strip()
#                 Shared_var = str(step_data[1][2]).strip()
#                 result = run_cmd_and_save_in_Shared_var(Shared_var,command)
#                 if result in failed_tag_list:
#                     CommonUtil.ExecLog(sModuleInfo, "Could not run sudo command '%s'" % (command), 3)
#                     return "failed"
#                 else:
#                     CommonUtil.ExecLog(sModuleInfo, "sudo command is run properly '%s'" % (command), 1)
#                     return "passed"
# 
#     except Exception:
#         return CommonUtil.Exception_Handler(sys.exc_info())

# Method to Get Home Directory
def Get_Home_Directory(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    try:
        home_dir = data_set[0][2] # Get shared variable name from Value on action row
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())
    
    try:
        path = get_home_folder() # Get home directory path
        if path in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find home directory: '%s'" % str(path), 3)
            return 'failed'
        CommonUtil.ExecLog(sModuleInfo, "Home Directory Path is '%s'" % (path), 1)
        
        Shared_Resources.Set_Shared_Variables(home_dir, path) # Store home directory in shared variable
        return 'passed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to Get Current Desktop
def Get_Current_Desktop(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        path = os.path.join(get_home_folder(), 'Desktop') # concate home folder path with "/Desktop"

        if path in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find desktop '%s'" % (path), 3)
            return "failed"

        CommonUtil.ExecLog(sModuleInfo, "desktop path is '%s'" % (path), 1)
        Shared_Resources.Set_Shared_Variables("Desktop", path)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to Get Current Documents
def Get_Current_Documents(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        path = os.path.join(get_home_folder(), 'Documents') # concate home folder path with "/Desktop"

        if path in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find Documents path '%s'" % (path), 3)
            return "failed"

        CommonUtil.ExecLog(sModuleInfo, "Documents path is '%s'" % (path), 1)
        Shared_Resources.Set_Shared_Variables("Documents", path)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to create file
def Create_File(step_data):#!!!why is this here
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        path = get_home_folder() + str(step_data[0][2]).strip()
        file_or_folder = str(step_data[1][2]).strip()
        if file_or_folder.lower() == 'file':
            # create file "path"
            result = CreateFile(path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not create file '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "File '%s' created" % (path), 1)
                return "passed"

        else:
            CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return 'failed'

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

# Method to compare file
def Compare_File(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

    # Recall file attachment, if not already set
    file_attachment = []
    if Shared_Resources.Test_Shared_Variables('file_attachment'):
        file_attachment = Shared_Resources.Get_Shared_Variables('file_attachment')

    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
            from_path = str(step_data[0][2]).strip()  # location of file path to be compared
            to_path = str(step_data[1][2]).strip()  # location of file path to be compared
        elif _platform == "win32":
            from_path = raw(str(step_data[0][2]).strip())  # location of file path to be compared
            # print  from_path
            to_path = raw(str(step_data[1][2]).strip())  # location of file path to be compared

        # Try to find the file
        if from_path not in file_attachment and os.path.exists(os.path.join(get_home_folder(), from_path)) == False:
            CommonUtil.ExecLog(sModuleInfo,
                               "Could not find file attachment called %s, and could not find it locally" % from_path, 3)
            return 'failed'
        if from_path in file_attachment: from_path = file_attachment[from_path]  # In file is an attachment, get the full path

        if from_path not in file_attachment:
            from_path = os.path.join(get_home_folder(), from_path)

        # Try to find the file
        if to_path not in file_attachment and os.path.exists(os.path.join(get_home_folder(), to_path)) == False:
            CommonUtil.ExecLog(sModuleInfo,
                               "Could not find file attachment called %s, and could not find it locally" % to_path, 3)
            return 'failed'
        if to_path in file_attachment: to_path = file_attachment[to_path]  # In file is an attachment, get the full path

        if to_path not in file_attachment:
            to_path = os.path.join(get_home_folder(), to_path)

        file_or_folder = str(step_data[2][2]).strip()
        if file_or_folder.lower() == 'file':
            # compare file "from_path" and "to_path"
            result = CompareFile(from_path, to_path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Files %s and %s are not equal" % (to_path, from_path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "File '%s' and %s are equal " % (to_path, from_path), 1)
                return "passed"

        else:
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return 'failed'

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to rename file/folder
def Rename_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin" :

            from_path = get_home_folder() + str(step_data[0][2]).strip()  # location of the file/folder to be renamed
            to_path = get_home_folder() + str(step_data[1][2]).strip()  # location where to rename the file/folder
        elif _platform == "win32":
            from_path = raw(str(step_data[0][2]).strip())  # location of the file/folder to be renamed
            to_path = raw(str(step_data[1][2]).strip())  # location where to rename the file/folder

        file_or_folder = str(step_data[2][2]).strip()  # get if it is file/folder to rename
        if file_or_folder.lower() == 'file':
                # rename file "from_path" to "to_path"
            result = RenameFile(from_path, to_path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not rename file '%s' to '%s'" % (from_path, to_path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "File '%s' renamed to '%s' successfully" % (from_path, to_path), 1)
                return "passed"
        elif file_or_folder.lower() == 'folder':
                # rename folder "from_path" to "to_path"
            result = RenameFolder(from_path, to_path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not rename folder '%s' to '%s'" % (from_path, to_path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Folder '%s' renamed to '%s' successfully" % (from_path, to_path),
                                       1)
                return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return 'failed'


    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())



# Method to zip file/folder
def Zip_File_or_Folder(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    # Parse data set
    try:
        source = ''
        destination = ''
        
        for row in data_set:
            if row[0].lower().strip() in ('src', 'source'):
                source = row[2].strip()
            elif row[0].lower().strip() in ('dst', 'dest', 'destination'):
                destination = row[2].strip()

        if source == '' or destination == '':
            CommonUtil.ExecLog(sModuleInfo, "Either 'source' or 'destination' information missing", 3)
            return 'failed'
        
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")
        
    # Zip file
    try:
        result = ZipFile(source, destination) # Perform zip on file or directory

        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Cannot zip file '%s' to '%s'" % (source, destination), 3)
            return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "File '%s' zipped to '%s' successfully" % (source, destination), 1)
            return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error zipping")





# Method to move file/folder
def Move_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

    # Recall file attachment, if not already set
    file_attachment = []
    if Shared_Resources.Test_Shared_Variables('file_attachment'):
        file_attachment = Shared_Resources.Get_Shared_Variables('file_attachment')

    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin" :

            from_path = str(step_data[0][2]).strip()  # location of the file/folder to be renamed
            to_path = str(step_data[1][2]).strip()  # location where to rename the file/folder
        elif _platform == "win32":
            from_path = raw(str(step_data[0][2]).strip())  # location of the file/folder to be renamed
            to_path = raw(str(step_data[1][2]).strip())  # location where to rename the file/folder

         # Try to find the file
        if from_path not in file_attachment and os.path.exists(os.path.join(get_home_folder(), from_path)) == False:
            CommonUtil.ExecLog(sModuleInfo,
                               "Could not find file attachment called %s, and could not find it locally" % from_path, 3)
            return 'failed'
        if from_path in file_attachment: from_path = file_attachment[from_path]  # In file is an attachment, get the full path

        if from_path not in file_attachment:
            from_path = os.path.join(get_home_folder(), from_path)


        to_path = os.path.join(get_home_folder(), to_path)

        file_or_folder = str(step_data[2][2]).strip()  # get if it is file/folder to move
        if file_or_folder.lower() == 'file':
                # move file "from_path to "to_path"
            result = MoveFile(from_path, to_path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not move file '%s' to '%s'" % (from_path, to_path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "File '%s' moved to '%s' successfully" % (from_path, to_path), 1)
                return "passed"
        elif file_or_folder.lower() == 'folder':
                # move folder "from_path" to "to_path"
            result = MoveFolder(from_path, to_path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not move folder '%s' to '%s'" % (from_path, to_path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Folder '%s' moved to '%s' successfully" % (from_path, to_path), 1)
                return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return 'failed'

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


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

# Copy/paste file to zeuz log uploader
def Upload(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            from_path = get_home_folder() + str(step_data[0][2]).strip()  # location of the file/folder to be copied\
            temp_ini_file = get_home_folder() + "/Desktop/AutomationLog/temp_config.ini"
            list = from_path.split("/")
            to_path = ConfigModule.get_config_value('sectionOne', 'test_case_folder', temp_ini_file) +"/"+ list[len(list) - 1]  # location where to copy the file/folder

        elif _platform == "win32":
            # windows
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            from_path = raw(str(step_data[0][0]).strip())  # location of the file/folder to be copied
            temp_ini_file = get_home_folder() + raw("\Desktop\AutomationLog\temp_config.ini")
            list = from_path.split("\\")
            to_path = ConfigModule.get_config_value('sectionOne', 'test_case_folder', temp_ini_file) + "\\" + list[len(list) - 1]

        result = copy_file(from_path, to_path)
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Could not copy file '%s' to the log uploader '%s'" % (from_path, to_path), 3)
            return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"File '%s' copied to the log uploader '%s' successfully" % (from_path, to_path), 1)
            return "passed"


    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())




temp_config = os.path.join(os.path.join(get_home_folder(), os.path.join('Desktop', os.path.join('AutomationLog',ConfigModule.get_config_value('Temp', '_file')))))


def TakeScreenShot(step_data):
    """
    Takes screenshot and saves it as jpg file
    name is the name of the file to be saved appended with timestamp
    #TakeScreenShot("TestStepName")
    """
    # file Name don't contain \/?*"<>|
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

    try:
        ImageName = 'image'
        image_folder = get_home_folder()
        # ImageFolder = Global.TCLogFolder + os.sep + "Screenshots"
        ImageFolder = image_folder  # location of the folder where the screen shot should be saved
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

            # linux working copy

            full_location = ImageFolder + os.sep + TimeStamp("utc") + "_" + ImageName + '.png'  # location of the file where the screen shot should be saved
            CommonUtil.ExecLog(sModuleInfo, "file location is %s" % full_location, 1)
            # os.system("import -window root %s"%full_location)

            try:
                from gi.repository import Gdk

            except ImportError:
                CommonUtil.ExecLog(sModuleInfo,'could not import python package needed for screenshot...installing package "gi"', 1)
                os.system('pip install gi')

            # set the root window as the window we want for screenshot
            window = Gdk.get_default_root_window()
            # get dimensions of the window
            x, y, width, height = window.get_geometry()

            # print 'taking screenshot...'
            CommonUtil.ExecLog(sModuleInfo, 'taking screenshot...', 1)
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
                CommonUtil.ExecLog(sModuleInfo, 'screenshot saved as: "%s"' % full_location, 1)
                # print 'screenshot saved as: "%s"' % full_location
            else:
                # print "unable to take screenshot..."
                CommonUtil.ExecLog(sModuleInfo, "unable to take screenshot...", 1)



        elif os.name == 'nt':
            # windows working copy
            from PIL import ImageGrab
            from PIL import Image
            path = ImageFolder + os.sep + TimeStamp("utc") + "_" + ImageName + ".jpg"  # location of the file where the screen shot should be saved
            img = ImageGrab.grab()
            basewidth = 1200
            wpercent = (basewidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            img.save(path, 'JPEG')
            CommonUtil.ExecLog(sModuleInfo, 'screenshot saved as: "%s"' % path, 1)


    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to sleep for a particular duration
def Sleep(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if ((len(step_data) != 1)):
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
            return "failed"
        else:
            tuple = step_data[0]
            seconds = int(tuple[2])
            CommonUtil.ExecLog(sModuleInfo, "Sleeping for %s seconds" % seconds, 1)
            time.sleep(seconds)
            return "passed"
            # return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to save text
def Save_Text(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if( step_data[0][1] == 'value'):
            result = Shared_Resources.Set_Shared_Variables(step_data[0][2],int(step_data[1][2]))  # setting the shared variables
        else:
            result = Shared_Resources.Set_Shared_Variables(step_data[0][2],step_data[1][2])  # setting the shared variables
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Value of Variable '%s' could not be saved!!!", 3)
            return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Showing saved variables", 1)
            Shared_Resources.Show_All_Shared_Variables()
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

# Method to download file
def Download_file(data_set):
    ''' Download file from URL '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    # Parse data set
    try:
        url = '' # Mandatory
        file_location = '' # Optional - default will be used if omited
        shared_var = '' # Optional
        
        for row in data_set:
            op = row[0].strip().lower()
            if op == 'url':
                url = row[2].strip()
            elif op in ('folder', 'location', 'directory'):
                file_location = row[2].strip()
            elif op in ('shared variable', 'shared var', 'variable', 'var', 'save'):
                shared_var = row[2].strip()
        
        # Verify input
        if file_location == '': file_location = os.path.join(get_home_folder(), 'Downloads') # if no location is given, set default to Downloads directory
        if url == '': # Make sure we have a URL
            CommonUtil.ExecLog(sModuleInfo,"Expected Field to contain 'url' and Value to contain a valid URL to a file", 3)
            return 'failed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    try:
        # Download file and get path/filename
        file_name = download_file_using_url(url, file_location)
        
        # Verify download
        if file_name in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Failed to save file from (%s) to disk (%s)" % (url, file_location), 3)
            return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "File downloaded successfully to %s" % file_name, 1)
            if shared_var: Shared_Resources.Set_Shared_Variables(shared_var, file_name) # Store path/file in shared variables if variable name was set by user
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error downloading file")

# Method to download file and unzip
def Download_File_and_Unzip(data_set):
    ''' Download file and unzip to specified path '''

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    
    # Parse data set
    try:
        url = '' # Mandatory
        unzip_location = '' # Optional - default will be used if omited
        shared_var = '' # Optional
        file_location = os.path.join(get_home_folder(), 'Downloads') # Set location of download to Downloads directory
        
        for row in data_set:
            op = row[0].strip().lower()
            if op == 'url':
                url = row[2].strip()
            elif op in ('folder', 'location', 'directory'):
                unzip_location = row[2].strip()
            elif op in ('shared variable', 'shared var', 'variable', 'var', 'save'):
                shared_var = row[2].strip()
        
        # Verify input
        
        if url == '': # Make sure we have a URL
            CommonUtil.ExecLog(sModuleInfo,"Expected Field to contain 'url' and Value to contain a valid URL to a file", 3)
            return 'failed'
        if unzip_location == '': unzip_location = file_location # Set unzip location to Downloads by default if omited 
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    # Download
    try:
        # Download file and get path/filename
        file_name = download_file_using_url(url, file_location)
        
        # Verify download
        if file_name in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Failed to save file from (%s) to disk (%s)" % (url, file_location), 3)
            return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "File downloaded successfully to %s" % file_name, 1)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error downloading file")
    
    # Unzip
    try:
        result = UnZip(file_name, unzip_location)
        
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Failed to unzip %s to %s" % (file_name, unzip_location), 3)
            return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"Successfully unzipped to %s" % unzip_location,1)
            if shared_var: Shared_Resources.Set_Shared_Variables(shared_var, unzip_location) # Store path in shared variables if variable name was set by user
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error unzipping file")


def replace_Substring(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

    # Recall file attachment, if not already set
    file_attachment = []
    if Shared_Resources.Test_Shared_Variables('file_attachment'):
        file_attachment = Shared_Resources.Get_Shared_Variables('file_attachment')

    # Parse data set
    try:
        substring = ''
        new_string = ''
        file_name = ''
        replace_all = True
        case_sensitive = True
        replace_dict = {}
        for row in data_set:
            if "action" in row[1]:
                file_name = row[2]
                if file_name[0]=="/": file_name=file_name.lstrip("/")
            if row[1] == 'element parameter':
                if row[0] == 'replace all':
                    #The user should be able to replace the first instance found, or all strings found (default is to replace all)
                    if row[2].lower().strip() == 'true' or row[2].lower().strip() == 'yes': #replace_all
                        replace_all = True
                    elif row[2].lower().strip() == 'false' or row[2].lower().strip() == 'no': #replace_first_one_only
                        replace_all = False
                    elif row[2]!='':
                        CommonUtil.ExecLog(sModuleInfo,"Unknown Value for element parameter 'replace_all'. Should be true or false.", 3)
                        return 'failed'

                elif row[0] == 'case sensitive':
                    #User should be able to specify case sensitivity (default is to be case sensitive)
                    if row[2].lower().strip() == 'true' or row[2].lower().strip() == 'yes':  #case_sensitive
                        case_sensitive = True
                    elif row[2].lower().strip() == 'false' or row[2].lower().strip() == 'no': #case_insensitive
                        case_sensitive = False
                    elif row[2]!='':
                        CommonUtil.ExecLog(sModuleInfo,"Unknown Value for element parameter 'case_sensitive'. Should be true or false.", 3)
                        return 'failed'

                elif row[0] == 'dictionary':
                    if row[2] != '':
                        try:
                            replace_dict = ast.literal_eval(row[2].strip())
                        except:
                            CommonUtil.ExecLog(sModuleInfo,"Unknown Value for element parameter 'dictionary'. Should be a string representation of python dictionary.", 3)
                            return 'failed'
                    else:
                        CommonUtil.ExecLog(sModuleInfo,"Unknown Value for element parameter 'dictionary'. Should be a string representation of python dictionary.",3)
                        return 'failed'
                else:
                    substring = row[0].strip()  #substring to be replaced
                    new_string = row[2].strip()  #substring should be replaced to this string
                    replace_dict = {substring:new_string}

         # Try to find the file
        if file_name not in file_attachment and os.path.exists(os.path.join(get_home_folder(), file_name)) == False:
            CommonUtil.ExecLog(sModuleInfo, "Could not find file attachment called %s, and could not find it locally" % file_name, 3)
            return 'failed'
        if file_name in file_attachment: file_name = file_attachment[file_name] # In file is an attachment, get the full path

        if file_name not in file_attachment:
            file_name = os.path.join(get_home_folder(), file_name)
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    # Perform action
    try:

        #read and change the file
        f = open(file_name, 'r')
        newTxt = str(f.read())
        f.close()

        for substring in replace_dict.keys():
            new_string = replace_dict[substring]
            if substring == '':
                CommonUtil.ExecLog(sModuleInfo, "Could not find substring for this action", 3)
                return 'failed'
            if new_string == '':
                CommonUtil.ExecLog(sModuleInfo, "Could not find new_string for this action", 3)
                return 'failed'
            if case_sensitive == False: #case insensitive
                newTxt = newTxt.lower()
                substring = substring.lower()
                new_string = new_string.lower()
            if replace_all == False: #replace only first one
                newTxt = newTxt.replace(substring, new_string, 1)
            if replace_all == True: #replace all
                newTxt =newTxt.replace(substring, new_string)

        #write back
        f = open(file_name, 'w')
        f.write(newTxt)
        f.close()
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())



def Change_Value_ini(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

    # Recall file attachment, if not already set
    file_attachment = []
    if Shared_Resources.Test_Shared_Variables('file_attachment'):
        file_attachment = Shared_Resources.Get_Shared_Variables('file_attachment')

    # Parse data set
    try:
        file_name = ''
        section_name = ''
        line_name = ''
        new_expected_value_of_line = ''
        for row in data_set:
            if "action" in row[1]:
                new_expected_value_of_line = row[2]    #previous value should be changed to this value
            if row[1] == 'path':
                file_name = row[2]    # name of the file where the change should be made
            if row[1] == 'value':
                section_name = row[0]   # name of the section where th change should be made
                line_name = row[2]    # name of the line where value should be changed

        # Try to find the file
        if file_name not in file_attachment and os.path.exists(os.path.join(get_home_folder(), file_name)) == False:
            CommonUtil.ExecLog(sModuleInfo, "Could not find file attachment called %s, and could not find it locally" % file_name, 3)
            return 'failed'
        if file_name in file_attachment: file_name = file_attachment[file_name] # In file is an attachment, get the full path

        if file_name not in file_attachment:
            file_name = os.path.join(get_home_folder(), file_name)

        if section_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find ini file section name for this action", 3)
            return 'failed'
        if line_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find ini file line name for this action", 3)
            return 'failed'
        if new_expected_value_of_line == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find new expected value for this action", 3)
            return 'failed'
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    # Perform action
    try:

        result = ConfigModule.add_config_value(section_name, line_name, new_expected_value_of_line, location = file_name)
        if result:
            CommonUtil.ExecLog(sModuleInfo, "INI upated successfully", 1)
            return 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Error updating %s with %s in section %s" % (line_name, new_expected_value_of_line, section_name), 3)
        return "failed"



    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error performing action")


def Add_line_ini(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

    # Recall file attachment, if not already set
    file_attachment = []
    if Shared_Resources.Test_Shared_Variables('file_attachment'):
        file_attachment = Shared_Resources.Get_Shared_Variables('file_attachment')

    # Parse data set
    try:
        file_name = ''
        section_name = ''
        line_name = ''
        value_of_line = ''
        for row in data_set:
            if "action" in row[1]:
                value_of_line = row[2]   # value of the new line
            if row[1] == 'path':
                file_name = row[2]         # name of the file where the change should be made
            if row[1] == 'value':
                section_name = row[0]       # name of the section where the new line should be added
                line_name = row[2]       # name of the new line to be added

        # Try to find the file
        if file_name not in file_attachment and os.path.exists(os.path.join(get_home_folder(), file_name)) == False:
            CommonUtil.ExecLog(sModuleInfo, "Could not find file attachment called %s, and could not find it locally" % file_name, 3)
            return 'failed'
        if file_name in file_attachment: file_name = file_attachment[file_name] # In file is an attachment, get the full path

        if file_name not in file_attachment:
            file_name = os.path.join(get_home_folder(), file_name)

        if section_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find ini file section name for this action", 3)
            return 'failed'
        if line_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find ini file line name for this action", 3)
            return 'failed'
        if value_of_line == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find new expected value for this action", 3)
            return 'failed'
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    # Perform action
    try:

        result = ConfigModule.add_config_value(section_name, line_name, value_of_line,location=file_name)
        if result:
            CommonUtil.ExecLog(sModuleInfo, "INI upated successfully", 1)
            return 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Error updating %s with %s in section %s" % (line_name, value_of_line, section_name), 3)
        return "failed"



    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Delete_line_ini(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

    # Recall file attachment, if not already set
    file_attachment = []
    if Shared_Resources.Test_Shared_Variables('file_attachment'):
        file_attachment = Shared_Resources.Get_Shared_Variables('file_attachment')

    # Parse data set
    try:
        file_name = ''
        section_name = ''
        line_name = ''
        for row in data_set:
            if row[1] == 'path':
                file_name = row[2]   # name of the file where the change should be made
            if row[1] == 'value':
                section_name = row[0]    # name of the section from where line should be deleted
                line_name = row[2]    # name of the line to be deleted

        # Try to find the file
        if file_name not in file_attachment and os.path.exists(os.path.join(get_home_folder(), file_name)) == False:
            CommonUtil.ExecLog(sModuleInfo, "Could not find file attachment called %s, and could not find it locally" % file_name, 3)
            return 'failed'
        if file_name in file_attachment: file_name = file_attachment[file_name] # In file is an attachment, get the full path

        if file_name not in file_attachment:
            file_name = os.path.join(get_home_folder(), file_name)

        if section_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find ini file section name for this action", 3)
            return 'failed'
        if line_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find ini file line name for this action", 3)
            return 'failed'
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    # Perform action
    try:

        result = ConfigModule.remove_config_value(section_name, line_name,location=file_name)
        if result:
            CommonUtil.ExecLog(sModuleInfo, "INI upated successfully", 1)
            return 'passed'
        else:
            CommonUtil.ExecLog(sModuleInfo, "Error updating %s with %s in section %s" % (line_name, section_name), 3)
        return "failed"



    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Read_line_name_and_value(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    # Parse data set
    try:
        file_name = ''
        save_line_name_value = ''
        for row in data_set:
            if row[1] == 'path':
                file_name = row[2]    # name of the file from where line name and value should be read
            if "action" in row[1]:
                save_line_name_value = row[2]    #user will provide the vaiable to the save the line name and values


        if file_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find ini file name for this action", 3)
            return 'failed'
        if save_line_name_value == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find the name where to save line name and value in shared variables for this action", 3)
            return 'failed'
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")
    try:
        if os.path.isfile(file_name):    # check if the file exists or not
            Shared_Resources.Set_Shared_Variables(save_line_name_value, dir)
            return "passed"

        else:
            CommonUtil.ExecLog(sModuleInfo, "Couldn't find the config file", 1)
            return "failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# return only the path step data
def Get_Path_Step_Data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        element_step_data = []
        for each in step_data:
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


# return validated path data with path1 and path2
def Validate_Path_Step_Data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        path1 = get_home_folder() + str(step_data[0][0]).strip()
        path2 = get_home_folder() + str(step_data[0][2]).strip()
        validated_data = (path1, path2)
        return validated_data
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find the new page element requested.  Error: %s" % (Error_Detail), 3)
        return "failed"


# return no of files(sub directory included) in a directory
def count_no_of_files_in_folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        path = get_home_folder() + "/" +str(step_data[0][2]).strip()
        count = 0
        count = sum([len(files) for r, d, files in os.walk(path)])
        Shared_Resources.Set_Shared_Variables('noOfFiles',str(count))
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def pattern_matching(dataset):
    ''' Perform user provided regular expression on a string '''
    
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)

    # Parse dataset
    try:
        pattern = ''
        shared_var = ''
        strg = ''
        
        for row in dataset:
            if row[0].lower().strip() == 'pattern': # Regular expression pattern
                pattern = row[2].strip()
            elif row[0].lower().strip() == 'variable': # Shared variable to save any matches to
                shared_var = row[2].strip()
            elif row[0].lower().strip() == 'string': # String to search
                strg = row[2].strip()
    
        if pattern == '' or shared_var == '' or strg == '':
            return CommonUtil.Exception_Handler(sys.exc_info(), None, "Missing one of the inputs. Expected 3 element parameters: 'pattern', 'variable', and 'string'")
        
    except:
        CommonUtil.ExecLog(sModuleInfo, "Error parsing dataset", 3)
        
    try:
        p = re.compile(pattern, re.M)
        m = p.findall(strg)
        if m == [] or m == None:
            CommonUtil.ExecLog(sModuleInfo, "Pattern did not produce a match", 3)
            return 'failed'
        else:
            Shared_Resources.Set_Shared_Variables(shared_var, m[0]) # !!! Idealy would save the entire list, but we need a way to access a single element
            CommonUtil.ExecLog(sModuleInfo, "Pattern matched: %s - Saved to Shared variable: %s" % (str(m[0]), shared_var), 1)
            return 'passed'
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error performing pattern match")


def save_substring(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    # Parse data set
    try:
        from_var = '' #the varibale from which string will be copied
        to_var = '' #the variable wher estring will be saved
        index_string = '' #index of the substring operation like '5'-> will copy from index 5 to last of string, '5,8' -> will copy from index 5 to index before 8, which is 7, likeany programming language
        substring = ''
        from_index = -1
        to_index = -1
        for row in data_set:
            if row[1] == 'element parameter':
                if row[0] == 'from':
                    from_var = str(row[2])
                elif row[0] == 'to':
                    to_var = str(row[2])
            elif row[1] == 'action':
                index_string = str(row[2])

        if Shared_Resources.Test_Shared_Variables(from_var):
            from_var = Shared_Resources.Get_Shared_Variables(from_var) #save the value of 'from_var' shared varibale to 'from_var'
        else:
            CommonUtil.ExecLog(sModuleInfo,"Could not find the variable named '%s'"%from_var, 3)
            return "failed"

        #process index_string
        if "," in index_string:
            splitted = index_string.split(",")
            from_index = int(splitted[0].strip())
            to_index = int(splitted[1].strip())
        else:
            from_index = int(index_string.strip())

        if from_index == -1:
            CommonUtil.ExecLog(sModuleInfo, "From Index for getting substing can't be negative", 3)
            return "failed"
        else:
            if to_index == -1:
                try:
                    substring = from_var[from_index:]
                except:
                    CommonUtil.ExecLog(sModuleInfo, "Can't get substring.Index out of range for string '%s'" % from_var, 3)
                    return "failed"
            else:
                try:
                    substring = from_var[from_index:to_index]
                except:
                    CommonUtil.ExecLog(sModuleInfo, "Can't get substring. Index out of range for string '%s'" % from_var, 3)
                    return "failed"

        #now save the substing to new variable
        return Shared_Resources.Set_Shared_Variables(to_var,substring)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())
'''
extracts number from a string, suppose a string is "hi123 4.5 -6hola", It will get all the numbers in a list ['123','4.5','-6'].. then if index is specified for example 2,
then it will return 2nd element of the list which is '4.5'. If no index is specified default index 1 will be applied. It will return the 1st element which is 123
It converts that number to be formatted a specified way if round is defined

Original value of the variable: 246.789

eg. If round is 1  -  output = 247
    If round is 10     -  output = 250
    If round is 100    -  output = 200

    If round is 0.1     -  output = 246.8
    If round is 0.01    -  output = 246.79
    If round is 0.001   -  output = 246.789
    If round is 0.0001  -  output = 246.789
    If round is 0.00001  -  output = 246.789
This function saves the variable to a defined variable(not the source variable)

'''
def extract_number(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    # Parse data set
    try:
        from_var = '' #the varibale from which string will be copied
        to_var = '' #the variable wher estring will be saved
        index = 0 #index of the digit for a string "hello123 2.5 67" if index is 2(starting from 1) we will get 2.5
        rounded_number=''
        digit = 1
        extracted_number = ''
        for row in data_set:
            if row[1] == 'element parameter':
                if row[0] == 'from':
                    from_var = str(row[2])
                elif row[0] == 'to':
                    to_var = str(row[2])
                elif row[0] == 'index':
                    index = int(row[2])
                elif row[0] == 'round':
                    digit = str(row[2])

        if Shared_Resources.Test_Shared_Variables(from_var):
            from_var = Shared_Resources.Get_Shared_Variables(from_var) #save the value of 'from_var' shared varibale to 'from_var'
        else:
            CommonUtil.ExecLog(sModuleInfo,"Could not find the variable named '%s'"%from_var, 3)
            return "failed"

        if index < 0:
            CommonUtil.ExecLog(sModuleInfo, "Index for extracting number can't be negative", 3)
            return "failed"
        else:
            try:
                all_digit = [s for s in re.findall(r'-?\d+\.?\d*', from_var)]
                extracted_number = all_digit[index-1]

                if re.match("-?\d+?\.\d+?$", digit) is None:
                    digit = int(digit)
                else:
                    digit = float(digit)

                if re.match("-?\d+?\.\d+?$", extracted_number) is None:
                    extracted_number = int(extracted_number)
                else:
                    extracted_number = float(extracted_number)

                if digit >= 1:
                    rounded_number = int((round(float(extracted_number) / digit))) * digit
                else:
                    c = 0
                    for i in range(1, 20):
                        digit *= 10
                        c += 1
                        if int(digit) == 1:
                            break
                    if digit != 1:
                        CommonUtil.ExecLog(sModuleInfo, "Can't round number. Incorrect digit '%s' given" % digit, 3)
                        return "failed"
                    rounded_number = round(float(extracted_number), c)
            except:
                CommonUtil.ExecLog(sModuleInfo, "Can't extract digit. Index out of range for string '%s'" % from_var, 3)
                return "failed"

        #now save the substing to new variable
        return Shared_Resources.Set_Shared_Variables(to_var,rounded_number)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())