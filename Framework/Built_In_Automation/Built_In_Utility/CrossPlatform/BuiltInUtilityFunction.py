# -*- coding: cp1252 -*-
'''
Created on May 15, 2016

@author: Built_In_Automation Solutionz Inc.
'''

import sys
import datetime

sys.path.append("..")
import time
import inspect
import zipfile
import string
import ConfigParser
from Framework.Utilities import ConfigModule
import filecmp
import random
import requests
from Framework.Utilities import CommonUtil
from sys import platform as _platform
from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list, skipped_tag_list

from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources
import os, subprocess, shutil

add_sanitization = True


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
        CommonUtil.ExecLog(sModuleInfo, "Create Folder %s" % folderPath, 1)
        if os.path.isdir(folderPath):
            if forced == False:
                # print "folder already exists"
                CommonUtil.ExecLog(sModuleInfo, "Folder already exists", 1)
                return "passed"
            DeleteFolder(folderPath)
        os.makedirs(folderPath)
        # after performing os.makedirs() we have to check that if the folder with new name exists in correct location.
        # if the folder exists in correct position then return passed
        # if the folder doesn't exist in correct position then return failed
        if os.path.isdir(folderPath):
            CommonUtil.ExecLog(sModuleInfo, "folder exists... create folder function is done properly", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "file doesn't exist... create folder function is not done properly", 3)
            return "failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# function to create a file
def CreateFile(sFilePath):
    """

        :param sFilePath: file path to be created
        :param forced: if true remove the folder first, if false won't remove the folder if there exists one with same name
        :return: Exception if Exception occurs or True if successful or False if file already exists
        """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Create File %s" % sFilePath, 1)
        if os.path.isfile(sFilePath):
            CommonUtil.ExecLog(sModuleInfo, "File already exists", 1)
            # print "File already exists"
            return False
        else:
            # print "Creating new file"
            CommonUtil.ExecLog(sModuleInfo, "Creating new file", 1)
            newfile = open(sFilePath, 'w')
            newfile.close()
            CommonUtil.ExecLog(sModuleInfo, "Creating file %s is complete" % sFilePath, 1)
            return newfile
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# function to rename file a to b
def RenameFile(file_to_be_renamed, new_name_of_the_file):
    """

        :param file_to_be_renamed: location of source file to be renamed
        :param new_name_of_the_file: location of destination file
        :return: Exception if Exception occurs otherwise return result  
        """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Renaming file %s to %s" % (file_to_be_renamed, new_name_of_the_file), 0)
        shutil.move(file_to_be_renamed, new_name_of_the_file)
        # after performing shutil.move() we have to check that if the file with new name exists in correct location.
        # if the file exists in correct position then return passed
        # if the file doesn't exist in correct position then return failed
        if os.path.isfile(new_name_of_the_file):

            CommonUtil.ExecLog(sModuleInfo, "file exists... rename function is done properly", 0)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "file doesn't exist... rename function is not done properly", 3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


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
            CommonUtil.ExecLog(sModuleInfo, "file exists... move function is done properly", 0)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "file doesn't exist... move function is not done properly", 3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# function to rename folder a to b
def RenameFolder(folder_to_be_renamed, new_name_of_the_folder):
    """

        :param folder_to_be_renamed: location of source folder to be renamed
        :param new_name_of_the_folder: full location of destination folder
        :return: Exception if Exception occurs otherwise return result  
        """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Renaming folder %s to %s" % (folder_to_be_renamed, new_name_of_the_folder), 0)
        shutil.move(folder_to_be_renamed, new_name_of_the_folder)
        # after performing shutil.move() we have to check that if the folder with new name exists in correct location.
        # if the folder exists in correct position then return passed
        # if the folder doesn't exist in correct position then return failed
        if os.path.isdir(new_name_of_the_folder):
            CommonUtil.ExecLog(sModuleInfo, "folder exists... rename function is done properly", 0)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "folder doesn't exist... rename function is not done properly", 3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


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
        CommonUtil.ExecLog(sModuleInfo, "Moving folder %s to %s" % (folder_to_be_moved, new_name_of_the_folder), 0)
        shutil.move(folder_to_be_moved, new_name_of_the_folder)
        # after performing shutil.move() we have to check that if the folder with new name exists in correct location.
        # if the folder exists in correct position then return passed
        # if the folder doesn't exist in correct position then return failed
        if os.path.isdir(new_name_of_the_folder):
            CommonUtil.ExecLog(sModuleInfo, "folder exists... move function is done properly", 0)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "folder doesn't exist... move function is not done properly", 3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


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
        if os.path.isfile(file_to_be_unzipped):
            zip_ref = zipfile.ZipFile(file_to_be_unzipped, 'r')
            zip_ref.extractall(location_where_to_unzip)
            result = zip_ref.close()
            return result
        else:
            CommonUtil.ExecLog(sModuleInfo, "can't unzip file as it doesn't exist", 3)
            return "failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


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
        CommonUtil.ExecLog(sModuleInfo, "Comparing files %s and %s" % (file_to_be_compared1, file_to_be_compared2), 1)
        result = filecmp.cmp(file_to_be_compared1, file_to_be_compared2)
        return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# function to zip a file for linux
