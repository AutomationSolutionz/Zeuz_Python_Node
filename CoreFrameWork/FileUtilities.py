# coding=utf-8
import sys
sys.path.append("..")
import datetime
import os, subprocess
import shutil
import stat, time
import inspect
import CommonUtil



if os.name == 'nt':
    from PCDesktop import WinCommonFoldersPaths as ComPath
    import win32api
    from win32com.shell import shell, shellcon
elif os.name == 'posix':
    from MacDesktop import MacCommonFoldersPaths as ComPath

def PCtoMACpathchange(currentFilePath):
    return currentFilePath

def WriteResultLog(strWrite, sFilePath):
    fileName = sFilePath
    fileObj = open(fileName, 'a')
    s = str(str(datetime.now()) + " : " + strWrite + '\n')
    fileObj.write(s)
    fileObj.close()


#Creating a new empty Folder

def CreateEmptyFolder(folderPath, newFolder):
    """
    Description: CreateEmptyFolder function will take path and folder name. It will delete folder first if folder is exist.
    """
    try:
        isFolder = os.path.isdir(folderPath + os.sep + newFolder)
        if isFolder:
            try:
                for Root, Folders, Files in os.walk(folderPath + os.sep + newFolder):
                    for file in Files:
                        os.unlink(os.path.join(Root, file))
                    for Folder in Folders:
                        shutil.rmtree(os.path.join(Root, Folder))

                    os.removedirs(folderPath + os.sep + newFolder)
            except Exception, e:
                    return "Error: %s" % e
        os.makedirs(folderPath + os.sep + newFolder)
        return True

    except Exception, e:
        return "Error: %s" % e

