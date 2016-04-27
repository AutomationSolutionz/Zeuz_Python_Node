# Copyright 2015, Automation Solutionz
# ---

import subprocess
import shutil
import os


install_str = "python -m pip install -U"

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
    subprocess.call(command, shell=True)

def Installer_With_Pip():
    pass
    
    # Check and install appscript
#    try:
#        install(type="pip", module_name="appscript")
#    except:
#        print "unable to install/update %s"%module_name  

def Easy_Installer():

    try:
        speech_easy_install = "pip install SpeechRecognition"
        install(cmd=speech_easy_install)
    except:
        print "unable to install/update SpeechRecognition"

    try:
        import uiautomator
    except ImportError as e:
        try:
            ui_easy_install="easy_install https://github.com/xiaocong/uiautomator/archive/master.zip"
            install(cmd=ui_easy_install)
        except:
            print "unable to install/update uiautomator"
	
def Installer_With_Exe():
    try:
        import pyaudio
    except ImportError as e:
        try:
            pyaudio_easy_install = "easy_install http://people.csail.mit.edu/hubert/pyaudio/packages/pyaudio-0.2.8.py27.exe"
            install(cmd=pyaudio_easy_install)
        except:
            print "unable to install/update pyaudio"

        
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

def appium():
	#first give the ant setup
	ant_path=os.getcwd()+os.sep+'backupDriverFiles'+os.sep+'Android'+os.sep+'apache-ant-1.9.5-bin.zip'
	unzip(ant_path,'C:\Python27\Lib\site-packages')
	os.environ['ANT_HOME']='C:\Python27\Lib\site-packages\apache-ant-1.9.5\bin'
	os.environ['PATH']+='C:\Python27\Lib\site-packages\apache-ant-1.9.5\bin'
	maven_path=os.getcwd()+os.sep+'backupDriverFiles'+os.sep+'Android'+os.sep+'apache-maven-3.3.3-bin.zip'
	unzip(maven_path,'C:\Python27\Lib\site-packages')
	os.environ['PATH']+='C:\Python27\Lib\site-packages\apache-maven-3.3.3\bin;'
	os.system(os.getcwd().replace('\\','/')+'/backupDriverFiles/Android/appium.bat')

def main():
    Installer_With_Pip()
    if os.name == 'nt':
        Installer_With_Exe()
        Selenium_Driver_Files_Windows()
        Easy_Installer()
	appium()


if __name__=="__main__":
	main()
