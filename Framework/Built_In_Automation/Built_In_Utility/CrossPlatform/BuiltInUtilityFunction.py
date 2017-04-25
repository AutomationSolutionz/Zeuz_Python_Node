# -*- coding: cp1252 -*-
'''
Created on May 15, 2016

@author: Built_In_Automation Solutionz Inc.
'''

import sys
import os
sys.path.append("..")
import time
import inspect

from Framework.Utilities import CommonUtil
from Framework.Utilities import FileUtilities

passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True','1','Success','success','SUCCESS',True]
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE','0',False]

#Handles actions for the sequential logic, based on the input from the mentioned function
def Action_Handler(action_step_data, action_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Action_Handler", 1)
    try:
        if action_name =="copy":
            result = Copy_File_or_Folder(action_step_data)
            if result == "failed":
                return "failed"
        elif action_name =="delete":
            result = Delete_File_or_Folder(action_step_data)
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
        elif action_name =="sleep":
            result = Sleep(action_step_data)
            if result == "failed":
                return "failed"

        else:
            CommonUtil.ExecLog(sModuleInfo, "The action you entered is incorrect. Please provide accurate information on the data set(s).", 3)
            return "failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Method to sleep for a particular duration
def Copy_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Copy File or Folder", 1)
    try:
        from_path = FileUtilities.get_home_folder() + str(step_data[0][0][0]).strip()
        to_path = FileUtilities.get_home_folder() + str(step_data[0][0][2]).strip()
        file_or_folder = str(step_data[0][1][2]).strip()
        if file_or_folder.lower() == 'file':
            result = FileUtilities.copy_file(from_path,to_path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Could not copy file '%s' to the destination '%s'"%(from_path,to_path),3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"File '%s' copied to the destination '%s' successfully" % (from_path, to_path), 1)
                return "passed"
        elif file_or_folder.lower() == 'folder':
            result = FileUtilities.copy_folder(from_path,to_path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Could not copy folder '%s' to the destination '%s'"%(from_path,to_path),3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"Folder '%s' copied to the destination '%s' successfully" % (from_path, to_path), 1)
                return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return 'failed'

        #return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


#Method to sleep for a particular duration
def Delete_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Copy File or Folder", 1)
    try:
        path = FileUtilities.get_home_folder() + str(step_data[0][0][0]).strip()
        file_or_folder = str(step_data[0][1][2]).strip()
        if file_or_folder.lower() == 'file':
            result = FileUtilities.DeleteFile(path)
            if result in failed_tag_list:
                CommonUtil.ExecLog(sModuleInfo,"Could not delete file '%s'"%(path),3)
                return "failed"
            else:
                CommonUtil.ExecLog(sModuleInfo,"File '%s' deleted successfully" % (path), 1)
                return "passed"
        elif file_or_folder.lower() == 'folder':
            result = FileUtilities.DeleteFolder(path)
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

def Rename_File_or_Folder(step_data):
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        CommonUtil.ExecLog(sModuleInfo, "Function: Rename File or Folder", 1)
        try:
            from_path = FileUtilities.get_home_folder() + str(step_data[0][0][0]).strip()
            to_path = FileUtilities.get_home_folder() + str(step_data[0][0][2]).strip()
            file_or_folder = str(step_data[0][1][2]).strip()
            if file_or_folder.lower() == 'file':
                result = FileUtilities.RenameFile(from_path, to_path)
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
                result = FileUtilities.RenameFolder(from_path, to_path)
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

def Move_File_or_Folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Rename File or Folder", 1)
    try:
        from_path = FileUtilities.get_home_folder() + str(step_data[0][0][0]).strip()
        to_path = FileUtilities.get_home_folder() + str(step_data[0][0][2]).strip()
        file_or_folder = str(step_data[0][1][2]).strip()
        if file_or_folder.lower() == 'file':
            result = FileUtilities.RenameFile(from_path, to_path)
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
            result = FileUtilities.RenameFolder(from_path, to_path)
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





#Performs a series of action or conditional logical action decisions based on user input
def Sequential_Actions(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    CommonUtil.ExecLog(sModuleInfo, "Function: Sequential_Actions", 1)
    try:
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

                else:
                    CommonUtil.ExecLog(sModuleInfo, "The sub-field information is incorrect. Please provide accurate information on the data set(s).", 3)
                    return "failed"
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())




