
import sys
sys.path.append("..")

import os, subprocess
import time
import inspect
import stat
import CommonUtil
import FileUtilities as FileUtil

if os.name == 'nt':
    from PCDesktop import WinCommonFoldersPaths as ComPath

elif os.name == 'posix':
    from MacDesktop import MacCommonFoldersPaths as ComPath

class CleanUp():
    ##Input to this class is: sClientName

    def __init__(self, sClientName):
        self.sClientName = sClientName

    def getClientName(self):
        return self.sClientName


    def ClientCleanUp(self):
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

        return "Pass"


    def DesktopCleanUp(self):
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        if os.name == 'nt':
            sFolderPath = ComPath.Get_Appdata_Path() + "\ProductFolderName"
            os.chmod(sFolderPath, stat.S_IWRITE)
            sTestStepReturnStatus = FileUtil.DeleteFolderContents(sFolderPath)
            print "Deleted Data from the Desktop App Data folder!"
            CommonUtil.ExecLog(sModuleInfo, "Cleaned up Desktop App Data folder!", 1)

            sFolderPath = ComPath.Get_local_Appdata_Path() + "\ProductFolderName"
            os.chmod(sFolderPath, stat.S_IWRITE)
            sTestStepReturnStatus = FileUtil.DeleteFolderContents(sFolderPath)
            print "Deleted Data from the Desktop Local App Data folder!"
            CommonUtil.ExecLog(sModuleInfo, "Cleaned up Desktop Local App Data folder!", 1)

            CommonUtil.ExecLog(sModuleInfo, "Cleaned up Desktop Log files in Temp folder!", 1)

        elif os.name == 'posix':
            sFolderPath = ComPath.Get_Appdata_Path() + os.sep + "logs"
            if os.path.isdir(sFolderPath):
                os.system("chflags nouchg " + "\"" + sFolderPath + "\"")

                TempFolderLog = []
                for eachfile in FileUtil.SearchFiles(sFolderPath, '.log'):
                    TempFolderLog.append(eachfile)

                for eachfile in TempFolderLog:
                    FileUtil.DeleteFile(eachfile)

                print "Deleted Data from the Desktop App Data folder!"
                CommonUtil.ExecLog(sModuleInfo, "Deleted Data from the Desktop App Data folder!", 1)
            else:
                print "Logs folder not found"
                sTestStepReturnStatus = "Pass"

        CommonUtil.ExecLog(sModuleInfo, "Completed Desktop Cleanup", 1)

        return sTestStepReturnStatus


    def RemoveAutomationFiles(self):
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        #import WinCommonFoldersPaths as WinPath
        try:
            CommonUtil.ExecLog(sModuleInfo, "Starting Automation files cleanup", 1)
            print "Removing all automation test data from previous test runs"
            if os.path.isdir(ComPath.Get_Desktop_Path() + os.sep + 'Temp' + os.sep + 'AutomationTestData'):
                os.chmod(ComPath.Get_Desktop_Path() + os.sep + 'Temp' + os.sep + 'AutomationTestData', 0777)
                sTestStepReturnStatus = FileUtil.DeleteFolderContents(ComPath.Get_Desktop_Path() + os.sep + 'Temp' + os.sep + 'AutomationTestData')
            else:
                sTestStepReturnStatus = FileUtil.CreateFolder(ComPath.Get_Desktop_Path() + os.sep + 'Temp' + os.sep + 'AutomationTestData', False)
                sTestStepReturnStatus = "Pass"
            if os.path.isdir(ComPath.Get_Desktop_Path() + os.sep + 'AutomationTestData'):
                os.chmod(ComPath.Get_Desktop_Path() + os.sep + 'AutomationTestData', 0777)
                sTestStepReturnStatus = FileUtil.DeleteFolderContents(ComPath.Get_Desktop_Path() + os.sep + 'AutomationTestData')
            else:
                sTestStepReturnStatus = FileUtil.CreateFolder(ComPath.Get_Desktop_Path() + os.sep + 'AutomationTestData', False)
                sTestStepReturnStatus = "Pass"
            CommonUtil.ExecLog(sModuleInfo, "Finished Automation files cleanup", 1)
            return sTestStepReturnStatus
        except Exception, e:
            return CommonUtil.LogCriticalException(sModuleInfo, e)


    def CleanUpMyFolderFiles(self, sFolderType='All'):
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        #Remove all files with MyPictures, MyVideo or MyMusic default folders
        CommonUtil.ExecLog(sModuleInfo, "Starting Windows My folder files cleanup", 1)
        print "Removing all data form %s" % sFolderType

        if sFolderType == "MyPictures":
            os.chmod(ComPath.Get_My_Pictures_Path(), 0777)
            sTestStepReturnStatus = FileUtil.DeleteFolderContents(ComPath.Get_My_Pictures_Path())
            #RenameFolder(WinPath.Get_My_Pictures_Path(), "Pictures", "My Pictures")                 
            print "My Pictures folder is cleaned"
            CommonUtil.ExecLog(sModuleInfo, "My Pictures Cleaned", 1)

        if sFolderType == "MyVideos":
            os.chmod(ComPath.Get_My_Videos_Path(), 0777)
            sTestStepReturnStatus = FileUtil.DeleteFolderContents(ComPath.Get_My_Videos_Path())
            print "My Videos folder is cleaned"
        if sFolderType == "MyMusic":
            if os.name == 'nt':
                os.chmod(ComPath.Get_MyMusic_Path(), 0777)
                sTestStepReturnStatus = FileUtil.DeleteFolderContents(ComPath.Get_MyMusic_Path())
                print "My Music folder is cleaned"
            elif os.name == 'posix':
                print "By Passing the Deleting of the iTunes folder"
        if sFolderType == 'All':
            try:
                os.chmod(ComPath.Get_My_Pictures_Path(), 0777)
                sTestStepReturnStatus = FileUtil.DeleteFolderContents(ComPath.Get_My_Pictures_Path())
                CommonUtil.ExecLog(sModuleInfo, "My Pictures Cleaned", 1)
                os.chmod(ComPath.Get_CommonPictures_Path(), 0777)
                sTestStepReturnStatus = FileUtil.DeleteFolderContents(ComPath.Get_CommonPictures_Path())
                CommonUtil.ExecLog(sModuleInfo, "Public Pictures Cleaned", 1)
            except Exception, e:
                print e
            try:
                os.chmod(ComPath.Get_My_Videos_Path(), 0777)
                sTestStepReturnStatus = FileUtil.DeleteFolderContents(ComPath.Get_My_Videos_Path())
                CommonUtil.ExecLog(sModuleInfo, "My Videos Cleaned", 1)
                os.chmod(ComPath.Get_CommonVideos_Path(), 0777)
                sTestStepReturnStatus = FileUtil.DeleteFolderContents(ComPath.Get_CommonVideos_Path())
                CommonUtil.ExecLog(sModuleInfo, "Public Videos Cleaned", 1)
            except Exception, e:
                print e
            try:
                if os.name == 'nt':
                    os.chmod(ComPath.Get_MyMusic_Path(), 0777)
                    sTestStepReturnStatus = self.DeleteMusicFolderContents(ComPath.Get_MyMusic_Path())
                    CommonUtil.ExecLog(sModuleInfo, "My Music Cleaned", 1)
                elif os.name == 'posix':
                    iTunes.CloseiTunes()
                    time.sleep(4)
                    print "By Passing the Deleting of the iTunes folder"
                    ##os.system("rm -rf %s/iTunes"%ComPath.Get_MyMusic_Path())
                    time.sleep(2)
                    iTunes.OpeniTunes()
                    CommonUtil.ExecLog(sModuleInfo, "My Music Cleaned", 1)
                #os.chmod(ComPath.Get_CommonMusic_Path(), 0777)
                #sTestStepReturnStatus = FileUtil.DeleteFolderContents(ComPath.Get_CommonMusic_Path())
                #CommonUtil.ExecLog(sModuleInfo,"Public Music Cleaned",1)
            except Exception, e:
                print e

            try:
                os.chmod(ComPath.Get_My_Documents_Path(), 0777)
                sTestStepReturnStatus = FileUtil.DeleteFolderContents(ComPath.Get_My_Documents_Path())
                CommonUtil.ExecLog(sModuleInfo, "My Documents Cleaned", 1)
                os.chmod(ComPath.Get_CommonMusic_Path(), 0777)
                sTestStepReturnStatus = FileUtil.DeleteFolderContents(ComPath.Get_Common_Documents_Path())
                CommonUtil.ExecLog(sModuleInfo, "Public Documents Cleaned", 1)
            except Exception, e:
                print e
        CommonUtil.ExecLog(sModuleInfo, "Finished Windows My folder files cleanup", 1)
        return sTestStepReturnStatus