def CreateFolder(folderPath, forced=True):
    """
    Description: CreateFolder function will take path containing the folder name. It will delete folder first if folder is exist.
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
            return True
    except Exception, e:
        return "Error: %s" % e

def WriteLineToFile(sFilePath, line):
    try:
        if os.path.isfile(sFilePath):
            print "File exists"
            f = open(sFilePath, 'w')
            f.write(line + '\n')
            f.close()
            return True
        else:
            print "File not found"
            return False
    except Exception, e:
        return "Error: %s" % e

def RemoveLineFromFile(sFilePath, line):
    try:
        if os.path.isfile(sFilePath):
            print "File exists"
            f = open(sFilePath, 'r')
            lines = f.readlines()
            f.close()
            f = open(sFilePath, 'w')
            for eachline in lines:
                if eachline != line + '\n':
                    f.write(line + '\n')
            f.close()
            return True
        else:
            print "file not found"
            return False
    except Exception, e:
        return "Error: %s" % e

def DeleteFolder(sFolderPath):
    try:
        """ OLD CODE
        isFolder = os.path.isdir(sFolderPath)
        if isFolder:
                for Root,Folders,Files in os.walk(sFolderPath):
                    for file in Files:
                        print os.unlink(os.path.join(Root,file))

                    for Folder in Folders:
                        shutil.rmtree(os.path.join(Root,Folder))

                    os.removedirs(sFolderPath)
                    return True
        """

        target = sFolderPath
        if os.path.exists(target) :
            #subprocess.check_call(('attrib -R ' + target + os.sep + '* /S').split())
            if os.name == 'nt':
                shutil.rmtree(target)
            elif os.name == 'posix':
                # Until a solution for delete ACL file on the MAC is found..... skipping the removal of files
                #os.remove(target)
                #shutil.rmtree(target)
                #print "PROBLEM: Unable to remove file for the MAC OS 'Operation not permitted'"
                cmd = "rm -rf %s/" % target
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
                #p.wait()
                cmdValue = p.communicate()

            return True
        else:
            return False
    except Exception, e:
        return "Error: %s" % e

def DeleteFolderContents(sFolderPath):
    """
    Description: DeleteFolderContents deletes contents of the folder, but keeps the top parent folder
    Parameters: sFolderPath is folder path of the target Folder
    Example: DeleteFolderContents("C:\\Users\\Name\\Pictures")
    Result:  "Pictures folder will be empty

    Note:
    """
    try:
        if os.path.isdir(sFolderPath):
            for root, dirs, files in os.walk(sFolderPath):
                for f in files:
                    try:
                        #print f
                        #Dont delete desktop.ini file found in system folders such as 'my pictures'
                        if f != 'desktop.ini':
                            os.unlink(os.path.join(root, f))
                    except Exception, e:
                        print "Exception:", e
                for d in dirs:
                    try:
                        #print d
                        if os.name == 'nt':
                            shutil.rmtree(os.path.join(root, d))
                        elif os.name == 'posix':
                            os.remove(os.path.join(root, d))
                    except Exception, e:
                        print "Exception:", e
            #return "Pass"
        return "Pass"
#        else:
#            return "Warning"    

    except Exception, e:
        print "Error: %s" % e
        return "Critical"


def RenameFolder(sFolderPath, sOldName, sNewName):
    """
    Description: RenameFolder changes the name of the Folder from sOldName to sNewName at sFolderPath
    Parameters: sFolderPath is folder path of the target Folder
                sOldName is the current name of the target Fodler
                sNewName is the new name of the target folder
    Example: RenameFile("C:\\Users\\Name\\Pictures","MyFolder","Change My Folder")
    Result:  "C:\\Users\\Name\\Pictures\\Change My Folder"

    Note: sOldName,sNewName is case sensitive
    """
    try:
        if os.path.isdir(sFolderPath):
            for Root, Folders, Files in os.walk(sFolderPath):
                    for Folder in Folders:
                        if cmp(Folder, sOldName) == 0:
                            os.rename(os.path.join(Root, sOldName), os.path.join(Root, sNewName))
                            return True

    except Exception, e:
        return e

def CopyFolder(sSourceFolderPath, sDesFolderPath):
    """
    Description: CopyFolder copies folder from source path to destination path
    Note: Add required folder name in both paths
    Example: CopyFolder("C:\\Users\\SoureFolder","D:\\Program\\MyPicture\\SourceFolder")
    SourceFolder folder will be copied form C:\\.. to D:\\..
    """
    try:
        if os.path.isdir(sSourceFolderPath):
            if os.path.isdir(sDesFolderPath):
                DeleteFolder(sDesFolderPath)
                shutil.copytree(sSourceFolderPath, sDesFolderPath)
                return True
            else:
                shutil.copytree(sSourceFolderPath, sDesFolderPath)
                return True
    except Exception, e:
        return "Error: %s" % e

def CopyFolder2(sSourceFolderPath, sDesFolderPath):
    """
    @summary: The difference between CopyFolder & CopyFolder2 is that this fn is using
    a custom *CopyTree* fn taken from shutil and modified to ignore a windows access denied
    error due to pythons os.utime error while copying to sd card
    Description: CopyFolder copies folder from source path to destination path
    Note: Add required folder name in both paths
    Example: CopyFolder("C:\\Users\\SoureFolder","D:\\Program\\MyPicture\\SourceFolder")
    SourceFolder folder will be copied form C:\\.. to D:\\..
    """
    try:
        if os.path.isdir(sSourceFolderPath):
            if os.path.isdir(sDesFolderPath):
                DeleteFolder(sDesFolderPath)
                CopyTree(sSourceFolderPath, sDesFolderPath)
                return True
            else:
                CopyTree(sSourceFolderPath, sDesFolderPath)
                return True
    except Exception, e:
        return "Error: %s" % e

def CopyTree(src, dst, symlinks=False, ignore=None):
    """
    ***Modified from shutil to use ourown Copy2 & CopyStat fns****
    Recursively copy a directory tree using copy2().

    The destination directory must not already exist.
    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    XXX Consider this example code rather than the ultimate tool.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                CopyTree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                try:
                    Copy2(srcname, dstname)
                except Exception, e:
                    if os.name == 'nt':
                        #Copy using windows api's if python copy fails in the above call
                        WinCopy(srcname, dstname)
                    elif os.name == 'posix':
                        print "Exception:", e
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error, err:
            errors.extend(err.args[0])
        except EnvironmentError, why:
            errors.append((srcname, dstname, str(why)))
    try:
        CopyStat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise Error, errors

def Copy2(src, dst):
    """
    ***Modified from shutil to use our own CopyStat fn****
    Copy data and all stat info ("cp -p src dst").

    The destination may be a directory.

    """
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    #shutil.copyfile(src, dst)
    CopyFile2(src, dst)
    try:
        CopyStat(src, dst)
    except Exception, e:
        print "CopyStat Exception:", e
        pass

