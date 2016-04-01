'''

'''
import sys
sys.path.append("..")

import os
import ConfigParser
import inspect
import time
import stat
import FileUtilities as FileUtil
import CommonUtil
import Global

class AutoUpdate():

    def __init__(self):
        try:
            sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
            Config = ConfigParser.ConfigParser()
            Config.read('config.ini')
            self.EnableUpdate = Config.getboolean('AutoUpdate', 'EnableUpdate')
            self.AutoUpdate = Config.getboolean('AutoUpdate', 'AutoUpdate')

            #self.ServerSourcePath =  Config.get('Update', 'SourcePath')
            self.Branch = Config.get('AutoUpdate', 'Branch')
            if Global.Environment == 'Test':
                #print "In Test Environment"
                if os.name == 'nt':
                    self.ServerSourcePath = "//ServerSourceFolderPath"
                elif os.name == 'posix':
                    self.ServerSourcePath = "/Volumes/ServerSourceFolderPath"
            elif Global.Environment == 'Production':
                #print "In Production Environment"
                if self.Branch == 'UX':
                    self.ServerSourcePath = "//ServerSourceFolderPath"
                elif self.Branch == 'SCM':
                    if os.name == 'nt':
                        self.ServerSourcePath = "//ServerSourceFolderPath"
                    elif os.name == 'posix':
                        self.ServerSourcePath = "/Volumes/ServerSourceFolderPath"

            #CommonUtil.ExecLog(sModuleInfo,"In %s Environment"%Global.Environment,4)

            ServerConfig = ConfigParser.ConfigParser()
            ServerConfig.read(self.ServerSourcePath + os.sep + 'Framework' + os.sep + 'config.ini')

            self.LocalVersion = Config.get('AutoUpdate', 'Version')
            #CommonUtil.ExecLog(sModuleInfo,"Local Fw Version:%s"%self.LocalVersion,4)
            self.ServerVersion = ServerConfig.get('AutoUpdate', 'Version')
            #CommonUtil.ExecLog(sModuleInfo,"Server Fw Version:%s"%self.ServerVersion,4)
        except Exception, e:
            print "Exception %s" % e
            CommonUtil.ExecLog(sModuleInfo, "Exception:%s" % e, 4)


    def CheckUpdate(self):
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        try:
            #print "Checking if FW Update is available"
            if self.ServerVersion > self.LocalVersion:
                print "A new version of framework is available"
                CommonUtil.ExecLog(sModuleInfo, "A new version of framework is available", 4)
                return True
            else:
                #print "You've the latest framework!"
                #CommonUtil.ExecLog(sModuleInfo,"You have the latest framework!",4)
                return False

        except Exception, e:
            print "Exception %s" % e
            CommonUtil.ExecLog(sModuleInfo, "Exception:%s" % e, 4)
            return False

    def GetUpdate(self):
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        try:
            print "Getting FW Update"
            if os.path.isdir(self.ServerSourcePath):
                ServerFWPath = self.ServerSourcePath + os.sep + 'Framework'
                CommonUtil.ExecLog(sModuleInfo, "Server Path:%s" % ServerFWPath, 4)
                LocalFWPath = os.path.dirname(os.path.realpath(__file__))
                CommonUtil.ExecLog(sModuleInfo, "Local Path:%s" % LocalFWPath, 4)
                #Get all files
                ServerFWFiles = [ os.path.join(ServerFWPath, f) for f in os.listdir(ServerFWPath) if os.path.isfile(os.path.join(ServerFWPath, f)) ]
                LocalFWFiles = [ os.path.join(LocalFWPath, f) for f in os.listdir(LocalFWPath) if os.path.isfile(os.path.join(LocalFWPath, f)) ]
                tempfiles = []
                #Remove .pyc files
                for eachfile in ServerFWFiles:
                    if '.pyc' not in eachfile:
                        tempfiles.append(eachfile)
                ServerFWFiles = tempfiles

                tempfiles = []
                for eachfile in LocalFWFiles:
                    if '.pyc' not in eachfile:
                        tempfiles.append(eachfile)
                LocalFWFiles = tempfiles

                #Find files to be added
                FilesToAdd = []
                for eachfile in ServerFWFiles:
                    if not os.path.isfile(LocalFWPath + os.sep + os.path.basename(eachfile)):
                        FilesToAdd.append(eachfile)

                #Find Files to be deleted
                FilesToDelete = []
                for eachfile in LocalFWFiles:
                    if not os.path.isfile(ServerFWPath + os.sep + os.path.basename(eachfile)):
                        FilesToDelete.append(eachfile)

                #Find files to be updated
                FilesToUpdate = []
                FilesToUpdateWith = []
                for eachServerFile in ServerFWFiles:
                    for eachLocalFile in LocalFWFiles:
                        if os.path.basename(eachServerFile) == os.path.basename(eachLocalFile):
                            #Check if server file has a newer modified time
                            if os.path.getmtime(eachServerFile) > os.path.getmtime(eachLocalFile):
                                FilesToUpdate.append(eachLocalFile)
                                FilesToUpdateWith.append(eachServerFile)
                            break

                #Perform update
                print "starting update"
                #First delete all files which are not needed anymore
                for eachfile in FilesToDelete:
                    if os.path.isfile(eachfile):
                        print "Deleting unwanted file:%s" % os.path.basename(eachfile)
                        CommonUtil.ExecLog(sModuleInfo, "Deleting unwanted file:%s" % os.path.basename(eachfile), 4)
                        os.chmod(eachfile, stat.S_IWRITE)
                        FileUtil.DeleteFile(eachfile)

                for eachfile in FilesToUpdate:
                    if os.path.isfile(eachfile):
                        print "Deleting file to update:%s" % os.path.basename(eachfile)
                        CommonUtil.ExecLog(sModuleInfo, "Deleting file to update:%s" % os.path.basename(eachfile), 4)
                        os.chmod(eachfile, stat.S_IWRITE)
                        FileUtil.DeleteFile(eachfile)

                #Now add the new files & the updated files
                for eachfile in FilesToAdd:
                    if os.path.isfile(eachfile):
                        print "Adding new file:%s" % os.path.basename(eachfile)
                        CommonUtil.ExecLog(sModuleInfo, "Adding new file:%s" % os.path.basename(eachfile), 4)
                        FileUtil.CopyFile(eachfile, LocalFWPath)

                for eachfile in FilesToUpdateWith:
                    if os.path.isfile(eachfile):
                        print "Adding updated file:%s" % os.path.basename(eachfile)
                        CommonUtil.ExecLog(sModuleInfo, "Adding updated file:%s" % os.path.basename(eachfile), 4)
                        FileUtil.CopyFile(eachfile, LocalFWPath)

                return True
            else:
                print "Network path is not accessible"
                return False

        except Exception, e:
            print "Exception %s" % e
            CommonUtil.ExecLog(sModuleInfo, "Exception:%s" % e, 4)
            return False

    def Restart(self):
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        try:
            print "Restarting FW"
            return 'restart'
        except Exception, e:
            print "Exception %s" % e
            return False

    def UpdateProcess(self):
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        try:
            if self.EnableUpdate == False:
                #print "Framework update check is disabled"
                CommonUtil.ExecLog(sModuleInfo, "Framework update check is disabled", 4)
                return False

            if self.CheckUpdate():
                if self.AutoUpdate == False:
                    print "Press 1 to update the Framework or any other key to cancel the update:"
                    UserInput = raw_input()

                    if UserInput == "1":
                        print "Performing Update..."
                        if self.GetUpdate():
                            return self.Restart()
                    else:
                        return False
                    CommonUtil.ExecLog(sModuleInfo, "Framework update check is disabled", 4)
                    return False
                else:
                    print "Performing Auto Update to the newest framework"
                    if self.GetUpdate():
                        return self.Restart()
            else:
                #print "No update available"
                #CommonUtil.ExecLog(sModuleInfo,"No update available",4)
                return True

        except Exception, e:
            print "Exception %s" % e
            CommonUtil.ExecLog(sModuleInfo, "Exception:%s" % e, 4)
            return False