def ZipFile(file_to_be_zipped, location_where_to_zip):
    """

        :param file_to_be_zipped: location of source file to be zipped
        :param location_where_to_zip: location of destination 
        :return: Exception if Exception occurs or false file doesn't exist otherwise return result  
        """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Zipping file %s to %s" % (file_to_be_zipped, location_where_to_zip), 0)

        if os.path.isfile(file_to_be_zipped):

            list1 = file_to_be_zipped.split('/')
            list2 = location_where_to_zip.split('/')
            value = file_to_be_zipped[:len(file_to_be_zipped) - len(list1[len(list1) - 1])]
            os.chdir(value)
            zipfile.ZipFile(list2[len(list2) - 1], mode='w').write(list1[len(list1) - 1])
            # after performing zipfile() we have to check that if the file with new name exists in correct location.
            # if the file exists in correct position then return passed
            # if the file doesn't exist in correct position then return failed
            if os.path.isfile(location_where_to_zip):
                CommonUtil.ExecLog(sModuleInfo, "file exists... zip function is done properly", 0)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "file doesn't exist... zip function is not done properly", 3)
                return "failed"

        else:
            CommonUtil.ExecLog(sModuleInfo, "can't zip file as file doesn't exist", 3)
            return False
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# function to zip file for windows
def ZipFile_for_windows(file_to_be_zipped, location_where_to_zip):
    """

        :param file_to_be_zipped: location of source file to be zipped
        :param location_where_to_zip: location of destination 
        :return: Exception if Exception occurs or false if file doesn't exist otherwise return result  
        """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Zipping file %s to %s" % (file_to_be_zipped, location_where_to_zip), 0)
        if os.path.isfile(file_to_be_zipped):
            list1 = file_to_be_zipped.split('\\')
            list2 = location_where_to_zip.split('\\')
            value = file_to_be_zipped[:len(file_to_be_zipped) - len(list1[len(list1) - 1])]
            os.chdir(value)
            result = zipfile.ZipFile(list2[len(list2) - 1], mode='w').write(list1[len(list1) - 1])
            CommonUtil.ExecLog(sModuleInfo,"Zipping file %s to %s is complete" % (file_to_be_zipped, location_where_to_zip), 0)
            return result
        else:
            CommonUtil.ExecLog(sModuleInfo, "can't zip file for windows as file doesn't exist", 3)
            return False
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# funtion zip a folder
def ZipFolder(dir_to_be_zipped, location_where_to_zip):
    """
    Zips a given folder, its sub folders and files. Ignores any empty folders
    dir is the path of the folder to be zipped
    zip_file is the path of the zip file to be created


        :param dir_to_be_zipped: location of source folder to be zipped
        :param location_where_to_zip: location of destination 
        :return: Exception if Exception occurs or false if folder doesn't exist otherwise return result  
            """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:

        CommonUtil.ExecLog(sModuleInfo, "Zipping folder %s to %s" % (dir_to_be_zipped, location_where_to_zip), 1)
        if os.path.exists(dir_to_be_zipped):
            zip = zipfile.ZipFile(location_where_to_zip, 'w', compression=zipfile.ZIP_DEFLATED)
            root_len = len(os.path.abspath(dir_to_be_zipped))

            for root, dirs, files in os.walk(dir_to_be_zipped):
                archive_root = os.path.abspath(root)[root_len:]
                for f in files:
                    fullpath = os.path.join(root, f)
                    archive_name = os.path.join(archive_root, f)
                    # print f
                    if f not in location_where_to_zip:
                        zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)

            zip.close()
            # after performing zip.close() we have to check that if the file with new name exists in correct location.
            # if the file exists in correct position then return passed
            # if the file doesn't exist in correct position then return failed
            if os.path.isfile(location_where_to_zip):
                CommonUtil.ExecLog(sModuleInfo, "file exists... zip function is done properly", 0)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "file doesn't exist... zip function is not done properly", 3)
                return "failed"

        else:
            CommonUtil.ExecLog(sModuleInfo, "can't zip folder as folder doesn't exist", 3)
            return False

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


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
def DeleteFolder(sFolderPath):
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
def find(sFilePath):
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
def empty_trash(trash_path):
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
        if len(sys.argv) >= 2:
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
def copy_file(src, dest):
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


