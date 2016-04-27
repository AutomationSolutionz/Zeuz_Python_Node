# Copyright 2016, Automation Solutionz Inc.
# ---

import subprocess
import os
import sys
import commands

install_str = "sudo pip install -U pip"
apt_get_str = "sudo apt-get install"

br_install_str = "brew install"

# Installation function
def install(type = "", module_name = "", module_version = None, cmd = ""):
    command = ""

    if type == "pip":
        command = "%s %s" % (install_str, module_name)
        if module_version:
            command = "%s==%s" % (command, module_version)
        print "Installing: %s " %command
    elif type == "brew":
        command = "%s %s" % (br_install_str, module_name)
        print "Installing: %s " %command
    elif type == "apt-get":
        command = "%s %s --yes" % (apt_get_str, module_name)
        print "Installing: %s " %command
    else:
        command = cmd
        print "Running: %s " %command

    status, output = commands.getstatusoutput(command)
    print output
    print (78 * '-')

def Installer_With_Pip():
    #pip install
    try:
        install(type = "apt-get", module_name = "python-pip")
    except:
        print "Unable to install pip"

    # Check and install urllib3
    try:
        install(type="pip", module_name="urllib3")
    except:
        print "unable to install/update urllib3"

    # Check and install psutil
    try:
        install(type="pip", module_name="psutil")
    except:
        print "unable to install/update psutil"

    # Check and install requests
    try:
        install(type="pip", module_name="requests")
    except:
        print "unable to install/update requests"

    # Check and install python-dateutil
    try:
        install(type="pip", module_name="python-dateutil")
    except:
        print "unable to install/update dateutil"


def Installer_With_Brew():

    #npm install
    try:
        install(type = "apt-get", module_name = "npm")
    except:
        print "Unable to install npm"

    #brew install
    print "Installing brew installer..."
    try:
        #status, output = commands.getstatusoutput("sudo apt-get install build-essential curl git m4 python-setuptools ruby texinfo libbz2-dev libcurl4-openssl-dev libexpat-dev libncurses-dev zlib1g-dev")
        install(type="apt-get" ,module_name = "build-essential curl git m4 python-setuptools ruby texinfo libbz2-dev libcurl4-openssl-dev libexpat-dev libncurses-dev zlib1g-dev")
    except:
        print "Unable to install brew requirements"

    try:
        install(cmd='ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Linuxbrew/linuxbrew/go/install)" </dev/null')
    except:
        print "Unable to install brew"

    try:
        install(cmd="sudo dpkg --configure -a")
    except:
        print "Unable to configure dpkg"

    try:
        install(cmd="sudo apt-get update -y")
    except:
        print "Unable to update"

    try:
        install(cmd="sudo apt-get upgrade -y")
    except:
        print "Unable to upgrade"

    try:
        install(type="apt-get" ,module_name="build-essential make cmake scons curl git \
                                   ruby autoconf automake autoconf-archive \
                                   gettext libtool flex bison \
                                   libbz2-dev libcurl4-openssl-dev \
                                   libexpat-dev libncurses-dev")
    except:
        print "Unable to install brew requirements"

    try:
        install(cmd="git clone https://github.com/Homebrew/linuxbrew.git ~/.linuxbrew")
    except:
        print "Unable to install brew"

    try:
        install(cmd="export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:/usr/local/lib64/pkgconfig:/usr/lib64/pkgconfig:/usr/lib/pkgconfig:/usr/lib/x86_64-linux-gnu/pkgconfig:/usr/lib64/pkgconfig:/usr/share/pkgconfig:$PKG_CONFIG_PATH")
        install(cmd="export LINUXBREWHOME=$HOME/.linuxbrew")
        install(cmd="export PATH=$LINUXBREWHOME/bin:$PATH")
        install(cmd="export MANPATH=$LINUXBREWHOME/man:$MANPATH")
        install(cmd="export INFOPATH=$LINUXBREWHOME/info:$INFOPATH")
        install(cmd="export PKG_CONFIG_PATH=$LINUXBREWHOME/lib64/pkgconfig:$LINUXBREWHOME/lib/pkgconfig:$PKG_CONFIG_PATH")
        install(cmd="export LD_LIBRARY_PATH=$LINUXBREWHOME/lib64:$LINUXBREWHOME/lib:$LD_LIBRARY_PATH")
        print (78 * '-')
    except:
        print "Unable to install brew"

    # install node
    try:
        install(type="brew", module_name="node")
    except:
        print "unable to install/update node"


class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("Android_Automation_Linux_Setup_Logs.log", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

def Installing_appium():
    print (78 * '-')
    print "Installing appium..."

    try:
        install(cmd="npm install -g appium")
    except:
        print "Unable to install appium"

    try:
        install(type="pip", module_name="Appium-Python-Client")
    except:
        print "Unable to install appium"

    ## Install android sdk
    print "Installing android sdk..."
    try:
        install(type="apt-get", module_name="openjdk-7-jdk")
    except:
        print "Unable to install jdk"

    try:
        install(cmd="wget http://dl.google.com/android/android-sdk_r24.4.1-linux.tgz")
    except:
        print "Unable to download android sdk"

    try:
        install(cmd="tar -xvf android-sdk_r24.4.1-linux.tgz -C $HOME")
    except:
        print "Unable to extract sdk"

    try:
        install(type="apt-get", module_name="android-tools-adb")
    except:
        print "Unable to install adb"

    try:
        install(cmd="android update sdk --no-ui")
    except:
        print "Unable to update sdk"

    try:
        install(cmd="vi ~/.bashrc << EOT")
        install(cmd="export ANDROID_HOME=$HOME/android-sdk-linux")
        install(cmd="export PATH=${PATH}:$HOME/android-sdk-linux/platform-tools:$HOME/android-sdk-linux/tools:$HOME/android-sdk-linux/build-tools/24.4.1/")
        install(cmd="EOT")
        install(cmd="source ~/.bashrc")
    except:
        print "Unable to set android paths"

    #adb
    try:
        install(type="apt-get", module_name="libc6:i386 libstdc++6:i386")
    except:
        print "Unable to install adb"

    #aapt
    try:
        install(type="apt-get", module_name="zlib1g:i386")
    except:
        print "Unable to install aapt"

    #run appium server
    try:
        install(cmd="appium &")
    except:
        print "Unable to run appium server"


def main():
    sys.stdout = Logger()

    ## Install PIP modules
    Installer_With_Pip()

    ## Install brew modules
    Installer_With_Brew()

    ## appium install
    Installing_appium()

if __name__=="__main__":
    main()
