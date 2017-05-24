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

import filecmp
import random
from Framework.Utilities import CommonUtil
from sys import platform as _platform

passed_tag_list = ['Pass', 'pass', 'PASS', 'PASSED', 'Passed', 'passed', 'true', 'TRUE', 'True', '1', 'Success','success', 'SUCCESS', True]
failed_tag_list = ['Fail', 'fail', 'FAIL', 'Failed', 'failed', 'FAILED', 'false', 'False', 'FALSE', '0', False]

import os, subprocess, shutil

add_sanitization = True


# funtion to get the path of home folder in linux
def get_home_folder():
    """

    :return: give the path of home folder
    """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get Home Folder", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Returning the path of home folder", 1)
        return os.path.expanduser("~")
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Create Folder", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Create Folder %s" % folderPath, 1)
        if os.path.isdir(folderPath):
            if forced == False:
                #print "folder already exists"
                CommonUtil.ExecLog(sModuleInfo, "Folder already exists", 1)
                return True
            DeleteFolder(folderPath)
        os.makedirs(folderPath)
        CommonUtil.ExecLog(sModuleInfo, "Creating folder %s is complete" % folderPath, 1)
        return True
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Create File", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Create File %s" % sFilePath, 1)
        if os.path.isfile(sFilePath):
            CommonUtil.ExecLog(sModuleInfo, "File already exists", 1)
            #print "File already exists"
            return False
        else:
            #print "Creating new file"
            CommonUtil.ExecLog(sModuleInfo, "Creating new file", 1)
            newfile = open(sFilePath, 'w')
            newfile.close()
            CommonUtil.ExecLog(sModuleInfo, "Returning result of create file function", 1)
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Rename File", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Renaming file %s to %s" % (file_to_be_renamed, new_name_of_the_file), 1)
        shutil.move(file_to_be_renamed, new_name_of_the_file)
        CommonUtil.ExecLog(sModuleInfo, "Checking whether file is renamed properly", 1)
        # after performing shutil.move() we have to check that if the file with new name exists in correct location.
        # if the file exists in correct position then return passed
        # if the file doesn't exist in correct position then return failed
        if os.path.isfile(new_name_of_the_file):
            CommonUtil.ExecLog(sModuleInfo, "Returning result of rename file function", 1)
            CommonUtil.ExecLog(sModuleInfo, "file exists... rename function is done properly", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Returning result of rename file function", 1)
            CommonUtil.ExecLog(sModuleInfo, "file doesn't exist... rename function is not done properly", 3)
            return "failed"
        CommonUtil.ExecLog(sModuleInfo, "Renaming file %s to %s complete" % (file_to_be_renamed, new_name_of_the_file),1)

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
    CommonUtil.ExecLog(sModuleInfo, "Function: Move File", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Moving file %s to %s" % (file_to_be_moved, new_name_of_the_file), 1)
        shutil.move(file_to_be_moved, new_name_of_the_file)
        CommonUtil.ExecLog(sModuleInfo, "Checking whether file is moved properly", 1)
        # after performing shutil.move() we have to check that if the file with new name exists in correct location.
        # if the file exists in correct position then return passed
        # if the file doesn't exist in correct position then return failed
        if os.path.isfile(new_name_of_the_file):
            CommonUtil.ExecLog(sModuleInfo, "Returning result of move file function", 1)
            CommonUtil.ExecLog(sModuleInfo, "file exists... move function is done properly", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Returning result of move file function", 1)
            CommonUtil.ExecLog(sModuleInfo, "file doesn't exist... move function is not done properly", 3)
            return "failed"
        CommonUtil.ExecLog(sModuleInfo, "Moving file %s to %s complete" % (file_to_be_renamed, new_name_of_the_file),1)

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
    CommonUtil.ExecLog(sModuleInfo, "Function: Rename Folder", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Renaming folder %s to %s" % (folder_to_be_renamed, new_name_of_the_folder), 1)
        shutil.move(folder_to_be_renamed, new_name_of_the_folder)
        CommonUtil.ExecLog(sModuleInfo, "Checking whether folder is renamed properly", 1)
        # after performing shutil.move() we have to check that if the folder with new name exists in correct location.
        # if the folder exists in correct position then return passed
        # if the folder doesn't exist in correct position then return failed
        if os.path.isdir(new_name_of_the_folder):
            CommonUtil.ExecLog(sModuleInfo, "Returning result of rename folder function", 1)
            CommonUtil.ExecLog(sModuleInfo, "folder exists... rename function is done properly", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Returning result of rename folder function", 1)
            CommonUtil.ExecLog(sModuleInfo, "folder doesn't exist... rename function is not done properly", 3)
            return "failed"
        CommonUtil.ExecLog(sModuleInfo,"Renaming folder %s to %s is complete" % (folder_to_be_renamed, new_name_of_the_folder), 1)
        return result
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Rename Folder", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Moving folder %s to %s" % (folder_to_be_moved, new_name_of_the_folder), 1)
        shutil.move(folder_to_be_moved, new_name_of_the_folder)
        CommonUtil.ExecLog(sModuleInfo, "Checking whether folder is moved properly", 1)
        # after performing shutil.move() we have to check that if the folder with new name exists in correct location.
        # if the folder exists in correct position then return passed
        # if the folder doesn't exist in correct position then return failed
        if os.path.isdir(new_name_of_the_folder):
            CommonUtil.ExecLog(sModuleInfo, "Returning result of move folder function", 1)
            CommonUtil.ExecLog(sModuleInfo, "folder exists... move function is done properly", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Returning result of move folder function", 1)
            CommonUtil.ExecLog(sModuleInfo, "folder doesn't exist... move function is not done properly", 3)
            return "failed"
        CommonUtil.ExecLog(sModuleInfo,"Moving folder %s to %s is complete" % (folder_to_be_renamed, new_name_of_the_folder), 1)
        return result
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Unzip", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Unzipping file %s to %s" % (file_to_be_unzipped, location_where_to_unzip), 1)
        if os.path.isfile(file_to_be_unzipped):
            zip_ref = zipfile.ZipFile(file_to_be_unzipped, 'r')
            zip_ref.extractall(location_where_to_unzip)
            result = zip_ref.close()
            CommonUtil.ExecLog(sModuleInfo, "Returning result of unzip  function", 1)
            CommonUtil.ExecLog(sModuleInfo,"Unzipping file %s to %s is complete" % (file_to_be_unzipped, location_where_to_unzip),1)
            return result
        else:
            CommonUtil.ExecLog(sModuleInfo, "can't unzip file as it doesn't exist", 3)
            return False
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare File", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Comparing files %s and %s" % (file_to_be_compared1, file_to_be_compared2), 1)
        result = filecmp.cmp(file_to_be_compared1, file_to_be_compared2)
        CommonUtil.ExecLog(sModuleInfo, "Returning result of compare file function", 1)
        CommonUtil.ExecLog(sModuleInfo,"Comparing files %s and %s is complete" % (file_to_be_compared1, file_to_be_compared2), 1)
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Zip File", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Zipping file %s to %s" % (file_to_be_zipped, location_where_to_zip), 1)
        if os.path.isfile(file_to_be_zipped):
            list1 = file_to_be_zipped.split('/')
            list2 = location_where_to_zip.split('/')
            value = file_to_be_zipped[:len(file_to_be_zipped) - len(list1[len(list1) - 1])]
            os.chdir(value)
            result = zipfile.ZipFile(list2[len(list2) - 1], mode='w').write(list1[len(list1) - 1])
            CommonUtil.ExecLog(sModuleInfo, "Returning result of zip file function", 1)
            CommonUtil.ExecLog(sModuleInfo,"Zipping file %s to %s is complete" % (file_to_be_zipped, location_where_to_zip), 1)
            return result
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Zip File for Windows", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Zipping file %s to %s" % (file_to_be_zipped, location_where_to_zip), 1)
        if os.path.isfile(file_to_be_zipped):
            list1 = file_to_be_zipped.split('//')
            list2 = location_where_to_zip.split('//')
            value = file_to_be_zipped[:len(file_to_be_zipped) - len(list1[len(list1) - 1])]
            os.chdir(value)
            result = zipfile.ZipFile(list2[len(list2) - 1], mode='w').write(list1[len(list1) - 1])
            CommonUtil.ExecLog(sModuleInfo, "Returning result of zip file for windows function", 1)
            CommonUtil.ExecLog(sModuleInfo,"Zipping file %s to %s is complete" % (file_to_be_zipped, location_where_to_zip), 1)
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Zip Folder", 1)
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

            result = zip.close()
            CommonUtil.ExecLog(sModuleInfo, "Returning result of zip folder function", 1)
            CommonUtil.ExecLog(sModuleInfo,
                               "Zipping folder %s to %s is complete" % (dir_to_be_zipped, location_where_to_zip), 1)
            return result

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
    CommonUtil.ExecLog(sModuleInfo, "Function: Delete File", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Deleting file %s" % sFilePath, 1)
        if os.path.isfile(sFilePath):
            os.remove(sFilePath)
            CommonUtil.ExecLog(sModuleInfo, "Checking whether folder is deleted properly", 1)
            # after performing os.remove() we have to check that if the file still exists in that location.
            # if the file exists in that position then return failed as it is not deleted
            # if the file doesn't exist in that position then return passed
            if os.path.isfile(sFilePath):
                CommonUtil.ExecLog(sModuleInfo, "Returning result of delete file function", 1)
                CommonUtil.ExecLog(sModuleInfo, "file exists... delete function is not done properly", 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Returning result of delete file function", 1)
                CommonUtil.ExecLog(sModuleInfo, "file doesn't exist... delete function is done properly", 1)
                return "passed"
            CommonUtil.ExecLog(sModuleInfo, "Deleting file %s is complete" % sFilePath, 1)

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
    CommonUtil.ExecLog(sModuleInfo, "Function: Delete Folder", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Deleting folder %s" % sFolderPath, 1)
        # print os.path.isdir(sFolderPath)
        if os.path.isdir(sFolderPath):
            shutil.rmtree(sFolderPath)
            CommonUtil.ExecLog(sModuleInfo, "Checking whether folder is deleted properly", 1)
            # after performing os.remove() we have to check that if the folder still exists in that location.
            # if the folder exists in that position then return failed as it is not deleted
            # if the folder doesn't exist in that position then return passed
            if os.path.isdir(sFolderPath):
                CommonUtil.ExecLog(sModuleInfo, "Returning result of delete folder function", 1)
                CommonUtil.ExecLog(sModuleInfo, "folder exists... delete function is not done properly", 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Returning result of delete folder function", 1)
                CommonUtil.ExecLog(sModuleInfo, "folder doesn't exist... delete function is done properly", 1)
                return "passed"
            CommonUtil.ExecLog(sModuleInfo, "Deleting folder %s is complete" % sFilePath, 1)
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Find file", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Returning result of find file function", 1)
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
    CommonUtil.ExecLog(sModuleInfo, "Function: empty trash", 1)
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
        for dir, sub_dirs, files in os.walk(trash_path):      #checking if trash is empty or not
            if not files:
                CommonUtil.ExecLog(sModuleInfo, "Trying to find files/folders in trash", 1)
            else:
                flag=1    # Trash is not empty. Trash will be cleared if flag is changed to 1
        if flag==1:
            CommonUtil.ExecLog(sModuleInfo, "Files/folders found in trash.... So trying to empty it", 1)
            result = os.system("rm -rf *")  #Empty Trash

        else:
            CommonUtil.ExecLog(sModuleInfo, "------Trash is empty already------", 1)
            return "passed"   #return "failed" if trash is already cleared


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
    CommonUtil.ExecLog(sModuleInfo, "Function: Copy Folder", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Coping folder %s to %s" % (src, dest), 1)
        shutil.copytree(src, dest)
        CommonUtil.ExecLog(sModuleInfo, "Checking whether folder is copied properly", 1)
        # after performing shutil.copytree() we have to check that if the folder is created correct location.
        # if the folder exists in correct position then return passed
        # if the folder doesn't exist in correct position then return failed
        if os.path.isdir(dest):
            CommonUtil.ExecLog(sModuleInfo, "Returning result of copy folder function", 1)
            CommonUtil.ExecLog(sModuleInfo, "folder exists... copy function is done properly", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Returning result of rename folder function", 1)
            CommonUtil.ExecLog(sModuleInfo, "folder doesn't exist... copy function is not done properly", 3)
            return "failed"
        CommonUtil.ExecLog(sModuleInfo, "Coping folder %s to %s is complete" % (src, dest), 1)
        return result
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Copy File", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Coping file %s to %s" % (src, dest), 1)
        shutil.copyfile(src, dest)
        CommonUtil.ExecLog(sModuleInfo, "Checking whether file is copied properly", 1)
        # after performing shutil.copyfile() we have to check that if the file with new name exists in correct location.
        # if the file exists in correct position then return passed
        # if the file doesn't exist in correct position then return failed
        if os.path.isfile(dest):
            CommonUtil.ExecLog(sModuleInfo, "Returning result of copy file function", 1)
            CommonUtil.ExecLog(sModuleInfo, "file exists... copy function is done properly", 1)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Returning result of rename file function", 1)
            CommonUtil.ExecLog(sModuleInfo, "file doesn't exist... copy function is not done properly", 3)
            return "failed"
        CommonUtil.ExecLog(sModuleInfo, "Coping file %s to %s is complete" % (src, dest), 1)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# function to empty recycle bin for windows
def empty_recycle_bin():
    """
                :return: Exception if Exception occurs or "failed if bin is empty otherwise return the result
                    """
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Empty Recycle Bin", 1)
    try:
        import winshell
        CommonUtil.ExecLog(sModuleInfo, "Staring to empty recycle bin", 1)
        recycle_bin = winshell.recycle_bin()
        List_recycle = list(recycle_bin)
        flag = 0
        if len(List_recycle) > 0:  #checking if trash is empty or not
            flag=1        # Trash is not empty. Trash will be cleared if flag is changed to 1
        if flag == 1:
            CommonUtil.ExecLog(sModuleInfo, "Files/folders found in recycle bin.... So trying to empty it", 1)
            result = winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)       #Empty Trash

        else:
            CommonUtil.ExecLog(sModuleInfo, "------Recycle Bin is empty already------", 1)
            return "passed"   #return "failed" if trash is already cleared

        CommonUtil.ExecLog(sModuleInfo, "Returning result of empty recycle bin function", 1)
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Run Win Cmd", 1)
    try:
        CommonUtil.ExecLog(sModuleInfo, "Staring to run windows admin command", 1)
        result = []
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in process.stdout:
            result.append(line)
        errcode = process.returncode
        for line in result:
            #print(line)
            CommonUtil.ExecLog(sModuleInfo, "%s" %line, 1)
        if errcode is not None:
            CommonUtil.ExecLog(sModuleInfo, 'cmd %s failed, see above for details' % cmd, 3)
            raise Exception('cmd %s failed, see above for details', cmd)
        CommonUtil.ExecLog(sModuleInfo, "Win Command Complete", 1)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def run_cmd(command, return_status=False, is_shell=True, stdout_val=subprocess.PIPE, local_run=False):
    """

                    :param command: sudo command to run
                    :return: Exception if Exception occurs otherwise return result 
                        """
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
        CommonUtil.ExecLog(sModuleInfo, "Trying to run command: %s" % command, 1, local_run)
        # global subprocess_dict
        result = []

        # open a subprocess with command, and assign a session id to the shell process
        # this is will make the shell process the group leader for all the child processes spawning from it
        status = subprocess.Popen(command, shell=is_shell, stdout=stdout_val, preexec_fn=os.setsid)
        subprocess_dict[status] = Running
        for line in status.stdout:
            result.append(line)
        errcode = status.returncode
        for line in result:
            CommonUtil.ExecLog(sModuleInfo, "%s" % line, 1)
        if return_status:
            return status
        else:
            CommonUtil.ExecLog(sModuleInfo, "Sudo Command Complete", 1)
            return Passed

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# function to generate random string
def random_string_generator(pattern='nluc', size=10):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: random string generator", 1)
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


def sanitizing_function(input_string):
    """

    Convert _, or multiple _ to single space
    Convert multiple space to single space
    Strip leading and trailing whitespace
    Convert to lower case
    put a limit on string length - say 256 bytes



        :param input_string: take input string
        :return: return sanitized string 
                            """
    input_string = input_string.replace('_', ' ')  # replace "_" with " "

    input_string = ' '.join(input_string.split())  # Convert multiple space to single space

    input_string = input_string.lower()  # Convert to lower case
    input_string = input_string[:256]  # put a limit on string length - say 256 bytes

    return input_string


def sanitize(step_data, sanitization):
    if sanitization == True:
        for each in step_data:
            for row in each:
                i = 0
                for element in row:
                    if (isinstance(element, str)):
                        if "%|" not in element or "|%" not in element:  # will not sanitize a string like %|...|%
                            row[i] = sanitizing_function(element)

                    i += 1
    return step_data


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

#code to generate raw string
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Copy File or Folder", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            from_path = get_home_folder() + str(step_data[0][0][0]).strip()  # location of the file/folder to be copied
            to_path = get_home_folder() + str(step_data[0][0][2]).strip()  # location where to copy the file/folder
            file_or_folder = str(step_data[0][1][2]).strip()  # get if it is file/folder to copy
            if file_or_folder.lower() == 'file':
                # copy file "from_path" to "to_path"
                result = copy_file(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,"Could not copy file '%s' to the destination '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,"File '%s' copied to the destination '%s' successfully" % (from_path, to_path),1)
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
        elif _platform == "win32":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            from_path = raw(str(step_data[0][0][0]).strip())  # location of the file/folder to be copied
            to_path = raw(str(step_data[0][0][2]).strip())  # location where to copy the file/folder
            file_or_folder = str(step_data[0][1][2]).strip()  # get if it is file/folder to copy
            if file_or_folder.lower() == 'file':
                # copy file "from_path" to "to_path"
                result = copy_file(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,"Could not copy file '%s' to the destination '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,"File '%s' copied to the destination '%s' successfully" % (from_path, to_path),1)
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

                # return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to delete file/folder
def Delete_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Delete File or Folder", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            path = get_home_folder() + str(step_data[0][0][0]).strip()  # path of the file/folder to be deleted
            file_or_folder = str(step_data[0][1][2]).strip()  # get if it is file/folder to delete
            if file_or_folder.lower() == 'file':
                # delete file "path"
                result = DeleteFile(path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Could not delete file '%s'" % (path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "File '%s' deleted successfully" % (path), 1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
                # delte folder "path"
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
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            path = raw(str(step_data[0][0][0]).strip())  # path of the file/folder to be deleted
            file_or_folder = str(step_data[0][1][2]).strip()  # get if it is file/folder to delete
            if file_or_folder.lower() == 'file':
                # delete file "path"
                result = DeleteFile(path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Could not delete file '%s'" % (path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "File '%s' deleted successfully" % (path), 1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
                # delete folder "path"
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


# Method to find file
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
                CommonUtil.ExecLog(sModuleInfo, "Could not find file '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "File '%s' found" % (path), 1)
                return "passed"

        else:
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return 'failed'

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to empty trash/recycle bin
def Empty_Trash(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Empty Trash Can", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            path = get_home_folder() + '/.local/share/Trash'  # location of trash for linux
            #print path

            result = empty_trash(path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not empty trash '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "trash is cleared '%s'" % (path), 1)
                return "passed"
        elif _platform == "win32":
            # linux
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Get User Name", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            path = get_home_folder()  # get the path of the home directory
            list_elemnet = path.split("/")  # list the parts of path by spliting it by "/"
            name = list_elemnet[len(list_elemnet) - 1]  # name of the user
            if name in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find user name '%s'" % (name), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "user name is '%s'" % (name), 1)
                return "passed"
        elif _platform == "win32":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            CommonUtil.ExecLog(sModuleInfo, "Could not find user name as it is windows", 3)
            return "failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to Run Sudo Command
def Run_Sudo_Command(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Run Sudo Command", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            command = str(step_data[0][0][0]).strip()
            result = run_cmd(command)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not run sudo command '%s'" % (command), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "sudo command is run properly '%s'" % (command), 1)
                return "passed"
        elif _platform == "win32":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            CommonUtil.ExecLog(sModuleInfo, "Could not run sudo command as it is windows", 3)
            return "failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to Run Command
def Run_Command(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Run command for windows", 1)
    try:
        if _platform == "win32":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            command = str(step_data[0][0][0]).strip()
            result = run_win_cmd(command)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not run sudo command '%s'" % (command), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "sudo command is run properly '%s'" % (command), 1)
                return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to Get Home Directory
def Get_Home_Directory(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get Home Directory", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            path = get_home_folder()
            #print path
            CommonUtil.ExecLog(sModuleInfo, "Home Directory Path is '%s'"%(path), 1)
            if path in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find home directory '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "home directory is '%s'" % (path), 1)
                return "passed"
        elif _platform == "win32":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            CommonUtil.ExecLog(sModuleInfo, "Could not find home directory as it is windows", 3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to Get Current Desktop
def Get_Current_Desktop(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get Current Desktop", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            path = get_home_folder() + "/Desktop"  # concate home folder path with "/Desktop"
            #print path
            CommonUtil.ExecLog(sModuleInfo, "Desktop Path is '%s'" % (path), 1)
            if path in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find desktop '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "desktop path is '%s'" % (path), 1)
                return "passed"
        elif _platform == "win32":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            path = os.path.join(os.environ["HOMEPATH"], "Desktop")
            #print path
            CommonUtil.ExecLog(sModuleInfo, "Desktop Path is '%s'" % (path), 1)
            if path in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find desktop '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "desktop path is '%s'" % (path), 1)
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to Get Current Documents
def Get_Current_Documents(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Get Current Documents", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            path = get_home_folder() + "/Documents"  # concate home folder path with "/Documents"
            #print path
            CommonUtil.ExecLog(sModuleInfo, "Documents Path is '%s'" % (path), 1)
            if path in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find Documents '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Documents path is '%s'" % (path), 1)
                return "passed"
        elif _platform == "win32":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            path = os.path.join(os.environ["HOMEPATH"], "Documents")
            #print path
            CommonUtil.ExecLog(sModuleInfo, "Documents Path is '%s'" % (path), 1)
            if path in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Could not find Documents '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Documents path is '%s'" % (path), 1)
                return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to create file
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
                CommonUtil.ExecLog(sModuleInfo, "Could not create file '%s'" % (path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "File '%s' created" % (path), 1)
                return "passed"

        else:
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return 'failed'

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to compare file
def Compare_File(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Compare File", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            from_path = get_home_folder() + str(step_data[0][0][0]).strip()  # location of file path to be compared
            to_path = get_home_folder() + str(step_data[0][0][2]).strip()  # location of file path to be compared
            file_or_folder = str(step_data[0][1][2]).strip()
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
        elif _platform == "win32":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            #print step_data[0][0][0]
            #print str(step_data[0][0][0])
            from_path = raw(str(step_data[0][0][0]).strip())  # location of file path to be compared
            #print  from_path
            to_path = raw(str(step_data[0][0][2]).strip())  # location of file path to be compared
            #print to_path
            file_or_folder = str(step_data[0][1][2]).strip()
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
    CommonUtil.ExecLog(sModuleInfo, "Function: Rename File or Folder", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            from_path = get_home_folder() + str(step_data[0][0][0]).strip()  # location of the file/folder to be renamed
            to_path = get_home_folder() + str(step_data[0][0][2]).strip()  # location where to rename the file/folder
            file_or_folder = str(step_data[0][1][2]).strip()  # get if it is file/folder to rename
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
                CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
                return 'failed'
        elif _platform == "win32":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            from_path = raw(str(step_data[0][0][0]).strip())  # location of the file/folder to be renamed
            to_path = raw(str(step_data[0][0][2]).strip())  # location where to rename the file/folder
            file_or_folder = str(step_data[0][1][2]).strip()  # get if it is file/folder to rename
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
                # rename folder 'from_path" to "to_path"
                result = RenameFolder(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Could not rename folder '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Folder '%s' renamed to '%s' successfully" % (from_path, to_path),
                                       1)
                    return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
                return 'failed'

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to zip file/folder
def Zip_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Zip File or Folder", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            from_path = get_home_folder() + str(step_data[0][0][0]).strip()  # location of the file/folder to be zipped
            to_path = get_home_folder() + str(step_data[0][0][2]).strip()  # location where to zip the file/folder
            file_or_folder = str(step_data[0][1][2]).strip()  # get if it is file/folder to zip
            if file_or_folder.lower() == 'file':
                result = ZipFile(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo, "Can't not zip file '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo, "File '%s' renamed to '%s' successfully" % (from_path, to_path), 1)
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
                CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
                return 'failed'
        elif _platform == "win32":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            from_path = raw(str(step_data[0][0][0]).strip())  # location of the file/folder to be zipped
            to_path = raw(str(step_data[0][0][2]).strip())  # location where to zip the file/folder
            file_or_folder = str(step_data[0][1][2]).strip()  # get if it is file/folder to zip
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
                CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
                return 'failed'
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to unzip
def Unzip_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Unzip File or Folder", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            from_path = get_home_folder() + str(
                step_data[0][0][0]).strip()  # location of the file/folder to be unzipped
            to_path = get_home_folder() + str(step_data[0][0][2]).strip()  # location where to unzip the file/folder

            result = UnZip(from_path, to_path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo, "Can't not unzip '%s' to '%s'" % (from_path, to_path), 3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "'%s' is unzipped to '%s' successfully" % (from_path, to_path), 1)
                return "passed"



        elif _platform == "win32":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            from_path = raw(str(step_data[0][0][0]).strip())  # location of the file/folder to be unzipped
            to_path = raw(str(step_data[0][0][2]).strip())  # location where to unzip the file/folder

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
    CommonUtil.ExecLog(sModuleInfo, "Function: Move File or Folder", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "linux", 1)
            from_path = get_home_folder() + str(step_data[0][0][0]).strip()  # location of the file/folder to be moved
            to_path = get_home_folder() + str(step_data[0][0][2]).strip()  # location where to move the file/folder
            file_or_folder = str(step_data[0][1][2]).strip()  # get if it is file/folder to move
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
        elif _platform == "win32":
            # linux
            CommonUtil.ExecLog(sModuleInfo, "windows", 1)
            from_path = raw(str(step_data[0][0][0]).strip())  # location of the file/folder to be moved
            to_path = raw(str(step_data[0][0][2]).strip())  # location where to move the file/folder
            file_or_folder = str(step_data[0][1][2]).strip()  # get if it is file/folder to move
            if file_or_folder.lower() == 'file':
                # move file "from_path" to "to_path"
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


# Method to sleep for a particular duration
def Sleep(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Sleep", 1)
    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return "failed"
        else:
            tuple = step_data[0][0]
            seconds = int(tuple[2])
            CommonUtil.ExecLog(sModuleInfo, "Sleeping for %s seconds" % seconds, 1)
            time.sleep(seconds)
            return "passed"
            # return result
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
            CommonUtil.ExecLog(sModuleInfo,"The action you entered is incorrect. Please provide accurate information on the data set(s).",3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# return only the path step data
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


# return validated path data with path1 and path2
def Validate_Path_Step_Data(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Validate_Step_Data", 1)
    try:
        path1 = get_home_folder() + str(step_data[0][0]).strip()
        path2 = get_home_folder() + str(step_data[0][2]).strip()
        validated_data = (path1, path2
                          )
        return validated_data
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not find the new page element requested.  Error: %s" % (Error_Detail), 3)
        return "failed"


# Performs a series of action or conditional logical action decisions based on user input
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
            logic_row = []
            for row in each:
                # finding what to do for each dataset
                # if len(row)==5 and row[1] != "":     ##modifying the filter for changes to be made in the sub-field of the step data. May remove this part of the if statement
                if ((row[
                         1] == "path")):  ##modifying the filter for changes to be made in the sub-field of the step data. May remove this part of the if statement
                    continue

                elif row[1] == "action":
                    # finding the action to be performed
                    CommonUtil.ExecLog(sModuleInfo, "Checking the action to be performed in the action row", 1)
                    # handle the action
                    result = Action_Handler([each], row[0])
                    if result == [] or result == "failed":
                        return "failed"
                elif row[1] == "conditional action":
                    CommonUtil.ExecLog(sModuleInfo,"Checking the logical conditional action to be performed in the conditional action row",1)
                    logic_decision = ""
                    logic_row.append(row)
                    if len(logic_row) == 2:
                        # element_step_data = each[0:len(step_data[0])-2:1]
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
                                return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                    else:
                        # continue until length  of logic_row is 2
                        continue

                    # handle the conditional action
                    for conditional_steps in logic_row:
                        if logic_decision in conditional_steps:
                            #print conditional_steps[2]
                            list_of_steps = conditional_steps[2].split(",")
                            for each_item in list_of_steps:
                                data_set_index = int(each_item) - 1
                                cond_result = Sequential_Actions([step_data[data_set_index]])
                                if cond_result == "failed":
                                    return "failed"
                            return "passed"

                else:
                    CommonUtil.ExecLog(sModuleInfo,"The sub-field information is incorrect. Please provide accurate information on the data set(s).",3)
                    return "failed"
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


'===================== ===x=== Sequential Action Section Ends ===x=== ======================'




