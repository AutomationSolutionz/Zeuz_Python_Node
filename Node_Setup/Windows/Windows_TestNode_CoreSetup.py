# Copyright 2015, Automation Solutionz
# ---

import subprocess
import shutil
import os
import sys
import commands
from subprocess import PIPE, Popen


install_str = "python -m pip install -U"

def cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0]

# Installation function
def install(type = "", module_name = "", module_version = None, cmd = ""):
    command = ""
    
    if type == "pip":
        command = "%s %s" % (install_str, module_name)
        if module_version:
            command = "%s==%s" % (command, module_version)
    else:
        command = cmd
    print "installing: %s " %command
    print cmdline("python -m pip install -U urllib3")
    #subprocess.call(command, shell=True)
    #status,output = commands.getstatusoutput(str(command))
    #print output

def Installer_With_Pip():

    # Check and install urllib3
    try:
        install(type="pip", module_name="urllib3")
    except:
        print "unable to install/update %s"%module_name  
    
    # Check and install django
    django_version = "1.8.2"
    try:
        install(type="pip", module_name="django", module_version=django_version)
    except:
        print "unable to install/update %s"%module_name  
        
    #pip install -U pyautoit
    try:
        install(type="pip", module_name="pyautoit")
    except:
        print "unable to install/update %s"%module_name  
    
    # Check and install django-celery    
    try:
        install(type="pip", module_name="django-celery")
    except:
        print "unable to install/update %s"%module_name  
    
    # Check and install selenium
    try:
        install(type="pip", module_name="selenium")
    except:
        print "unable to install/update %s"%module_name  
    
    # Check and install psutil
    try:
        install(type="pip", module_name="psutil")
    except:
        print "unable to install/update %s"%module_name  
    
    # Check and install wmi
    if os.name=='nt':
        try:
            install(type="pip", module_name="wmi")
        except:
            print "unable to install/update %s"%module_name  
    
    # Check and install requests
    try:
        install(type="pip", module_name="requests")
    except:
        print "unable to install/update %s"%module_name  
        
    # Check and install six
    try:
        install(type="pip", module_name="six")
    except:
        print "unable to install/update %s"%module_name  
    
    # Check and install pillow
    try:
        install(type="pip", module_name="Pillow")
    except:
        print "unable to install/update %s"%module_name  
    
    # Check and install poster
    try:
        install(type="pip", module_name="poster")
    except:
        print "unable to install/update %s"%module_name  
	
	# Check and install wheel
    try:
        install(type="pip", module_name="wheel")
    except:
        print "unable to install/update %s"%module_name

	# Check and install python-dateutil
    try:
        install(type="pip", module_name="python-dateutil")
    except:
        print "unable to install/update %s"%module_name

	# Check and install dropbox
    try:
        install(type="pip", module_name="dropbox")
    except:
        print "unable to install/update %s"%module_name

def Easy_Installer():
    try:
        psycopg2_easy_install = "easy_install http://www.stickpeople.com/projects/python/win-psycopg/2.6.0/psycopg2-2.6.0.win32-py2.7-pg9.4.1-release.exe"
        #psycopg2_easy_install = "python - m pip install wheel backupDriverFiles\wxPython_common-3.0.2.0-py2-none-any.whl"
        install(cmd=psycopg2_easy_install)
        wx_easy_install="python -m pip install wheel backupDriverFiles\wxPython-3.0.2.0-cp27-none-win32.whl"
        install(cmd=wx_easy_install)
        dateutil_setup="python - m pip install wheel backupDriverFiles\python_dateutil-2.4.2-py2.py3-none-any.whl"
        install(cmd=dateutil_setup)
    except:
        print "unable to install/update wxpython"
    
    # Check and install dateutil.relativedelta 
    try:
        from dateutil.relativedelta import relativedelta
    except ImportError as e:
        try:
            relativedelta_easy_install = "easy_install https://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz"
            install(cmd=relativedelta_easy_install)
        except:
            print "unable to install/update relativedelta"

    try:
        import funkload
    except ImportError as e:
        try:
            funkload_easy_install = "easy_install https://github.com/nuxeo/FunkLoad/archive/master.zip"
            install(cmd=funkload_easy_install)
        except:
            print "unable to install/update ImageGrab"

    # Check and install simplejson
    try:
        import simplejson
    except ImportError as e:
        try: 
            simplejson_easy_install = "easy_install https://github.com/simplejson/simplejson/archive/master.zip"
            install(cmd=simplejson_easy_install)
        except:
            print "unable to install/update win32api"
	