def WinCopy(src, dst):
    try:
        print shell.SHFileOperation((0, shellcon.FO_COPY, src, dst, shellcon.FOF_SILENT | shellcon.FOF_NOCONFIRMATION | shellcon.FOF_NOERRORUI | shellcon.FOF_NOCONFIRMMKDIR, None, None))
    except Exception, e:
        print "WinCopy exception:", e
def CopyStat(src, dst):
    """
    ***Modified from shutil to ignore the windows access denied error***
    Copy all stat info (mode bits, atime, mtime, flags) from src to dst"""
    st = os.stat(src)
    mode = stat.S_IMODE(st.st_mode)
    if hasattr(os, 'utime'):
        ###IGNORES THE WINDOWS ACCESS DENIED ERROR. EVERYTHING ELSE REMAINS SAME###
        try:
            os.utime(dst, (st.st_atime, st.st_mtime))
        except WindowsError:
            pass
    if hasattr(os, 'chmod'):
        os.chmod(dst, mode)
    if hasattr(os, 'chflags') and hasattr(st, 'st_flags'):
        try:
            os.chflags(dst, st.st_flags)
        except OSError, why:
            if (not hasattr(errno, 'EOPNOTSUPP') or
                why.errno != errno.EOPNOTSUPP):
                raise

def MoveFolder(sSourceFolderPath, sDesFolderPath):
    """
    Description: MoveFolder move folder from source path to destination path
    Note: Add required folder name in both paths
    Example: MoveFolder("C:\\Users\\SoureFolder","D:\\Program\\MyPicture\\SourceFolder")
    SourceFolder folder will be moved form C:\\.. to D:\\..
    """
    try:
        if os.path.isdir(sSourceFolderPath):
            if os.path.isdir(sDesFolderPath):
                DeleteFolder(sDesFolderPath)
                shutil.move(sSourceFolderPath, sDesFolderPath)
                return True
            else:
                shutil.move(sSourceFolderPath, sDesFolderPath)
                return True
    except Exception, e:
        return "Error: %s" % e

#def DeleteFile(sFolderPathOfTheFile,sFileNameWithExtension):
#    try:
#        isFolder = os.path.isdir(sFolderPathOfTheFile)
#        if isFolder:
#            for Root,Folders,Files in os.walk(sFolderPathOfTheFile):
#                for file in Files:
#                    if file.find(sFileNameWithExtension) != -1:
#                        #os.unlink(os.path.join(Root,file))
#                        #raw_input("Hit Enter to ...")
#                        os.remove(os.path.join(Root,file))
#                        #os.remove(sFolderPathOfTheFile+sFileNameWithExtension)
#                        return True
#    except Exception,e:
#        return "Error: %s" %e

def DeleteFile(sFilePath):
    try:
        if os.path.isfile(sFilePath):
            os.remove(sFilePath)
            return True
    except Exception, e:
        return "Error: %s" % e

def CopyFile(sSourceFilePath, DesPath):
    """
    Description: CopyFile copies file from source path to destination path
    Note: Add required folder name in both paths
    Example: CopyFile("C:\\Users\\SoureFolder\\filename.extension","D:\\Program\\MyPicture\\DestinationFolder")
    SourceFolder file will be copied form C:\\.. to D:\\..
    """
    try:

        """
         Copy the file src to the file or directory dst. If dst is a directory,
         a file with the same basename as src is created (or overwritten) in the directory specified.
         Permission bits are copied. src and dst are path names given as strings.
        """
        if os.path.isdir(DesPath) != True:
            print "Destination dir not found"
            return False
        shutil.copy(sSourceFilePath, DesPath)
        return True

    except Exception, e:
        print "Error:", e
        return "Error: %s" % e