def run_win_cmd(cmd):
    """

                :param cmd: admin command to run
                :return: Exception if Exception occurs 
                    """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        result = []
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in process.stdout:
            result.append(line)
        errcode = process.returncode
        for line in result:
            # print(line)
            CommonUtil.ExecLog(sModuleInfo, "%s" % line, 1)
        if errcode is not None:
            CommonUtil.ExecLog(sModuleInfo, 'cmd %s failed, see above for details' % cmd, 3)
            raise Exception('cmd %s failed, see above for details', cmd)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def run_cmd(command, return_status=False, is_shell=True, stdout_val=subprocess.PIPE, local_run=False):
    """

                    :param command: sudo command to run
                    :return: Exception if Exception occurs otherwise return result 
                        """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    '''Begin Constants'''
    Passed = "Passed"
    Failed = "Failed"
    Running = 'running'
    '''End Constants'''

    # Run 'command' via command line in a bash shell, and store outputs to stdout_val
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    subprocess_dict = {}
    try:
        # global subprocess_dict
        result = []

        # open a subprocess with command, and assign a session id to the shell process
        # this is will make the shell process the group leader for all the child processes spawning from it
        status = subprocess.Popen(command, shell=is_shell, stdout=stdout_val, preexec_fn=os.setsid)
        subprocess_dict[status] = Running
        status.wait() # Wait for process to complete, and populate returncode
        errcode = status.returncode
        
        for line in status.stdout:
            result.append(line)
        
        for line in result:
            CommonUtil.ExecLog(sModuleInfo, "%s" % line, 1)
        
        if return_status:
            return errcode, result
        elif errcode == 0:
            return Passed
        else:
            return Failed

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# function to generate random string
def random_string_generator(pattern='nluc', size=10):
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
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        ''' Setting stream parameter to True will cause the download of response headers only and the connection remains open.
          This avoids reading the content all at once into memory for large responses.
         A fixed chunk will be loaded each time while r.iter_content is iterated.'''
        r = requests.get(file_url, stream=True)

        list_the_parts_of_url = file_url.split("/") #get file name from the url

        file_name = os.path.join(location_of_file , list_the_parts_of_url[len(list_the_parts_of_url) - 1]) #complete file location

        with open(file_name, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):

            # writing one chunk at a time to pdf file
                if chunk:
                    f.write(chunk)
        # after performing the download operation we have to check that if the file with new name exists in correct location.
        # if the file exists in correct position then return passed
        # if the file doesn't exist in correct position then return failed
        if os.path.isfile(file_name):
            CommonUtil.ExecLog(sModuleInfo, "file exists... downloading file using url function is done properly", 1)
            Shared_Resources.Set_Shared_Variables("downloaded_file", file_name)
            Shared_Resources.Show_All_Shared_Variables()
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "file doesn't exist... downloading file using url function is not done properly", 3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