def Installer_With_Exe():
    # Check and install psycopg2
    try:
        psycopg2_easy_install = "easy_install http://www.stickpeople.com/projects/python/win-psycopg/2.6.0/psycopg2-2.6.0.win32-py2.7-pg9.4.1-release.exe"
        install(cmd=psycopg2_easy_install)
    except:
        print "unable to install/update psycopg2"
	    
    # Check and install win32api
    try:
        import win32api
    except ImportError as e:
        try: 
            win32api_easy_install = "easy_install http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/pywin32-219.win32-py2.7.exe/download"
            install(cmd=win32api_easy_install)
        except:
            print "unable to install/update win32api"
        
    #pill
    #http://effbot.org/downloads/PIL-1.1.7.win32-py2.7.exe
    try:
        from PIL import ImageGrab
    except ImportError as e:
        try:
            PIL_easy_install = "easy_install http://effbot.org/downloads/PIL-1.1.7.win32-py2.7.exe"
            install(cmd=PIL_easy_install)
        except:
            print "unable to install/update ImageGrab"
	
def Selenium_Driver_Files_Windows():
    Chrom_Driver_Download()
    Ie_Driver_Download()
    selenium_Server_StandAlone_Driver_Download()
    
def Ie_Driver_Download():
    import urllib3
    http = urllib3.PoolManager()
    download_link = ('http://selenium-release.storage.googleapis.com/2.45/IEDriverServer_Win32_2.45.0.zip')
    print "Downloading latest IE 32 bit driver from: %s" %download_link
    path = r'C:\Python27\Scripts\IEDriverServer_Win32_2.45.0.zip'
    with http.request('GET', download_link, preload_content=False) as r, open(path, 'wb') as out_file:       
        shutil.copyfileobj(r, out_file)
    print "Successfully download the file: %s"%path
    unzip(path,r'C:\Python27\Scripts')   
    
def Chrom_Driver_Download():
    import urllib3
    http = urllib3.PoolManager()
    try:
        print "Getting latest version of chrome driver"
        r = http.request('GET', 'http://chromedriver.storage.googleapis.com/LATEST_RELEASE')
        latest_version = r.data.split('\n')[0]
        print "latest version is: %s"%latest_version
    except:
        print "Unable to get the latest version."
        return
    download_link = ('http://chromedriver.storage.googleapis.com/%s/chromedriver_win32.zip')%latest_version
    print "Downloading latest Chrom 32 bit driver from: %s" %download_link
    path = r'C:\Python27\Scripts\chromedriver_win32.zip'
    try:
        chrom_driver_32 = urllib.URLopener()
        chrom_driver_32.retrieve ("http://chromedriver.storage.googleapis.com/%s/chromedriver_win32.zip"%latest_version, path)
        print "Successfully download the file: %s"%path     
        unzip(path,r'C:\Python27\Scripts')  
    except:
        print "Unable to download: % "%download_link

def selenium_Server_StandAlone_Driver_Download():
    import urllib3
    http = urllib3.PoolManager()
    download_link = ('http://selenium-release.storage.googleapis.com/2.45/selenium-server-standalone-2.45.0.jar')
    print "Downloading latest selenium_Server_StandAlone for Safari Browser: %s" %download_link
    path = r'C:\Python27\Scripts\selenium-server-standalone-2.45.0.jar'
    
    try:
        with http.request('GET', download_link, preload_content=False) as r, open(path, 'wb') as out_file:       
            shutil.copyfileobj(r, out_file)  
        print "Successfully download the file: %s"%path
    except:
        print "Unable to download: % "%download_link
        
def unzip(zipFilePath, destDir):
    import os
    import zipfile
    zfile = zipfile.ZipFile(zipFilePath)
    print "Unzipping %s to %s"%(zipFilePath,destDir)
    for name in zfile.namelist():
        (dirName, fileName) = os.path.split(name)
        if fileName == '':
            # directory
            newDir = destDir + '/' + dirName
            if not os.path.exists(newDir):
                os.mkdir(newDir)
        else:
            # file
            fd = open(destDir + '/' + name, 'wb')
            fd.write(zfile.read(name))
            fd.close()
    zfile.close()


class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("TestNode_Installer_Logs.log", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)


def main():
    sys.stdout = Logger()
    
    Installer_With_Pip()
    Installer_With_Exe()
    Selenium_Driver_Files_Windows()
    Easy_Installer()


if __name__=="__main__":
	main()
