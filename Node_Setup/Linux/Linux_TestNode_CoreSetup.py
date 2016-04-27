# Copyright 2015, Automation Solutionz
# ---

import subprocess
import os
import sys
import commands

install_str = "sudo pip install -U pip"
apt_get_str = "sudo apt-get install"


# Installation function
def install(type = "", module_name = "", module_version = None, cmd = ""):
    command = ""
    
    if type == "pip":
        command = "%s %s" % (install_str, module_name)
        if module_version:
            command = "%s==%s" % (command, module_version)
    elif type == "apt-get":
	command = "%s %s --yes" % (apt_get_str, module_name)
    else:
        command = cmd
    print "Installing: %s " %command
    status, output = commands.getstatusoutput(command)
    print output
    print (78 * '-')

def Installer_With_Pip():

    # Check and install simplejson
    try:
        import simplejson
    except ImportError as e:
	install(type="pip", module_name="simplejson")

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

    try:
        install(type="pip", module_name="python3-xlib")
    except:
        print "unable to install/update %s"%module_name

	# Check and install Xpresser
    try:
	command = "sudo apt-get install python-opencv --yes"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output

	command = "sudo apt-get install python-numpy --yes"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output

	command = "sudo apt-get install python-pyatspi2 --yes"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output

	command = "sudo apt-get install python-cairo --yes"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output

	command = "sudo apt-get install python-gi-cairo --yes"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output
	
	command = "sudo apt-get install ipython --yes"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output
	
	command = "sudo apt-get install python-pygame --yes"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output
	
	command = "sudo apt-get install python-scipy --yes"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output
	
	command = "sudo apt-get install imagemagick --yes"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output
	
	command = "sudo apt-get install scrot --yes"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output
		
	command = "sudo apt-get install python-tk --yes"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output
	
	command = "sudo apt-get install python3-dev --yes"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output
	
	command = "sudo apt-get -f install --yes"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output

	command= "sudo dpkg -i ./backupDriverFiles/python-simplecv_1.3-3_all.deb"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output

	command= "sudo dpkg -i ./backupDriverFiles/python-xpresser_1.1.4-2_all.deb"
    	print "Running: %s " %command
    	status, output = commands.getstatusoutput(command)
    	print output

    except:
        print "unable to install/update %s"%module_name

    try:
        install(type="pip", module_name="pyautogui")
    except:
        print "unable to install/update %s"%module_name



class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("TestNode_Installer_Logs.log", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)


def main():
    sys.stdout = Logger()

## Install PIP modules    
    Installer_With_Pip()

## Install Postgres
    print (78 * '-')
    print ('Postgres Installation')
    print (78 * '-')
    install(type = "apt-get", module_name = "libpq-dev python-dev")
    install(type = "apt-get", module_name = "postgresql postgresql-contrib")

## Check and install psycopg2
    print (78 * '-')
    print ('Install Psycopg2')
    print (78 * '-')
    try:
        import psycopg2
    except ImportError as e:
	install(type="apt-get", module_name="python-psycopg2")

## Easy install funkload
    try:
        import funkload
    except ImportError as e:
        try:
            funkload_easy_install = "sudo easy_install https://github.com/nuxeo/FunkLoad/archive/master.zip"
            install(cmd=funkload_easy_install)
        except:
            print "unable to install/update funkload"

## Install Chrome
    print (78 * '-')
    print ('Chrome Installation')
    print (78 * '-')
    install(type = "apt-get", module_name = "libxss1 libappindicator1 libindicator7")
    install(cmd = "wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
    install(cmd = "sudo dpkg -i google-chrome*.deb")
    install(cmd = "sudo apt-get install -f")

## Install Chrome Drivers
    print (78 * '-')
    print ('Chrome Drivers Installation')
    print (78 * '-')
    install(type = "apt-get", module_name = "unzip")
    install(cmd = "wget -N http://chromedriver.storage.googleapis.com/2.20/chromedriver_linux64.zip")
    install(cmd = "unzip chromedriver_linux64.zip")
    install(cmd = "chmod +x chromedriver")
    install(cmd = "sudo mv -f chromedriver /usr/local/share/chromedriver")
    install(cmd = "sudo ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver")
    install(cmd = "sudo ln -s /usr/local/share/chromedriver /usr/bin/chromedriver")


    #Selenium_Driver_Files_Linux()
    #Installer_With_Exe()
    #Selenium_Driver_Files_Windows()
    #Easy_Installer()

if __name__=="__main__":
	main()