def CopyFile2(src, dst, buffer_size=10485760, perserveFileDate=True):
    '''
    Copies a file to a new location. Much faster performance than Apache Commons due to use of larger buffer
    @param src:    Source File
    @param dst:    Destination File (not file path)
    @param buffer_size:    Buffer size to use during copy
    @param perserveFileDate:    Preserve the original file date
    '''
    try:
        #    Check to make sure destination directory exists. If it doesn't create the directory
        dstParent, dstFileName = os.path.split(dst)
        if(not(os.path.exists(dstParent))):
            os.makedirs(dstParent)

        #    Optimize the buffer for small files
        buffer_size = min(buffer_size, os.path.getsize(src))
        if(buffer_size == 0):
            buffer_size = 1024

        if shutil._samefile(src, dst):
            raise shutil.Error("`%s` and `%s` are the same file" % (src, dst))
        for fn in [src, dst]:
            try:
                st = os.stat(fn)
            except OSError:
                # File most likely does not exist
                pass
            else:
                # XXX What about other special files? (sockets, devices...)
                if shutil.stat.S_ISFIFO(st.st_mode):
                    raise shutil.SpecialFileError("`%s` is a named pipe" % fn)
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                shutil.copyfileobj(fsrc, fdst, buffer_size)

        if(perserveFileDate):
            CopyStat(src, dst)

        return True

    except Exception, e:
        print "Error:", e
        if os.name == 'nt':
            try:
                WinCopy(src, dst)
                return True
            except Exception, e1:
                print "WinCopy Error:", e1
        return "Error: %s" % e

def RenameFile(sFilePath, sOldName, sNewName):
    """
    Description: RenameFile changes the name of the file from sOldName to sNewName at sFilePath
    Parameters: sFilePath is folder path of the target file
                sOldName is the current name of the target file
                sNewName is the new name of the target file
    Example: RenameFile("C:\\Users\\Name\\Pictures","Autumn Leaves.jpg","Changed Name.jpg")
    """
    try:
        if os.path.isdir(sFilePath):
            for FileName in os.listdir(sFilePath):
                if FileName.find(sOldName) != -1:
                    os.rename(os.path.join(sFilePath, FileName), os.path.join(sFilePath, sNewName))
                    return True
    except Exception, e:
        return e


def CopyTestDataToLocalPC(FileList):
    """
    @summary: Copies file from Network storage to the automation test data folder in local pc
    @param FileList: This can either be a list of full file paths or a folder path
    @return: Returns False if any error happened or if no files found. Returns a list with new file path
    for the copied files
    """
    try:
        sDestPathOnPC = ComPath.Get_Desktop_Path() + os.sep + 'Temp' + os.sep + 'AutomationTestData'

        #Make Destination Directory on local PC
        CreateFolder(sDestPathOnPC, False)
        FilesToCopy = []
        FilesCopied = []

        #Start copying files
        for item in FileList:
            if os.name == 'posix':
                filepath = ConvertWinPathToMac(item)
            else:
                filepath = item

            #Check if copying file or folder                
            if os.path.isfile(filepath):
                sfileDest = sDestPathOnPC + os.sep + os.path.basename(filepath)
                retvalue = CopyFile2(filepath, sfileDest)
                if retvalue == True:
                    if os.name == 'posix':
                        os.system("chflags nouchg " + "\"" + sfileDest + "\"")
                    elif os.name == 'nt':
                        os.chmod(sfileDest, stat.S_IWRITE)
                    FilesCopied.append(sfileDest)
                else:
                    print "Error in copying file:", filepath
                    return False
            elif os.path.isdir(filepath):
                sfileDest = sDestPathOnPC + os.sep + os.path.basename(filepath)
                retvalue = CopyFolder(filepath, sfileDest)
                if retvalue == True:
                    os.chmod(sfileDest, stat.S_IWRITE)
                    FilesCopied.append(sfileDest)
                else:
                    print "Error in copying file:", filepath
                    return False
            else:
                print "File not found : ", filepath
                return False
        if len(FilesCopied) > 0:
            return FilesCopied
        else:
            return False
    except Exception, e:
        print "Exception : ", e
        return False

def ConvertNetworkPathToLocalPC(sNetworkPath):
    """
    Description: Creates a folder on the local PC's Desktop called 'AutomationTestData' and copies the test data from the network storage to this local directory.
    Parameters:
    Example: ConvertNetworkPathToLocalPC(FileList)

    """
    if os.name == 'posix':
        filepath = ConvertWinPathToMac(sNetworkPath)
    else:
        filepath = sNetworkPath

    sDestDir = "AutomationTestData"
    sfolderPath = ComPath.Get_Desktop_Path() + os.sep + "Temp"
    sDestPathOnPC = ComPath.Get_Desktop_Path() + os.sep + "Temp" + os.sep + sDestDir

    temp = os.path.basename(filepath)
    sfileDest = "%s" % sDestPathOnPC + os.sep + temp

    #Taking care of the single quote case
    if '"' in sfileDest:
        sfileDest = sfileDest.replace('"', '')
    #print "Network Storage Path %s"%filepath
    #print "Local Storage Path %s"%sfileDest

    return sfileDest