#Method to download and unzip file
def download_and_unzip_file(file_url, location_of_file):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        ''' Setting stream parameter to True will cause the download of response headers only and the connection remains open.
          This avoids reading the content all at once into memory for large responses.
         A fixed chunk will be loaded each time while r.iter_content is iterated.'''
        r = requests.get(file_url, stream=True)

        list_the_parts_of_url = file_url.split("/") #get file name from the url
        file_name = os.path.join(location_of_file, list_the_parts_of_url[len(list_the_parts_of_url) - 1])
        actual_file_name = list_the_parts_of_url[len(list_the_parts_of_url) - 1]
        with open(file_name, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):

            # writing one chunk at a time to pdf file
                if chunk:
                    f.write(chunk)
        # after performing the download operation we have to check that if the file with new name exists in correct location.
        # if the file exists in correct position then return passed
        # if the file doesn't exist in correct position then return failed
        if os.path.isfile(file_name):
            CommonUtil.ExecLog(sModuleInfo, "file exists... downloading file using url function is done properly", 0)
        else:
            CommonUtil.ExecLog(sModuleInfo, "file doesn't exist... downloading file using url function is not done properly", 3)
            return "failed"
        unzip_location = os.path.join(location_of_file,"latest_directory" )
        CommonUtil.ExecLog(sModuleInfo, "Creating the directory '%s' " % unzip_location, 0)
        result1 = CreateFolder(unzip_location)
        if result1 in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Can't not create folder '%s' " % unzip_location, 3)
            return "failed"
        CommonUtil.ExecLog(sModuleInfo, "Folder '%s' is created " % unzip_location, 1)
        result = UnZip(file_name,unzip_location)
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Can't not unzip file '%s' to '%s'" % (file_name, unzip_location), 3)
            return "failed"
        CommonUtil.ExecLog(sModuleInfo, "Unzipping file '%s' to '%s' is complete" % (file_name, unzip_location), 0)
        CommonUtil.ExecLog(sModuleInfo, "Saving directory location to shared resources" , 1)
        #Shared_Resources.Set_Shared_Variables("latest_directory", unzip_location)
        downloaded_file = os.path.join(unzip_location,actual_file_name )
        Shared_Resources.Set_Shared_Variables("downloaded_file", downloaded_file)
        Shared_Resources.Show_All_Shared_Variables()
        return "passed"


    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


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


# code to generate raw string
def raw(text):
    """Returns a raw string representation of text"""
    new_string = ''
    for char in text:
        try:
            new_string += escape_dict[char]
        except KeyError:
            new_string += char
    return new_string


'============================= Raw String Generation Ends=============================='

'============================= Sequential Action Section Begins=============================='


