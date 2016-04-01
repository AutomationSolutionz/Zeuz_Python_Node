# -*- coding: cp1252 -*-
import os
import time
import sys
sys.path.append("..")
top_path=os.path.realpath(os.path.join(os.path.join(os.getcwd(),os.pardir),os.pardir))
sys.path.append(top_path)
if os.name == 'nt':
    from AutomationFW.PCDesktop import WinCommonFoldersPaths
    #from AutomationFW import PCDesktop.WinCommonFoldersPaths as WinCommonFoldersPaths
else:
    from AutomationFW.MacDesktop import MacCommonFoldersPaths as WinCommonFoldersPaths

###########Production / Dev Config variables######################
#Environment = "Test"
Environment = "Production"
if Environment == "Test":
    ###########Dev Config Variables############################
    print "Running on Test Environment..."
    time.sleep(1)
    #go site URL
    go_url = "enter/url"

    #database ip
    database_ip = "127.0.0.1"
    #database_ip = "135.23.123.67"
    database_user= "postgres"
    database_password= "password"        
    database_name= "postgres"        
    database_port= 5432
    adb_port=5037
    #Email List for Daily Build
    dl_list = "test@test.com"
    server_port= 8000
    #Folder Paths
    if os.name == 'nt':
        NetworkFolder = WinCommonFoldersPaths.Get_My_Documents_Path()
        NetworkLogFolder = WinCommonFoldersPaths.Get_My_Documents_Path()
    elif os.name == 'posix':
        NetworkFolder = "/Volumes/AutomationNetworkFolderPath"
        NetworkLogFolder = "/Volumes/AutomationLogNetworkPath"
elif Environment == "Production":
    ###########Prod Config Variables############################
    #print "Running on Production Environment..."
    time.sleep(1)

    #go site URL
    go_url = "enter/url"

    #database ip
    database_ip = "assetscience.automationsolutionz.com"
    database_user= "postgres"            
    database_password= "password"        
    database_name= "postgres"        
    database_port= 5432
    
    adb_port=5037
    server_port= 90

    #Folder Paths
    if os.name == 'nt':
        #Email List for Daily Build
        dl_list = "test@test.com"

        NetworkFolder = WinCommonFoldersPaths.Get_My_Documents_Path()
        NetworkLogFolder = WinCommonFoldersPaths.Get_My_Documents_Path()
    elif os.name == 'posix':
        #Email List for Daily Build
        dl_list = "test@test.com"

        NetworkFolder = "/Volumes/AutomationNetworkFolderPath"
        NetworkLogFolder = "/Volumes/AutomationLogNetworkPath"

###########Global variables######################

#Execution Log Id
sTestStepExecLogId = ''

#Test Step Type
sTestStepType = ''

#Default Test Step Time out value
DefaultTestStepTimeout = 300

#Enable or Disable Threading for Test Steps
ThreadingEnabled = False

#Peformance Variables
transaction_starttime = ''
transaciton_endtime = ''
transaction_duration = ''

transaction_startmemory = 0
transaction_endmemory = 0
transaction_deltamemory = 0
transaction_deltapercentmemory = 0

transaction_peak_cpu = []
transaction_avg_cpu = 0

#This will be set in the driver
TCLogFolder = ""

#BuildFolders for Install
BuildPath = "C:\\Test"

RunIdTempPath=''
test_log_base_path='TestExecutionLog'
log_file_upload_server_ip='99.236.248.206'
log_file_upload_server_port=90
