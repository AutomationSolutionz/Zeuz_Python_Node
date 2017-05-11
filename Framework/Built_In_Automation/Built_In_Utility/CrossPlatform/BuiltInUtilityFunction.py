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


from Framework.Utilities import CommonUtil
from sys import platform as _platform

passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True','1','Success','success','SUCCESS',True]
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE','0',False]


import os,subprocess,shutil



import zipfile

add_sanitization = True

def get_home_folder():
    """

    :return: give the location of home folder
    """
    return os.path.expanduser("~")

def CreateFolder(folderPath, forced=True):
    """

    :param folderPath: folderpath to create
    :param forced: if true remove the folder first, if false won't remove the folder if there exists one with same name
    :return: False if failed and exception or True if successful
    """
    try:
        if os.path.isdir(folderPath):
            if forced == False:
                print "folder already exists"
                return True
            DeleteFolder(folderPath)
        os.makedirs(folderPath)
        return True
    except Exception, e:
        return "Error: %s" % e

def CreateFile(sFilePath):
    try:
        if os.path.isfile(sFilePath):
            print "File already exists"
            return False
        else:
            print "Creating new file"
            newfile = open(sFilePath, 'w')
            newfile.close()
            return newfile
    except Exception, e:
        print "Error: %s" % e
        return False

def RenameFile(a,b):
    try:
        result = shutil.move(a, b)
        return result
    except Exception, e:
        print "Error: %s" % e
        return False

def RenameFolder(a,b):
    try:
        result = shutil.move(a, b)
        return result
    except Exception, e:
        print "Error: %s" % e
        return False

def UnZip(a,b):
    try:
        if os.path.isfile(a):
            zip_ref = zipfile.ZipFile(a, 'r')
            zip_ref.extractall(b)
            result = zip_ref.close()
            return result
        else:
            return False
    except Exception, e:
        print "Error: %s" % e
        return False

def UnZip1(a,b):
    try:
        import zipfile

        with zipfile.ZipFile('test.zip', "r") as z:
            z.extractall("C:\\")
    except Exception, e:
        print "Error: %s" % e
        return False

def CompareFile(path1, path2):
    try:
        import filecmp
        result = filecmp.cmp(path1, path2)
        return result
    except Exception, e:
        print "Error: %s" % e
        return False

def ZipFile(path1, path2):
    try:
        import zipfile
        if os.path.isfile(path1):
            list1=path1.split('/')
            list2=path2.split('/')
            value=path1[:len(path1)-len(list1[len(list1)-1])]
            os.chdir(value)
            result=zipfile.ZipFile(list2[len(list2)-1], mode='w').write(list1[len(list1)-1])
            return result
        else:
            return False
    except Exception, e:
        print "Error: %s" % e
        return False

def ZipFolder(dir, zip_file):
    """
    Zips a given folder, its sub folders and files. Ignores any empty folders
    dir is the path of the folder to be zipped
    zip_file is the path of the zip file to be created
    """
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
            return result

        else:
            return False

    except Exception, e:
        print "Exception :", e
        return False

def DeleteFile(sFilePath):
    try:
        if os.path.isfile(sFilePath):
            result=os.remove(sFilePath)
            return result
        else:
            return False
    except Exception, e:
        print "Error: %s" % e
        return False


def DeleteFolder(sFilePath):
    try:
        if os.path.isdir(sFilePath):
            shutil.rmtree(sFilePath)

    except Exception, e:
        print "Error: %s" % e
        return False

def find(sFilePath):
    try:
        return os.path.isfile(sFilePath)

    except Exception, e:
        print "Error: %s" % e
        return False

def empty_trash(sFilePath):
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
        return False


def copy_folder(src, dest):
    """

    :param src: source of the folder
    :param dest: destination to be copied.
    :return: True if passed or False if failed
    """
    try:
        result = shutil.copytree(src, dest)
        return result
    except Exception, e:
        print "Error: %s" % e
        return False