# Method to copy file/folder
def Copy_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
            from_path = get_home_folder() + str(step_data[0][2]).strip()  # location of the file/folder to be copied
            to_path = get_home_folder() + str(step_data[1][2]).strip()  # location where to copy the file/folder
        elif _platform == "win32":
            from_path = raw(str(step_data[0][2]).strip())  # location of the file/folder to be copied
            to_path = raw(str(step_data[1][2]).strip())  # location where to copy the file/folder
        file_or_folder = str(step_data[2][2]).strip()  # get if it is file/folder to copy
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
        if _platform == "linux" or _platform == "linux2":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            path = get_home_folder() + str(step_data[0][2]).strip()  # path of the file/folder to be created
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
        elif _platform == "win32":
            # windows
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
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
                CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
                return 'failed'
        elif _platform == "darwin":
            # mac
            CommonUtil.ExecLog(sModuleInfo, "mac", 1)
            path = get_home_folder() + str(step_data[0][2]).strip()  # path of the file/folder to be created
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
def Run_Command(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if step_data[0][0] == "run command":
            if _platform == "win32":
                # windows
                command = str(step_data[0][2]).strip()
                result = run_win_cmd(command)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Could not run sudo command '%s'" % (command), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "sudo command is run properly '%s'" % (command), 1)
                    return "passed"
            elif _platform == "linux" or _platform == "linux2" or _platform == "darwin":

                CommonUtil.ExecLog(sModuleInfo, "Could not run admin command for linux/mac", 3)
                return "failed"
        elif step_data[0][0] == "run sudo":
            if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
                command = str(step_data[0][2]).strip()
                result = run_cmd(command)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Could not run sudo command '%s'" % (command), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "sudo command is run properly '%s'" % (command), 1)
                    return "passed"
            elif _platform == "win32":
                # windows
                CommonUtil.ExecLog(sModuleInfo, "Could not run sudo command as it is windows", 3)
                return "failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


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
def Create_File(step_data):
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
    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
            from_path = get_home_folder() + str(step_data[0][2]).strip()  # location of file path to be compared
            to_path = get_home_folder() + str(step_data[1][2]).strip()  # location of file path to be compared
        elif _platform == "win32":
            from_path = raw(str(step_data[0][2]).strip())  # location of file path to be compared
            # print  from_path
            to_path = raw(str(step_data[1][2]).strip())  # location of file path to be compared

        file_or_folder = str(step_data[2][2]).strip()
        if file_or_folder.lower() == 'file':
            # compare file "from_path" and "to_path"
            result = CompareFile(from_path, to_path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Files %s and %s are not equal '%s'" % (to_path, from_path), 3)
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
def Zip_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
            from_path = get_home_folder() + str(step_data[0][2]).strip()  # location of the file/folder to be zipped
            to_path = get_home_folder() + str(step_data[1][2]).strip()  # location where to zip the file/folder
            file_or_folder = str(step_data[2][2]).strip()  # get if it is file/folder to zip
            if file_or_folder.lower() == 'file':
                result = ZipFile(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Can't not zip file '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "File '%s' zipped to '%s' successfully" % (from_path, to_path), 1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
                result = ZipFolder(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Can't not zip folder '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Folder '%s' zipped to '%s' successfully" % (from_path, to_path), 1)
                    return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.", 3)
                return 'failed'
        elif _platform == "win32":
            # windows
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            from_path = raw(str(step_data[0][2]).strip())  # location of the file/folder to be zipped
            to_path = raw(str(step_data[1][2]).strip())  # location where to zip the file/folder
            file_or_folder = str(step_data[2][2]).strip()  # get if it is file/folder to zip
            if file_or_folder.lower() == 'file':
                result = ZipFile_for_windows(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Can't not zip file '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "File '%s' zipped to '%s' successfully" % (from_path, to_path), 1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
                result = ZipFolder(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Could not zip folder '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Folder '%s' zipped to '%s' successfully" % (from_path, to_path), 1)
                    return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
                return 'failed'

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to unzip
def Unzip_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            from_path = get_home_folder() + str(step_data[0][2]).strip()  # location of the file/folder to be unzipped
            to_path = get_home_folder() + str(step_data[1][2]).strip()  # location where to unzip the file/folder
        elif _platform == "win32":
            from_path = raw(str(step_data[0][2]).strip())  # location of the file/folder to be unzipped
            to_path = raw(str(step_data[1][2]).strip())  # location where to unzip the file/folder

        result = UnZip(from_path, to_path)
        if result in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Can't not unzip '%s' to '%s'" % (from_path, to_path), 3)
            return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "'%s' is unzipped to '%s' successfully" % (from_path, to_path), 1)
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to move file/folder
def Move_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
            from_path = get_home_folder() + str(step_data[0][2]).strip()  # location of the file/folder to be moved
            to_path = get_home_folder() + str(step_data[1][2]).strip()  # location where to move the file/folder
        elif _platform == "win32":
            from_path = raw(str(step_data[0][2]).strip())  # location of the file/folder to be moved
            to_path = raw(str(step_data[1][2]).strip())  # location where to move the file/folder
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

            result = copy_file(from_path, to_path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Could not copy file '%s' to the log uploader '%s'" % (from_path, to_path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"File '%s' copied to the log uploader '%s' successfully" % (from_path, to_path), 1)
                return "passed"
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
def Download_file(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        url = str(step_data[0][2]).strip()  # url to be downloaded
        file_location = str(step_data[1][2]).strip()  # location where to download the file/folder
        if file_location == "":
            # if no location is given
            file_location = os.path.join(get_home_folder(), 'Downloads')  # download to the Downloads folder
            result = download_file_using_url(url, file_location)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Download from url '%s' to location '%s' is not done" % (url, file_location), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"Download from url '%s' to location '%s' is done" % (url, file_location), 1)
                return "passed"
        else:
            # if location to download is given
            file_location = os.path.join(get_home_folder(), file_location)
            result = download_file_using_url(url, file_location)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Download from url '%s' to location '%s' is not done" % (url, file_location), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"Download from url '%s' to location '%s' is not done" % (url, file_location),1)
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

# Method to download file and unzip
def Download_File_and_Unzip(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
    try:
        url = str(step_data[0][2]).strip()  # url to be downloaded
        file_location = str(step_data[1][2]).strip()  # location where to download the file/folder
        if file_location == "":
            # if no location is given
            file_location = os.path.join(get_home_folder(), 'Downloads')  # download to the Downloads folder
            result = download_and_unzip_file(url, file_location)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Downloading from url '%s' to location '%s' and unzipping is not done" % (url, file_location), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"Download from url '%s' to location '%s' and unzipping is done" % (url, file_location),1)
                return "passed"
        else:
            # if location to download is given
            file_location = os.path.join(get_home_folder(), file_location)
            result = download_and_unzip_file(url, file_location)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Download from url '%s' to location '%s' and unzipping is not done" % (url, file_location), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"Download from url '%s' to location '%s' and unzipping is done" % (url, file_location),1)
                return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Change_Value_ini(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
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

        if file_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find ini file name for this action", 3)
            return 'failed'
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
        if os.path.isfile(file_name): # check if the file exists or not
            '''change the value'''
            config = ConfigParser.SafeConfigParser()
            config.read(file_name)
            list_of_sections = config.sections()
            if section_name in list_of_sections:
                options = config.options(section_name)
                # check if this name exists
                if line_name in options:
                    config.set(section_name, line_name, new_expected_value_of_line)  # change value
                    #writeback file
                    with open(file_name, 'wb') as configfile:
                        config.write(configfile)

                    '''check if line is changed properly'''
                    config.read(file_name)
                    check_value = config.get(section_name, line_name)
                    if check_value == new_expected_value_of_line:
                        CommonUtil.ExecLog(sModuleInfo, "Value is changed successfully", 1)
                        return "passed"

            CommonUtil.ExecLog(sModuleInfo, "Can't add line", 3)
            return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Couldn't find the config file", 1)
            return "failed"


    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def Add_line_ini(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
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

        if file_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find ini file name for this action", 3)
            return 'failed'
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
        if os.path.isfile(file_name):    # check if the file exists or not
            '''add line'''
            config = ConfigParser.SafeConfigParser()
            config.read(file_name)
            list_of_sections = config.sections()
            if section_name in list_of_sections:
                config.set(section_name, line_name, value_of_line)  #add line
                # writeback file
                with open(file_name, 'wb') as configfile:
                    config.write(configfile)

                '''check if line is added properly'''
                config.read(file_name)
                options = config.options(section_name)
                if line_name in options:
                    check_value = config.get(section_name, line_name)
                    if check_value == value_of_line:
                        CommonUtil.ExecLog(sModuleInfo,"Line is added successfully" ,1)
                        return "passed"

            CommonUtil.ExecLog(sModuleInfo, "Can't add line", 3)
            return "failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Couldn't find the config file", 1)
            return "failed"


    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def Delete_line_ini(data_set):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function start", 0)
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

        if file_name == '':
            CommonUtil.ExecLog(sModuleInfo, "Could not find ini file name for this action", 3)
            return 'failed'
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
        if os.path.isfile(file_name):   # check if the file exists or not
            '''delete the line'''
            config = ConfigParser.SafeConfigParser()
            config.read(file_name)
            config.remove_option(section_name, line_name)   #delete file
            # writeback file
            with open(file_name, 'wb') as configfile:
                config.write(configfile)

            '''check if the line is deleted properly'''
            config.read(file_name)
            options = config.options(section_name)
            if line_name in options:
                CommonUtil.ExecLog(sModuleInfo, "Can't delete line", 3)
                return "failed"

            CommonUtil.ExecLog(sModuleInfo, "The line is no more in the config file", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Couldn't find the config file", 1)
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
            '''read file and save'''
            config = ConfigParser.SafeConfigParser()
            config.read(file_name)
            list_of_sections = config.sections()
            dir ={}
            for section in list_of_sections:
                options = config.options(section)
                for option in options:
                    dir[section+"|"+option] = config.get(section,option)
            #save in shared variable
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