def GetFilesNameFromFolder(sFolderPathOfTheFile, sExtension='All'):

    """
    GetFilesName: This function takes two arguments, one is folder path as string of required file name and second one is extention of the required file name.
                  if the extension argument is left empty the functin will return all files names in the specified folder path.
    Return:       This  function returns the file name in list formate
    """
    FilesName, p = [], ""
    try:
        isFolder = os.path.isdir(sFolderPathOfTheFile)
        if isFolder:
            for Root, Folders, Files in os.walk(sFolderPathOfTheFile):
                for file in Files:
                    p = os.path.splitext(file)
                    if sExtension == 'All':
                        FilesName.append(p[0])

                    elif p[1] == '.%s' % sExtension:
                        FilesName.append(p[0])
                        #os.unlink(os.path.join(Root,file))
                        #raw_input("Hit Enter to ...")
                        #os.remove(os.path.join(Root,file))
                        #os.remove(sFolderPathOfTheFile+sFileNameWithExtension)
            return FilesName
    except Exception, e:
        return "Error: %s" % e

def SearchFiles(searchFolder, *searchTag):
    """
    Search for files in a given folder recursively and returns the full file path as a list.
    Either give full or partial file name or extension as input
    Ex: SearchFiles("C:\\Windows\Temp",'.dmp','DMP')
    """
    try:
        fileList = []
        filesFound = []
        for root, subFolders, files in os.walk(searchFolder):
            for file in files:
                fileList.append(os.path.join(root, file))

        for eachFilePath in fileList:
            for eachTag in searchTag:
                if (eachTag in eachFilePath):
                    filesFound.append(eachFilePath)
        return filesFound
    except Exception, e:
        print "Exception:", e
        return False

def GetlatestFolder(sPathToFolder):

    try:
        os.chdir(sPathToFolder)
        folders = os.listdir(sPathToFolder)
        FoldersList = []
        for eachFolder in folders:
            if os.path.isfile("%s\%s" % (sPathToFolder, eachFolder)) == False:
                FoldersList.append(eachFolder)
        FoldersList.sort(key=lambda x: os.path.getmtime(x))
        return FoldersList[-1]

    except Exception , e:
        return e

def GetOldestFolder(sPathToFolder):

    try:
        os.chdir(sPathToFolder)
        folders = os.listdir(sPathToFolder)
        FoldersList = []
        for eachFolder in folders:
            if os.path.isfile("%s\%s" % (sPathToFolder, eachFolder)) == False:
                FoldersList.append(eachFolder)
        FoldersList.sort(key=lambda x: os.path.getmtime(x))
        return FoldersList[0]

    except Exception , e:
        return e


def GetlatestFile(sPathToFile):

    try:
        os.chdir(sPathToFolder)
        files = os.listdir(sPathToFolder)
        files = [os.path.join(search_dir, f) for f in files]
        files.sort(key=lambda x: os.path.getmtime(x))
        return files[-1]

    except Exception , e:
        return e


def GetOldestFile(sPathToFile):

    try:
        os.chdir(sPathToFolder)
        files = os.listdir(sPathToFolder)
        files = [os.path.join(search_dir, f) for f in files]
        files.sort(key=lambda x: os.path.getmtime(x))
        return files[1]

    except Exception , e:
        return e



def CopyAllFilesFromSourceToDestFolder(src, dest):

    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, dest)
#            elif (os.path.isdir(full_file_name)):
#                shutil.copy(full_file_name, dest)
        return True

    except Exception, e:
        print "%s > Exception:  (%s)" % (sModuleInfo, e)
        CommonUtil.ExecLog(sModuleInfo, "Exception:  (%s)" % e, 3)
        return "Critical"

def ChangePermission(sFolderPath):
    """
    Description: DeleteFolderContents deletes contents of the folder, but keeps the top parent folder
    Parameters: sFolderPath is folder path of the target Folder
    Example: DeleteFolderContents("C:\\Users\\Name\\Pictures")
    Result:  "Pictures folder will be empty

    Note:
    """
    try:
        if os.path.isdir(sFolderPath):
            for root, dirs, files in os.walk(sFolderPath):
            #for dirs, files in sFolderPath:
                for d in dirs:
                    dirPath = root + os.sep + d
                    os.chmod(dirPath, stat.S_IWRITE)
                for f in files:
                    file = root + os.sep + f
                    os.chmod(file, stat.S_IWRITE)

            #return "Pass"
        return "Pass"
