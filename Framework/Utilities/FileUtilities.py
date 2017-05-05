import os,subprocess,shutil


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


def DeleteFolder(sFolderPath):
    """

    :param sFolderPath: name of the path to delete
    :return: True if success,False if failed
    """
    try:
        target = sFolderPath
        if os.path.exists(target) :
            if os.name == 'nt':
                shutil.rmtree(target)
            elif os.name == 'posix':
                cmd = "rm -rf %s/" % target
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
                cmdValue = p.communicate()
            return True
        else:
            return False
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


def ZipFolder(dir, zip_file):
    """
    Zips a given folder, its sub folders and files. Ignores any empty folders
    dir is the path of the folder to be zipped
    zip_file is the path of the zip file to be created
    """
    try:
        import zipfile
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

        zip.close()
        return zip_file
    except Exception, e:
        print "Exception :", e
        return False


def DeleteFile(sFilePath):
    try:
        if os.path.isfile(sFilePath):
            os.remove(sFilePath)
            return True
    except Exception, e:
        return "Error: %s" % e


def copy_folder(src, dest):
    """

    :param src: source of the folder
    :param dest: destination to be copied.
    :return: True if passed or False if failed
    """
    try:
        shutil.copytree(src, dest)
        return True
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
        shutil.copyfile(src, dest)
        return True
    except Exception, e:
        print "Error: %s" % e
        return False