def copy_file(src, dest):
    """

    :param src: full location of source file
    :param dest: full location of destination file
    :return: True if passed or False if failed
    """
    try:
        result = shutil.copyfile(src, dest)
        return result
    except Exception, e:
        print "Error: %s" % e
        return False

def empty_recycle_bin():
    try:
        import winshell
        result=winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        print result
        return result
    except Exception, e:
        print "Error: %s" % e
        return False

# not done properly...need more works
def change_path_for_windows(src):
    print src
    string_list=str(src).split("\\")
    print string_list
    print src
    return src

def sanitizing_function(input_string):

    input_string = input_string.replace('_', ' ')

    input_string = ' '.join(input_string.split())

    input_string = input_string.lower()
    input_string = input_string[:256]

    return input_string

def sanitize(step_data, sanitization):
    if sanitization == True:
        for each in step_data:
            for row in each:
                i=0
                for element in row:
                    if(isinstance(element, str)):
                        if "%|" not in element or "|%" not in element:
                            row[i] = sanitizing_function(element)

                    i+=1
    return step_data

#Handles actions for the sequential logic, based on the input from the mentioned function
def Action_Handler(action_step_data, action_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Action_Handler", 1)
    try:
        if action_name == "skip":
            return "passed"
        elif action_name =="copy":
            result = Copy_File_or_Folder(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name =="delete":
            result = Delete_File_or_Folder(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name =="create":
            result = Create_File(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name =="find":
            result = Find_File(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name =="rename":
            result = Rename_File_or_Folder(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name =="move":
            result = Move_File_or_Folder(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name =="zip":
            result = Zip_File_or_Folder(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name =="unzip":
            result = Unzip_File_or_Folder(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name =="compare":
            result = Compare_File(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name =="empty":
            result = Empty_Trash(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name =="sleep":
            result = Sleep(action_step_data)
            if result == "failed":
                return "failed"

        else:
            CommonUtil.ExecLog(sModuleInfo, "The action you entered is incorrect. Please provide accurate information on the data set(s).", 3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Method to copy file/folder
def Copy_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Copy File or Folder", 1)
    try:
        if _platform == "linux" or _platform == "linux2":
            # linux
            print "linux"
            from_path = get_home_folder() + str(step_data[0][0][0]).strip()
            to_path = get_home_folder() + str(step_data[0][0][2]).strip()
            file_or_folder = str(step_data[0][1][2]).strip()
            if file_or_folder.lower() == 'file':
                result = copy_file(from_path,to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,"Could not copy file '%s' to the destination '%s'"%(from_path,to_path),3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,"File '%s' copied to the destination '%s' successfully" % (from_path, to_path), 1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
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
            from_path = change_path_for_windows(str(step_data[0][0][0]).strip())
            to_path = change_path_for_windows(str(step_data[0][0][2]).strip())
            file_or_folder = str(step_data[0][1][2]).strip()
            if file_or_folder.lower() == 'file':
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
            path = get_home_folder() + str(step_data[0][0][0]).strip()
            file_or_folder = str(step_data[0][1][2]).strip()
            if file_or_folder.lower() == 'file':
                result = DeleteFile(path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,"Could not delete file '%s'"%(path),3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,"File '%s' deleted successfully" % (path), 1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
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
            path = change_path_for_windows(str(step_data[0][0][0]).strip())
            file_or_folder = str(step_data[0][1][2]).strip()
            if file_or_folder.lower() == 'file':
                result = DeleteFile(path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,"Could not delete file '%s'"%(path),3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,"File '%s' deleted successfully" % (path), 1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
               # path='C:\\Users\\User\\Pictures\\Saved Pictures'
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
            path = get_home_folder() + '/.local/share/Trash'
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
            result=empty_recycle_bin()
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Could not empty recycle bin ",3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"recycle bin is cleared " , 1)
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
            from_path = get_home_folder() + str(step_data[0][0][0]).strip()
            to_path = get_home_folder() + str(step_data[0][0][2]).strip()
            file_or_folder = str(step_data[0][1][2]).strip()
            if file_or_folder.lower() == 'file':
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
            from_path = change_path_for_windows(str(step_data[0][0][0]).strip())
            print  from_path
            to_path = change_path_for_windows(str(step_data[0][0][2]).strip())
            print to_path
            file_or_folder = str(step_data[0][1][2]).strip()
            if file_or_folder.lower() == 'file':
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
                from_path = get_home_folder() + str(step_data[0][0][0]).strip()
                to_path = get_home_folder() + str(step_data[0][0][2]).strip()
                file_or_folder = str(step_data[0][1][2]).strip()
                if file_or_folder.lower() == 'file':
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
                from_path = str(step_data[0][0][0]).strip()
                to_path = str(step_data[0][0][2]).strip()
                file_or_folder = str(step_data[0][1][2]).strip()
                if file_or_folder.lower() == 'file':
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
            from_path = get_home_folder() + str(step_data[0][0][0]).strip()
            to_path = get_home_folder() + str(step_data[0][0][2]).strip()
            file_or_folder = str(step_data[0][1][2]).strip()
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
            from_path = str(step_data[0][0][0]).strip()
            to_path = str(step_data[0][0][2]).strip()
            file_or_folder = str(step_data[0][1][2]).strip()
            if file_or_folder.lower() == 'file':
                result = ZipFile(from_path, to_path)
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
            from_path = get_home_folder() + str(step_data[0][0][0]).strip()
            to_path = get_home_folder() + str(step_data[0][0][2]).strip()
            file_or_folder = str(step_data[0][1][2]).strip()
            if file_or_folder.lower() == 'file':
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
            elif file_or_folder.lower() == 'folder':
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
            else:
                CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
                return 'failed'
        elif _platform == "win32":
                    # linux
            print "windows"
            from_path = get_home_folder() + str(step_data[0][0][0]).strip()
            to_path = get_home_folder() + str(step_data[0][0][2]).strip()
            file_or_folder = str(step_data[0][1][2]).strip()
            if file_or_folder.lower() == 'file':
                result = UnZip1(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,
                                   "Can't not unzip '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,
                                   "'%s' is unzipped to '%s' successfully" % (from_path, to_path),
                                   1)
                    return "passed"
            elif file_or_folder.lower() == 'folder':
                result = UnZip1(from_path, to_path)
                if result in failed_tag_list:
                    CommonUtil.ExecLog(sModuleInfo,
                                   "Can't not unzip '%s' to '%s'" % (from_path, to_path), 3)
                    return "failed"
                else:
                    CommonUtil.ExecLog(sModuleInfo,
                                   "'%s' is unzipped to '%s' successfully" % (from_path, to_path),
                                   1)
                    return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo,
                               "The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",
                               3)
                return 'failed'


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
            from_path = get_home_folder() + str(step_data[0][0][0]).strip()
            to_path = get_home_folder() + str(step_data[0][0][2]).strip()
            file_or_folder = str(step_data[0][1][2]).strip()
            if file_or_folder.lower() == 'file':
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
            from_path = str(step_data[0][0][0]).strip()
            to_path = str(step_data[0][0][2]).strip()
            file_or_folder = str(step_data[0][1][2]).strip()
            if file_or_folder.lower() == 'file':
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
        global add_sanitization
        if step_data[0][0][0]=="skip" and step_data[0][0][1]=="action":
            add_sanitization = False
        print step_data
        sanitize(step_data,add_sanitization)
        print step_data
        for each in step_data:
            logic_row=[]
            for row in each:
                #finding what to do for each dataset
                #if len(row)==5 and row[1] != "":     ##modifying the filter for changes to be made in the sub-field of the step data. May remove this part of the if statement
                if ((row[1] == "path")):     ##modifying the filter for changes to be made in the sub-field of the step data. May remove this part of the if statement
                    continue

                elif row[1]=="action":
                    CommonUtil.ExecLog(sModuleInfo, "Checking the action to be performed in the action row", 1)
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
                        continue

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



