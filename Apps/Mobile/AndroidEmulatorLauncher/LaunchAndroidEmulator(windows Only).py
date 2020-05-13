'''
Created on Apr. 14, 2020

@author: hossa
'''
import subprocess,re,time,os,sys
import importlib.util

# Check to see if all items are installed
package_name_list  = ['pick','windows-curses']



for package_name in package_name_list:
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(package_name +" is not installed")
        print ("Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

list_of_avds_raw = (subprocess.Popen("emulator -list-avds",
                           shell=True,
                           stdout=subprocess.PIPE,
                           universal_newlines=True).communicate()[0]) 


list_of_avds = list_of_avds_raw.splitlines()

emulator_location_raw = (subprocess.Popen("where emulator",
                           shell=True,
                           stdout=subprocess.PIPE,
                           universal_newlines=True).communicate()[0]) 


emulator_location_list = emulator_location_raw.splitlines()


full_emulator_path = emulator_location_list[0]

from pick import pick
title = 'Please select an emulator '
option, index = pick(list_of_avds, title)
device = "%s -avd %s"%(full_emulator_path,option)
output = os.system(device)
time.sleep(5)