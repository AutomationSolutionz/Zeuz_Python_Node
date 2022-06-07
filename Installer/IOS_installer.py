# Copyright 2016, Automation Solutionz
# ---


import os
import sys
import subprocess
import getpass

install_str = "pip3 install -U"
sudo_pass = ''
logfile = "TestNode_iOS_Logs.log"

# Create log file if it doesn't exist already
if not os.path.exists(logfile):
    with open(logfile, 'w'): pass

try:
    import subprocess  # We need commands to do anything, so if it's not installed, use subprocess to install it first
except:
    print("Module Commands is missing. I'll attempt to install it manually. \n")
    import subprocess  # Try to import again


# Import local modules
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')) # Set the path, so the can find the modules
from installation_files.Crossplatform import CommonUtils

def check_if_ran_with_sudo():
    global sudo_pass
    sudo_pass = None
    if os.getuid() == 0:
        return True
    else:
        max_try = 3
        counter=0
        have_pass = False
        while counter != max_try:
            print("This program needs sudo access.  please provide sudo password")
            global passwd
            passwd = getpass.getpass()
            print("checking to see if you have entered correct sudo")
            command = "echo 'sudo check'"
            p = os.system('echo "%s"|sudo -S %s' % (passwd, command)) # Issue: if shell has sudo permissions already, but user starts script without sudo, this will pass with the wrong password, because sudo won't ask for it
            if p == 256:
                print("You didnt enter the correct sudo password.  Chances left: %s"%(max_try-counter-1))
                counter = counter+1
            else:
                print("sudo authentication verified!")
                have_pass = True
                break
        if have_pass == False:
            return False
        else:
            sudo_pass = passwd
            return True



# Installation function
def install(type="", module_name="", module_version=None, cmd=""):
    command = ""

    if type == "pip":
        command = "%s %s" % (install_str, module_name)
        if module_version:
            command = "%s==%s" % (command, module_version)

    else:
        command = cmd
    print("Installing: %s " % command)
    status, output = subprocess.getstatusoutput(command)
    print(output)
    print((78 * '-'))







def basic_installation():


    # node
    try:
        sys.stdout.write("Installing: node\n", True)
        print("Installing: node")
        install(cmd="brew install node")
    except:
        sys.stdout.error("\tAn error occured. See log file\n")
        print("Unable to install node")

    # ideviceinstaller
    try:
        sys.stdout.write("Installing: ideviceinstaller\n", True)
        print("Installing: ideviceinstaller")
        install(cmd="brew install ideviceinstaller")
    except:
        sys.stdout.error("\tAn error occured. See log file\n")
        print("Unable to install ideviceinstaller")

    # libtool
    try:
        sys.stdout.write("Installing: autoconf automake libtool\n", True)
        print("Installing: autoconf automake libtool")
        install(cmd="brew install autoconf automake libtool")
    except:
        sys.stdout.error("\tAn error occured. See log file\n")
        print("Unable to install libtool")

    # pkg-config
    try:
        sys.stdout.write("Installing: pkg-config\n", True)
        print("Installing: pkg-config")
        install(cmd="brew reinstall pkg-config")
    except:
        sys.stdout.error("\tAn error occured. See log file\n")
        print("Unable to reinstall pkg-config")


    # appium
    try:
        sys.stdout.write("Installing: appium\n", True)
        print("Installing: appium")
        install(cmd="npm install -g appium")
    except:
        sys.stdout.error("\tAn error occured. See log file\n")
        print("Unable to install appium")

    # libimobiledevice
    try:
        sys.stdout.write("Installing: libimobiledevice\n", True)
        print("Installing: libimobiledevice")
        install(cmd="brew unlink libimobiledevice")
        install(cmd="brew install libimobiledevice --HEAD")
        install(cmd="brew link libimobiledevice")
    except:
        sys.stdout.error("\tAn error occured. See log file\n")
        print("Unable to install libimobiledevice")

    # carthage
    try:
        sys.stdout.write("Installing: carthage\n", True)
        print("Installing: carthage")
        install(cmd="brew install carthage")
    except:
        print("Unable to install carthage")



def main(rungui = False):
    global sudo_pass
    if rungui: # GUI will only run this if it already has the password, and it's verified
        sudo_pass = rungui # Save password
    else:
        # Make sure we have root privleges
        if check_if_ran_with_sudo():
            print("Running with root privs\n")
        else:
            print("Error - Need root privleges\n")
            quit()

    # Setup logging
    CommonUtils.Logger_Setup(logfile, rungui)

    try:
        xcode_path = subprocess.Popen(['xcrun', 'simctl'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        xcode_path = xcode_path.communicate()
        xcode_path = str(xcode_path[0]).strip()
        if xcode_path.find("Prints the usage for a given subcommand") != -1:
            basic_installation()
            sys.stdout.write("Installation complete please see log files\n", True)
        else:
            sys.stdout.error("\tCouldn't find xcode. You must install xcode manually first and launch it at least one time to make sure installation is completed.\n")
    except:
        sys.stdout.error("\tCouldn't find xcode. You must install xcode manually first and launch it at least one time to make sure installation is completed.\n")

    # Clean up logger, and reinstate STDOUT/ERR
    CommonUtils.Logger_Teardown(logfile)


if __name__ == "__main__":
    main()