#        else:
#            return "Warning"    

    except Exception, e:
        print "Error: %s" % e
        return "Critical"

def UnzipFolder(sFolderPath):

    """
        Description: UnzipFolder function extract the file from the folder
        Arguments: Path to folder including zipped folder without any extension
        Return: True when pass or exception

    """
    try:
        import zipfile

        zip = zipfile.ZipFile(sFolderPath + ".zip", "r")
        zip.extractall(path=sFolderPath)
        zip.close()
        return True

    except Exception, e:
        return e

def UntarFolder(sFolderPath):

    """
        Description: UntarFolder function extract the file from the folder
        Arguments: Path to folder including zipped folder without any extension
        Return: True when pass or exception

    """
    try:
        import tarfile

        zip = tarfile.open(sFolderPath + ".tar", "r")
        zip.extractall(path=sFolderPath)
        zip.close()
        return True

    except Exception, e:
        return e

def getFileVersion(fname):
    """
    for Windows fname is the full file path for eg, getFileVersion("C:\\Program Files (x86)\\Research In Motion\\BlackBerry Desktop\\Rim.Desktop.exe")
    for Mac fname is just the app name for eg, iTunes, BlackBerry Desktop Software
    """
    if os.name == 'nt':
        return getFileVersion_Win(fname)
    elif os.name == 'posix':
        return getFileVersion_Mac(fname)

def getFileVersion_Win(fname):

    """
    Description: Read all properties of the given file return them as a dictionary.
    The code has been modified to output only application name and version.

    Parameters: fName is folder path of the target Folder

    """
    propNames = ('Comments', 'InternalName', 'ProductName',
        'CompanyName', 'LegalCopyright', 'ProductVersion',
        'FileDescription', 'LegalTrademarks', 'PrivateBuild',
        'FileVersion', 'OriginalFilename', 'SpecialBuild')

    props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}

    try:
        # backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc
        fixedInfo = win32api.GetFileVersionInfo(fname, '\\')
        props['FixedFileInfo'] = fixedInfo
        props['FileVersion'] = "%d.%d.%d.%d" % (fixedInfo['FileVersionMS'] / 65536,
                fixedInfo['FileVersionMS'] % 65536, fixedInfo['FileVersionLS'] / 65536,
                fixedInfo['FileVersionLS'] % 65536)

        # \VarFileInfo\Translation returns list of available (language, codepage)
        # pairs that can be used to retreive string info. We are using only the first pair.
        lang, codepage = win32api.GetFileVersionInfo(fname, '\\VarFileInfo\\Translation')[0]

        # any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle
        # two are language/codepage pair returned from above

        strInfo = {}
        for propName in propNames:
            strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, propName)
            #print strInfoPath
            #print fname
            #print win32api.GetFileVersionInfo(fname, strInfoPath)
            strInfo[propName] = win32api.GetFileVersionInfo(fname, strInfoPath)

        props['StringFileInfo'] = strInfo
    except Exception, e:
        print e
        return False
    #props has all the info that this program collects.  Feel free to add additional info if need be 
    string_info = props["StringFileInfo"]
    AppName = string_info["FileDescription"]
    AppVersion = string_info["ProductVersion"]
    AppInfo = AppName + ": " + AppVersion
    #return AppInfo
    return AppVersion

def getFileVersion_Mac(appName):

    """
    getFileVersionMac('BlackBerry Desktop Software')
    Returns Version of the app if it found the app and
    """
    import plistlib
    from subprocess import Popen, PIPE

    try:
        #terminal command to get all apps
        command = ["system_profiler", "-xml", "SPApplicationsDataType"]
        task = Popen(command, stdout=PIPE)
        (stdout, unused_stderr) = task.communicate()

        apps = plistlib.readPlistFromString(stdout)[0]["_items"]

        for app in apps:
            if app["_name"] == appName:
                print "App found: ", app["_name"]
                if "version" in app:
                    print "Version found: ", app["version"]
                    return app["version"]
                else:
                    print "Version not available"
                    return "NA"
                break
        print "App not found: ", appName
        return False
    except Exception, e:
        print "Exception: ", e
        return False

def ConvertWinPathToMac(WinFilePath):
    return WinFilePath

def GetFileListFromFolder(srootDir):
    """
    @summary: Gets a list of all files from the given folder path. also recurses sub folders
    @return: FileList with all files full path. if nothing is found, then empty file list. if path doesnt exist, then False
    """
    try:
        fileList = []
        #get all files in the folder'
        for root, subFolders, files in os.walk(srootDir):
            for folder in subFolders:
                fileList.append(os.path.join(root, folder))
            for file in files:
                fileList.append(os.path.join(root, file))
        return fileList
    except Exception, e:
        print "Exception : ", e
        return False

def DelFolderWithExpTime(ParentFolder, KeyWordInFolder, ExpiredInMin):
    """
    Description:
    This module is used to delete a folder based on time created.  You will need to pass the parent folder, keyword in the
    folder name and the expiry time (the time it has been created for).

    Parameter Description:
    - ParentFolder = main folder that you want to search your folders
    - KeyWordInFolder = string value in the folder name
    - ExpiredInMin = int value of duration in minutes

    Example:
    ParentFolder = 'C:\Python27\WorkSpace\DjangoFramework10\site_media'
    KeyWordInFolder = 'graph'
    ExpiredInMin = 30
    call the below function:
    DelFolderWithExpTime(ParentFolder, KeyWordInFolder, ExpiredInMin)


    ======= End of Instruction: =========

    """

    try:
        folder_list = os.listdir(ParentFolder)
        for Folder in folder_list:
            if KeyWordInFolder in Folder:
                temp_folder = ParentFolder + "\\" + Folder
                current_time = (time.time()) / 60
                created_time = (os.path.getmtime(temp_folder)) / 60
                delta_time = current_time - created_time
                print delta_time
                if delta_time > ExpiredInMin:
                    try:
                        shutil.rmtree(temp_folder)
                        print "Deleted folder %s as it has been identified to be created over %s minutes" % (temp_folder, delta_time)
                    except Exception, e:
                        print "Error in deleting file: %s" % e
    except Exception, e:
        print "Error with delete function: %s" % e

def SearchStringInFile(file_path, search_string, delay=120):

    """
    Description:
    This module is used to search for a string in a file.  It will look for 120 times with 1 second delay in the middle
    until it finds the string.  If it doesnt find the string, it will return 'False', and 'True' if it finds it.  If there is
    an error, it will return 'error'


    Parameter Description:
    - file_path = full file path of your file in interest
    - search_string = string that you are looking for in that file
    - delay = how many times and how long you want to look for the file.  default is 120 seconds/tries

    Example:
    file_path = "C:\Users\ihossain\Music\iTunes\iTunes Music Library.xml"
    search_string = "Ø£ÙŽØ¨Ù’Ø¬ÙŽØ¯Ù�ÙŠÙŽÙ‘Ø© Ø¹ÙŽØ±ÙŽØ¨Ù�ÙŠÙŽÙ‘"
    search = SearchStringInFile(file_path, search_string, 3) -> it will search three times and total duration would be maximum of 3 seconds.
    if it finds before that time, it will exit out.


    ======= End of Instruction: =========

    """

    try:
        print "Checking file path...: " + file_path
        for x in range (0, 120):
            Existinance_of_Library = os.path.exists(file_path)
            if Existinance_of_Library == False:
                time.sleep(1)
            else:
                print "Found the file you are looking for ... waited for: %s seconds" % x
                break
            if x == 119:
                print "Did not find the file after waiting for: %s seconds " % x
                return "error"
        #We now search for the string the file
        for x in range (0, delay):
            datafile = file(file_path)
            time.sleep(1)
            search_result = False
            for line in datafile:
                if search_string in line:
                    search_result = True
                    print "Found your string: " + search_string + " in the given file path: " + file_path + " Waited for: %s seconds" % x
                    return search_result
        if search_result == False:
            print "Waited for %s seconds, but searched item was never found" % delay
        return search_result
    except Exception, e:
        print "There was an error with file path or other execution error.  See below error code for more info: "
        print e
        return "error"


def main():
    pass

if __name__ == "__main__":
    main()
