# -*- coding: cp1252 -*-
import os
import sys
import urllib2
import os.path

top_path=os.path.realpath(os.path.join(os.path.join(os.getcwd(),os.pardir),os.pardir))
sys.path.append(top_path)
#adding driver folder to sys.path
current_file_path=os.path.dirname(os.getcwd())#getting parent folder
driver_folder=os.path.join(current_file_path,'Drivers')
if driver_folder not in sys.path:
    sys.path.append(driver_folder)
import ConfigParser
import time
import threading, Queue
import inspect
import Utilities.DataBaseUtilities as DBUtil
from Utilities import FileUtilities as FL, CommonUtil,DataFetching,ConfigModule
import importlib
import requests
ReRunTag="ReRun"
passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True',True,1,'1','Success','success','SUCCESS']
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE',False,0,'0']

if os.name == 'nt':
    import pythoncom
    location = "X:\\Actions\\Common Tasks\\PythonScripts\\"
    if location not in sys.path:
        sys.path.append(location)
    current_location=os.getcwd()
    current_location=current_location+('\\Drivers\\')
    if current_location not in sys.path:
        sys.path.append(current_location)
def GetAllDriver(server_id):
    query="select distinct driver from test_steps_list"
    Conn=DBUtil.ConnectToDataBase(sHost=server_id)
    driver_name=DBUtil.GetData(Conn,query)
    if 'Manual' in driver_name:
        driver_name.remove('Manual')
    return driver_name
def collectAlldependency(project,team,server_id):
    query="select dependency_name, array_agg(distinct name) from dependency d,dependency_management dm,dependency_name dn where d.id=dm.dependency and d.id=dn.dependency_id and dm.project_id='%s' and dm.team_id=%d group by dependency_name"%(project,int(team))
    conn=DBUtil.ConnectToDataBase(sHost=server_id)
    dependency_list=DBUtil.GetData(conn,query,False)
    conn.close()
    return dependency_list
def update_global_config(section,key,value):
    file_name=os.getcwd()+os.sep+'global_config.ini'
    config=ConfigParser.SafeConfigParser()
    config.read(file_name)
    temp=config.sections()
    list_item=[]
    for each in temp:
        temp_dict=dict(config.items(each))
        if key.lower() in temp_dict.keys():
            #update the key
            temp_dict[key.lower()]=value
        else:
            temp_dict.update({key.lower():value})
        list_item.append((each,temp_dict))
    #print list_item
    for each in list_item:
        section=each[0]
        temp_dict=each[1]
        if not config.has_section(section):
            config.add_section(section)
        for eachitem in temp_dict.keys():
            config.set(section,eachitem,temp_dict[eachitem])

    with(open(file_name,'w')) as open_file:
        config.write(open_file)

def main(server_id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    if os.name == 'nt':
        pythoncom.CoInitialize()

    #*****************Start of Main Driver*****************
        #connect db based on test case number get all test step

        # Here we are starting the main driver operations

    #*****************Start of Main Driver*****************
        #connect db based on test case number get all test step

        # Here we are starting the main driver operations

    #first setup the config.ini file

    temp_ini_file=os.path.join(os.path.join(FL.get_home_folder(),os.path.join('Desktop',os.path.join('AutomationLog',ConfigModule.get_config_value('Temp','_file')))))
    ConfigModule.add_config_value('sectionOne','sTestStepExecLogId', sModuleInfo,temp_ini_file)
    conn=DBUtil.ConnectToDataBase(sHost=server_id)
    Userid = (CommonUtil.MachineInfo().getLocalUser()).lower()
    UserList = DBUtil.GetData(conn, "Select User_Names from permitted_user_list")
    conn.close()
    if Userid not in UserList:
        CommonUtil.ExecLog(sModuleInfo, "User don't have permission to run the tests" , 3)
        return "You Don't Have Permission"

    #Get all the drivers
    Driver_list=GetAllDriver(server_id)
    #Find Test Runs scheduled for this user from test_run_env table
    conn=DBUtil.ConnectToDataBase(sHost=server_id)
    TestRunLists = DBUtil.GetData(conn, "Select run_id,rundescription,tester_id from test_run_env Where tester_id = '%s' and (status = 'Submitted')" % Userid, False)
    conn.close()
    if len(TestRunLists) > 0:
        print "Running Test cases from Test Set : ", TestRunLists[0:len(TestRunLists)]
        CommonUtil.ExecLog(sModuleInfo, "Running Test cases from Test Set : %s" % TestRunLists[0:len(TestRunLists)], 1)

    else:
        print "No Test Run Schedule found for the current user :", Userid
        CommonUtil.ExecLog(sModuleInfo, "No Test Run Schedule found for the current user : %s" % Userid, 2)
        return False

    #Loop thru all the test runs scheduled for this user
    for TestRunID in TestRunLists:
        #get the dependency of all projects
        query="select distinct project_id, team_id from test_run_env tre, machine_project_map mpm where mpm.machine_serial=tre.id and run_id='%s'"%TestRunID[0]
        conn=DBUtil.ConnectToDataBase(sHost=server_id)
        project_team=DBUtil.GetData(conn,query,False)
        conn.close()
        dependency_list=collectAlldependency(project_team[0][0],project_team[0][1],server_id)
        #code for the dependency_list will go here.
        query="select rundescription from test_run_env where run_id='%s'"%TestRunID[0]
        conn=DBUtil.ConnectToDataBase(sHost=server_id)
        rundescription=DBUtil.GetData(conn,query)
        conn.close()
        dependency_list_final={}
        if isinstance(rundescription,list) and len(rundescription)==1:
            rundescription=rundescription[0]
            rundescription=rundescription.split("|")
            for each in rundescription:
                if ":" not in each:
                    continue
                for eachitem in dependency_list:
                    current_dependency=eachitem[0]
                    for eachitemlist in eachitem[1]:
                        if each.split(":")[1].strip()==eachitemlist:
                            current_item=each.split(":")[1].strip()
                            dependency_list_final.update({current_dependency:current_item})

        print dependency_list_final

        query="select distinct name,field,value from machine_run_params mrp, test_run_env tre where tre.id=mrp.machine_serial and run_id='%s'"%(TestRunID[0])
        conn=DBUtil.ConnectToDataBase(sHost=server_id)
        run_params=DBUtil.GetData(conn,query,False)
        conn.close()
        run_para=[]
        for each in run_params:
            m_={}
            m_.update({'field':each[0]})
            m_.update({'name':each[1]})
            m_.update({'value':each[2]})
            run_para.append(m_)
        print run_para
        #TestResultsEnv Table
        #Update test_run_env table with status for the current TestRunId
        conn=DBUtil.ConnectToDataBase(sHost=server_id)
        print DBUtil.UpdateRecordInTable(conn, 'test_run_env', "where run_id = '%s'" % TestRunID[0], status='In-Progress')
        conn.close()
        currentTestSetStatus = 'In-Progress'
        #Insert an entry to the TestResultsEnv table
        sTimeStamp = CommonUtil.TimeStamp('string') #used for run_id
        #sTestResultsRunId = TestRunID[0] + '-' + sTimeStamp
        sTestResultsRunId = TestRunID[0]# + sTimeStamp
        #test set start time
        conn=DBUtil.ConnectToDataBase(sHost=server_id)
        now = DBUtil.GetData(conn, "SELECT CURRENT_TIMESTAMP;", False)
        conn.close()
        sTestSetStartTime = str(now[0][0])
        iTestSetStartTime = now[0][0]
        #cur.execute("insert into test_env_results (run_id,rundescription,tester_id,status,teststarttime) values ('%s','%s','%s','In-Progress','%s')" % (sTestResultsRunId, TestRunID[1], Userid, sTestSetStartTime))
        #conn.commit()
        conn=DBUtil.ConnectToDataBase(sHost=server_id)
        DBUtil.UpdateRecordInTable(conn, 'test_env_results', "Where run_id = '%s' and tester_id = '%s'" % (sTestResultsRunId, Userid), status='In-Progress', teststarttime='%s' % (sTestSetStartTime))
        conn.close()

        # Find the type of dataset we want to run for given testset
        #no data Type is used in our framework thats why it is ommitted.
        #DataTypeList = DBUtil.GetData(conn, "Select data_type From test_run_env Where run_id = '%s'" % TestRunID[0], False)
        #DataType = DataTypeList[0][0]
        DataType=""

        #Find Test Cases in this Test Set & add it to test_run table
        #TestCaseLists = DBUtil.GetData(conn, "Select TC_ID From Test_Sets Where testset_id = '%s' order by id" % TestRunID[1], False) #and data_type
        #for TestCaseID in TestCaseLists:
            #Insert each test case id to the test_run table
         #   DBUtil.InsertNewRecordInToTable(conn, 'test_run', run_id=sTestResultsRunId, tc_id=list(TestCaseID)[0])

        #This step will remain here for now, just to make sure test case is added in the previous one
        #Find all test cases added in the test_run table for the current run id
        conn=DBUtil.ConnectToDataBase(sHost=server_id)
        query="select distinct tc.tc_id,test_case_type,test_order from result_test_cases tc, test_run tr where tr.run_id=tc.run_id and tr.tc_id=tc.tc_id and tc.run_id='%s' order by tr.test_order"%TestRunID[0].strip()
        TestCaseLists = DBUtil.GetData(conn, query,False) #"Select TC_ID From test_run Where run_id = '%s'" % TestRunID[0], False)
        conn.close()
        #HYBRID RUN IMPLEMENTED HERE
        AutomationList=[]
        run_type=""
        for each in TestCaseLists:
            print each
            test_case_id=each[0]
            query="select tc_type from result_test_cases where tc_id='%s' and run_id='%s'"%(test_case_id,TestRunID[0])
            conn=DBUtil.ConnectToDataBase(sHost=server_id)
            forced=DBUtil.GetData(conn,query)
            conn.close()
            if forced[0]=='Forc':
                AutomationList.append((test_case_id,'Manual'))
            else:
                AutomationList.append((each[0],each[1]))
        print AutomationList
        if len(filter(lambda x: x[1]=='Manual',AutomationList))>0:
            if (len(filter(lambda x:x[1]=='Automated',AutomationList)))>0 or (len(filter(lambda x:x[1]=='Performance',AutomationList)))>0:
                run_type='Hybrid'
            else:
                run_type='Manual'
        else:
            if (len(filter(lambda x:x[1]=='Performance',AutomationList)))== 0 and (len(filter(lambda x:x[1]=='Automated',AutomationList)))>0:
                run_type='Automation'
            elif (len(filter(lambda x:x[1]=='Performance',AutomationList)))>0 and (len(filter(lambda x:x[1]=='Automated',AutomationList)))==0:
                run_type='Performance'
            else:
                run_type='Hybrid'
        Dict={}
        Dict.update({'run_type':run_type})
        sWhereQuery="where run_id='%s'" %TestRunID[0]
        conn=DBUtil.ConnectToDataBase(sHost=server_id)
        print DBUtil.UpdateRecordInTable(conn,"test_run_env",sWhereQuery,**Dict)
        conn.close()
        TestCaseLists=[]
        automation_count=len(filter(lambda  x:x[1]=='Automated',AutomationList))
        performance_count=len(filter(lambda  x:x[1]=='Performance',AutomationList))
        TestCaseLists=filter(lambda  x:x[1]=='Automated' or x[1]=='Performance',AutomationList)
        print TestCaseLists
        if len(TestCaseLists) > 0:
            print "Running Test cases from list : ", TestCaseLists[0:len(TestCaseLists)]
            CommonUtil.ExecLog(sModuleInfo, "Running Test cases from list : %s" % TestCaseLists[0:len(TestCaseLists)], 1)
            print "Total number of test cases ", len(TestCaseLists)
        else:
            print "No test cases found for the current user :", Userid
            CommonUtil.ExecLog(sModuleInfo, "No test cases found for the current user : %s" % Userid, 2)
            return False
        #TestCaseLists = list(TestCaseLists[0])
        for TestCaseID in TestCaseLists:
            print TestCaseID
            #first check that it is all copied otherwise check it periodically.
            test_case_copy_status=False
            while(test_case_copy_status!=True):
                query="select copy_status from test_run where tc_id='%s' and run_id='%s'"%(TestCaseID[0],TestRunID[0])
                Conn=DBUtil.ConnectToDataBase(sHost=server_id)
                test_case_copy_status=DBUtil.GetData(Conn,query)[0]
                Conn.close()
            ConfigModule.add_config_value('sectionOne','sTestStepExecLogId',"MainDriver",temp_ini_file)
            StepSeq = 1
            TCID = list(TestCaseID)[0]
            test_case_type=TestCaseID[1]
            print test_case_type
            print "-------------*************--------------"
            """if Rerun==False:
                TestCaseName = DBUtil.GetData(conn, "Select tc_name From test_cases Where tc_id = '%s'" % TCID, False)
            else:
                TestCaseName = DBUtil.GetData(conn, "Select tc_name From result_test_cases Where tc_id = '%s' and run_id='%s'" % (TCID,referred_run_id), False)
            """
            conn=DBUtil.ConnectToDataBase(sHost=server_id)
            TestCaseName = DBUtil.GetData(conn, "Select tc_name From result_test_cases Where tc_id = '%s' and run_id='%s'" % (TCID,TestRunID[0]), False)
            conn.close()
            #Create Log Folder for the TC
            #get the config_global.ini
            try:
                log_file_path=ConfigModule.get_config_value('sectionOne', 'temp_run_file_path',temp_ini_file)
            except Exception, e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                print Error_Detail
            test_case_folder=log_file_path+os.sep+(TestRunID[0].replace(':','-')+os.sep+TCID.replace(":",'-'))
            ConfigModule.add_config_value('sectionOne', 'test_case',TCID,temp_ini_file)
            ConfigModule.add_config_value('sectionOne','test_case_folder',test_case_folder,temp_ini_file)
            log_folder=test_case_folder+os.sep+'Log'
            ConfigModule.add_config_value('sectionOne', 'log_folder',log_folder,temp_ini_file)
            screenshot_folder=test_case_folder+os.sep+'screenshots'
            ConfigModule.add_config_value('sectionOne', 'screen_capture_folder',screenshot_folder,temp_ini_file)

            home = os.path.join(FL.get_home_folder(),os.path.join('Desktop','Attachments'))
            ConfigModule.add_config_value('sectionOne', 'download_folder',home,temp_ini_file)

            #create_test_case_folder
            test_case_folder=ConfigModule.get_config_value('sectionOne','test_case_folder',temp_ini_file)
            FL.CreateFolder(test_case_folder)

            #FL.CreateFolder(Global.TCLogFolder + os.sep + "ProductLog")
            log_folder=ConfigModule.get_config_value('sectionOne','log_folder',temp_ini_file)
            FL.CreateFolder(log_folder)

            #FL.CreateFolder(Global.TCLogFolder + os.sep + "Screenshots")
            #creating ScreenShot File
            screen_capture_folder=ConfigModule.get_config_value('sectionOne','screen_capture_folder',temp_ini_file)
            FL.CreateFolder(screen_capture_folder)


            #download all the attachments
            download_folder=ConfigModule.get_config_value('sectionOne','download_folder',temp_ini_file)
            query="select distinct file_path,file_name,file_type from tc_attachement where tc_id='%s'"%TCID
            conn=DBUtil.ConnectToDataBase(sHost=server_id)
            a_list=DBUtil.GetData(conn,query,False)
            conn.close()

            query="select distinct file_path,file_name,file_type,sa.step_id from step_attachment sa, result_test_steps rts where rts.step_id=sa.step_id and rts.run_id='%s' and rts.tc_id='%s'"%(TestRunID[0],TCID)
            conn=DBUtil.ConnectToDataBase(sHost=server_id)
            ta_list=DBUtil.GetData(conn,query,False)
            conn.close()
            print ta_list
            file_specific_steps={}

            #now download the attached file
            FL.DeleteFolder(ConfigModule.get_config_value('sectionOne','download_folder',temp_ini_file))
            FL.CreateFolder(download_folder)
            for each in a_list:
                m=each[1]+'.'+each[2] #file name
                f=open(download_folder+'/'+m,'wb')
                f.write(urllib2.urlopen('http://'+ConfigModule.get_config_value('Server','server_address')+':'+str(ConfigModule.get_config_value('Server','server_port'))+'/static'+each[0]).read())
                file_specific_steps.update({m:download_folder+'/'+m})
                f.close()

            for each in ta_list:
                m=each[1]+'.'+each[2] #file name
                if not os.path.exists(download_folder+'/'+str(each[3])):
                    FL.CreateFolder(download_folder+'/'+str(each[3]))
                f=open(download_folder+'/'+str(each[3])+'/'+m,'wb')
                f.write(urllib2.urlopen('http://'+ConfigModule.get_config_value('Server','server_address')+':'+str(ConfigModule.get_config_value('Server','server_port'))+'/static'+each[0]).read())
                file_specific_steps.update({m:download_folder+'/'+str(each[3])+'/'+m})
                f.close()

            print "Running Test case id : %s :: %s" % (TCID, TestCaseName[0])
            CommonUtil.ExecLog(sModuleInfo, "-------------*************--------------", 1)
            CommonUtil.ExecLog(sModuleInfo, "Running Test case id : %s :: %s" % (TCID, TestCaseName), 1)


            #test Case start time
            conn=DBUtil.ConnectToDataBase(sHost=server_id)
            now = DBUtil.GetData(conn, "SELECT CURRENT_TIMESTAMP;", False)
            conn.close()

            sTestCaseStartTime = str(now[0][0])
            iTestCaseStartTime = now[0][0]

            #cur.execute("insert into test_case_results (run_id,tc_id,status,teststarttime ) values ('%s','%s','In-Progress','%s')" % (sTestResultsRunId, TCID, sTestCaseStartTime))
            #conn.commit()
            condition="where run_id='"+sTestResultsRunId+"' and tc_id='"+TCID+"'"
            conn=DBUtil.ConnectToDataBase(sHost=server_id)
            print DBUtil.UpdateRecordInTable(conn,"test_case_results", condition,status='In-Progress',teststarttime=sTestCaseStartTime)
            conn.close()
            #Get Test Case Index to be inserted to test_step_results table
            conn=DBUtil.ConnectToDataBase(sHost=server_id)
            TestCaseResultIndex = DBUtil.GetData(conn, "Select id From test_case_results where run_id = '%s' and TC_ID = '%s' Order By id desc limit 1" % (sTestResultsRunId, TCID), False)
            conn.close()
            #get the test case steps for this test case
            #TestStepsList = DBUtil.GetData(conn,"Select teststepname From TestSteps where TC_ID = '%s' Order By teststepsequence" %TCID,False)
            """if Rerun==False:
                TestStepsList = DBUtil.GetData(conn, "Select ts.step_id,stepname,teststepsequence,tsl.driver,ts.test_step_type From Test_Steps ts,test_steps_list tsl where TC_ID = '%s' and ts.step_id = tsl.step_id and tsl.stepenable='true' Order By teststepsequence" % TCID, False)
            else:
                TestStepsList = DBUtil.GetData(conn, "Select ts.step_id,stepname,teststepsequence,tsl.driver,ts.test_step_type From result_test_steps ts,result_test_steps_list tsl where ts.run_id=tsl.run_id and TC_ID = '%s' and ts.step_id = tsl.step_id and tsl.stepenable='true' and ts.run_id='%s' Order By teststepsequence" % (TCID,referred_run_id), False)
            """
            conn=DBUtil.ConnectToDataBase(sHost=server_id)
            TestStepsList = DBUtil.GetData(conn, "Select ts.step_id,stepname,teststepsequence,tsl.driver,tsl.steptype,tsl.data_required,tsl.step_editable From result_test_steps ts,result_test_steps_list tsl where ts.run_id=tsl.run_id and TC_ID = '%s' and ts.step_id = tsl.step_id and tsl.stepenable='true' and ts.run_id='%s' Order By teststepsequence" % (TCID,TestRunID[0]), False)
            conn.close()
            Stepscount = len(TestStepsList)
            sTestStepResultList = []
            #get the client name for this test case
            #sClientName = TestRunID[4]
            #sClientName=(TestRunID[4].split("("))[0].strip()
            #print sClientName
            """if Rerun==False:
                #DataSetList = DBUtil.GetData(conn, "Select tcdatasetid from test_case_datasets where tc_id='%s' and data_type='%s'" % (TCID, DataType), False) # Later we can add dataset tag like multilang here.
                DataSetList = DBUtil.GetData(conn, "Select tcdatasetid from test_case_datasets where tc_id='%s'" % (TCID), False)
            else:
                DataSetList = DBUtil.GetData(conn, "Select tcdatasetid from result_test_case_datasets where tc_id='%s' and run_id='%s'" % (TCID,referred_run_id), False)
            """
            conn=DBUtil.ConnectToDataBase(sHost=server_id)
            DataSetList = DBUtil.GetData(conn, "Select tcdatasetid from result_test_case_datasets where tc_id='%s' and run_id='%s'" % (TCID,TestRunID[0]), False)
            conn.close()
            if len(DataSetList) == 0:
                #This condition is for test cases which dont have any input data
                DataSetList.append('NoDataSetFound')
            for EachDataSet in DataSetList:
                #Check if this is a performance test case
                """if DataType == 'Performance':
                    #this is a performance test case
                    PerfQ = Queue.Queue()
                    PerfThread = threading.Thread(target=Performance.CollectProcessMemory, args=(TestStepsList[StepSeq - 1][1], PerfQ))
                    PerfThread.start()
                    PerfQ.put('Start')
                """
                while StepSeq <= Stepscount:
                    # Beginning of a Test Step
                    print "Step: ", TestStepsList[StepSeq - 1][1]
                    CommonUtil.ExecLog(sModuleInfo, "Step : %s" % TestStepsList[StepSeq - 1][1], 1)
                    testcasecontinue=False
                    Conn=DBUtil.ConnectToDataBase(sHost=server_id)
                    query="select description from master_data where field='continue' and value='point' and id ='%s'"%(TCID+'_s'+str(StepSeq))
                    test_case_continue=DBUtil.GetData(Conn,query,False)
                    Conn.close()
                    if test_case_continue[0][0]=='yes':
                        testcasecontinue=True
                    else:
                        testcasecontinue=False
                    #if DataType == 'Performance':
                    #    PerfQ.put(TestStepsList[StepSeq - 1][1])
                    #Check if the current test step is a Performance Test Step
                    #if TestStepsList[StepSeq - 1][4] == 'Performance':
                    #    Global.sTestStepType = TestStepsList[StepSeq - 1][4]
                    #open a file handler and write it to it
                    ConfigModule.add_config_value('sectionOne', 'sTestStepExecLogId', sTestResultsRunId+"|" + TCID +"|"+str(TestStepsList[StepSeq - 1][0]) +"|"+str(StepSeq),temp_ini_file)
                    # Test Step start time
                    conn=DBUtil.ConnectToDataBase(sHost=server_id)
                    now = DBUtil.GetData(conn, "SELECT CURRENT_TIMESTAMP;", False)
                    conn.close()
                    sTestStepStartTime = str(now[0][0])
                    #TestStepStartTime = now[0][0]
                    TestStepStartTime = time.time()
                    # Memory calculation at the beginning of test step
                    WinMemBegin = CommonUtil.PhysicalAvailableMemory()#MemoryManager.winmem()
                    #update test_step_results table
                    #cur.execute("insert into test_step_results (run_id,tc_id,teststep_id,teststepsequence,status,stepstarttime,logid,start_memory,testcaseresulttindex ) values ('%s','%s','%d','%d','In-Progress','%s','%s', '%s', '%d')" % (sTestResultsRunId, TCID, TestStepsList[StepSeq - 1][0], TestStepsList[StepSeq - 1][2], sTestStepStartTime, Global.sTestStepExecLogId, WinMemBegin, TestCaseResultIndex[0][0]))
                    #conn.commit()
                    condition="where run_id='"+sTestResultsRunId+"' and tc_id='"+TCID+"' and teststep_id='"+str(TestStepsList[StepSeq - 1][0])+"' and teststepsequence='"+str(TestStepsList[StepSeq - 1][2])+"'"
                    Dict={'teststepsequence':TestStepsList[StepSeq - 1][2],'status':'In-Progress','stepstarttime':sTestStepStartTime,'logid':ConfigModule.get_config_value('sectionOne','sTestStepExecLogId',temp_ini_file),'start_memory':WinMemBegin,'testcaseresulttindex':TestCaseResultIndex[0][0]}
                    conn=DBUtil.ConnectToDataBase(sHost=server_id)
                    DBUtil.UpdateRecordInTable(conn,"test_step_results",condition,**Dict)
                    conn.close()
                    steps_data=[]
                    #get the steps data from here
                    """if TestStepsList[StepSeq-1][5] and TestStepsList[StepSeq-1][6]:
                        #for the edit data steps
                        container_id_data_query="select ctd.curname,ctd.newname from test_steps_data tsd, container_type_data ctd where tsd.testdatasetid = ctd.dataid and tcdatasetid = 'CLI-0382ds' and teststepseq = 13060 and ctd.curname Ilike '%_s2%'"
                    elif TestStepsList[StepSeq-1][5] and not TestStepsList[StepSeq-1][6]:
                        container_id_data_query="select ctd.curname,ctd.newname from test_steps_data tsd, container_type_data ctd where tsd.testdatasetid = ctd.dataid and tcdatasetid = '%s' and teststepseq = %d and ctd.curname Ilike '%%_s%s%%'"%(EachDataSet[0],int(TestStepsList[StepSeq-1][2]),StepSeq)
                        conn=DBUtil.ConnectToDataBase()
                        container_data_details=DBUtil.GetData(conn,container_id_data_query,False)
                        conn.close()
                        steps_data=[]
                        for each_data_id in container_data_details:
                            From_Data = DataFetching.Get_PIM_Data_By_Id(each_data_id[0])
                            steps_data.append(From_Data)
                    else:
                        steps_data=[]"""
                    container_id_data_query="select ctd.curname,ctd.newname from test_steps_data tsd, container_type_data ctd where tsd.testdatasetid = ctd.dataid and tcdatasetid = '%s' and teststepseq = %d and ctd.curname Ilike '%%_s%s%%'"%(EachDataSet[0],int(TestStepsList[StepSeq-1][2]),StepSeq)
                    conn=DBUtil.ConnectToDataBase(sHost=server_id)
                    container_data_details=DBUtil.GetData(conn,container_id_data_query,False)
                    conn.close()
                    steps_data=[]
                    for each_data_id in container_data_details:
                        From_Data = DataFetching.Get_Data_Like_Server(server_id,TestRunID[0].strip(),each_data_id[0])
                        steps_data.append(From_Data)
                    print "steps data for #%d: "%StepSeq,steps_data
                    CommonUtil.ExecLog(sModuleInfo,"steps data for #%d: %s"%(StepSeq,str(steps_data)),1)
                    #get the estimateed time for the steps
                    step_time_query="select description from result_master_data where field='estimated' and value='time' and run_id='%s' and id='%s'"%(TestRunID[0].strip(),(TCID+'_s'+str(StepSeq)).strip())
                    conn=DBUtil.ConnectToDataBase(sHost=server_id)
                    step_time=DBUtil.GetData(conn,step_time_query)
                    conn.close()
                    step_time=step_time[0]
                    auto_generated_image_name=('_').join(TestStepsList[StepSeq-1][1].split(" "))+'_started.png'
                    CommonUtil.TakeScreenShot(auto_generated_image_name)
                    try:
                        q = Queue.Queue()
                        if TestStepsList[StepSeq-1][3] in Driver_list:
                            module_name=importlib.import_module(TestStepsList[StepSeq-1][3])
                            step_name=TestStepsList[StepSeq-1][1]
                            step_name=step_name.lower().replace(' ','_')
                            if test_case_type=='Performance':
                                config_file_path=os.path.realpath(os.path.join((os.path.join(module_name.__file__,os.pardir)),os.pardir))
                                conf=config_file_path+os.sep+'ConfigFiles'+os.sep+TestStepsList[StepSeq-1][3]+'.conf'
                                functionTocall = getattr(module_name, step_name)
                                simple_queue=Queue.Queue()
                                sStepResult = functionTocall([config_file_path, TestRunID[0], '--config',conf, TestStepsList[StepSeq-1][3], TestStepsList[StepSeq-1][3]+'.'+step_name], steps_data, simple_queue)
                                if sStepResult==0:
                                    sStepResult='Passed'
                                else:
                                    sStepResult='Failed'
                                #perf_result = ConfigFileGenerator.decode_result_performance(conf)
                                perf_result=True
                                if not isinstance(perf_result,bool):
                                    for each in perf_result.keys():
                                        t=perf_result[each]
                                        Dict={'tc_id':TCID,'run_id':TestRunID[0]}
                                        for t_t in range(0,len(t)):
                                            temp=t[t_t]
                                            for echit in temp.keys():
                                                Dict.update({echit:temp[echit]})
                                        print Dict
                                        Conn=DBUtil.ConnectToDataBase(sHost=server_id)
                                        print DBUtil.InsertNewRecordInToTable(Conn,"performance_results",**Dict)
                                        Conn.close()
                                else:
                                    print "error in file path"

                            else:
                                dep_plus_run_params={}
                                dep_plus_run_params.update({'dependency':dependency_list_final})
                                dep_plus_run_params.update({'run_time_params':run_para})
                                functionTocall = getattr(module_name, step_name)
                                simple_queue=Queue.Queue()
                                if ConfigModule.get_config_value('RunDefinition','Threading') in passed_tag_list:
                                    stepThread = threading.Thread(target=functionTocall, args=(dep_plus_run_params,steps_data,file_specific_steps,simple_queue))
                                else:
                                    #from Drivers import Futureshop
                                    sStepResult = functionTocall(dep_plus_run_params,steps_data,file_specific_steps,simple_queue)
                                    if sStepResult in passed_tag_list:
                                        sStepResult='PASSED'
                                    if sStepResult in failed_tag_list:
                                        sStepResult='FAILED'
                                    q.put(sStepResult)
                                    #sStepResult = module_name.ExecuteTestSteps(TestRunID[0],TestStepsList[StepSeq - 1][1],q,dependency_list,steps_data)
                                    #sStepResult = Futureshop.ExecuteTestSteps(TestStepsList[StepSeq - 1][1],q,dependency_list,steps_data)

                        else:
                            #If threading is enabled
                            if ConfigModule.get_config_value('RunDefinition','Threading') in passed_tag_list:
                                stepThread = threading.Thread(target=ExecuteTestSteps, args=(TestStepsList[StepSeq - 1][1], TCID, sClientName, TestStepsList[StepSeq - 1][2], EachDataSet[0], q))
                            else:
                                sStepResult = ExecuteTestSteps(TestStepsList[StepSeq - 1][1], TCID, sClientName, TestStepsList[StepSeq - 1][2], EachDataSet[0], q)

                        #If threading is enabled
                        if ConfigModule.get_config_value('RunDefinition','Threading') in passed_tag_list:
                            #Start the thread
                            print "Starting Test Step Thread.."
                            stepThread.start()
                            #Wait for the Thread to finish or until timeout
                            print "Waiting for Test Step Thread to finish..for (seconds) :", step_time #Global.DefaultTestStepTimeout
                            stepThread.join(float(step_time)) #Global.DefaultTestStepTimeout
                            try:
                                sStepResult=simple_queue.get_nowait()
                                #Get the return value from the ExecuteTestStep fn via Queue
                                q.put(sStepResult)
                                print "Test Step Thread Ended.."
                            except Queue.Empty:
                                print "Test Step did not return after default timeout (secs) : ", step_time#Global.DefaultTestStepTimeout
                                sStepResult = "Failed"
                                q.put(sStepResult)
                                #Clean up
                                if stepThread.isAlive():
                                    print "thread still alive"
                                    #stepThread.__stop()
                                    try:
                                        stepThread._Thread__stop()
                                        while stepThread.isAlive():
                                            time.sleep(1)
                                            print "Thread is still alive"
                                    except:
                                        print "Thread could not be terminated"

                    except Exception, e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                        print Error_Detail
                        CommonUtil.ExecLog(sModuleInfo, "Exception occurred in test step : %s" % Error_Detail, 3)
                        sStepResult = "Failed"

                    #Check if the db connection is alive or timed out
                    #if DBUtil.IsDBConnectionGood(conn) == False:
                    #    print "DB connection is bad"
                    #    CommonUtil.ExecLog(sModuleInfo, "DB connection error", 3)
                    auto_generated_image_name=('_').join(TestStepsList[StepSeq-1][1].split(" "))+'_'+sStepResult.lower()+'.png'
                    CommonUtil.TakeScreenShot(auto_generated_image_name)
                    try:
                        conn.close()
                    except Exception, e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                        print Error_Detail
                        CommonUtil.ExecLog(sModuleInfo, "Exception closing DB connection:%s" % Error_Detail, 2)
                    #test Step End time
                    conn=DBUtil.ConnectToDataBase(sHost=server_id)
                    now = DBUtil.GetData(conn, "SELECT CURRENT_TIMESTAMP;", False)
                    conn.close()
                    sTestStepEndTime = str(now[0][0])
                    #TestStepEndTime = now[0][0]
                    TestStepEndTime = time.time()

                    # Time it took to run the test step
                    TimeDiff = TestStepEndTime - TestStepStartTime
                    #TimeInSec = TimeDiff.seconds
                    TimeInSec = int(TimeDiff)
                    TestStepDuration = CommonUtil.FormatSeconds(TimeInSec)

                    # Memory at the end of Test Step
                    WinMemEnd = CommonUtil.PhysicalAvailableMemory() #MemoryManager.winmem()

                    # Total memory consumed during the test step
                    TestStepMemConsumed = WinMemBegin - WinMemEnd



                    #add result of each step to a list; for a test case to pass all steps should be pass; atleast one Failed makes it 'Fail' else 'Warning' or 'Blocked'
                    if sStepResult:
                        sTestStepResultList.append(sStepResult.upper())
                    else:
                        sTestStepResultList.append("FAILED")
                        print "sStepResult : ", sStepResult
                        CommonUtil.ExecLog(sModuleInfo, "sStepResult : %s" % sStepResult, 1)
                        sStepResult = "Failed"

                    #Take ScreenShot
                    #CommonUtil.TakeScreenShot(sStepResult + "_" + TestStepsList[StepSeq - 1][1])

                    #Update Results
                    if sStepResult.upper() == "PASSED":
                        #Step Passed
                        print TestStepsList[StepSeq - 1][1] + ": Test Step Passed"
                        CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Passed" % TestStepsList[StepSeq - 1][1], 1)
                        #Update Test Step Results table
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        DBUtil.UpdateRecordInTable(conn, 'test_step_results', "Where run_id = '%s' and tc_id = '%s' and teststep_id = '%s' and teststepsequence = '%d' and testcaseresulttindex = '%d'" % (sTestResultsRunId, TCID, TestStepsList[StepSeq - 1][0], TestStepsList[StepSeq - 1][2], TestCaseResultIndex[0][0]),
                                                   status='Passed',
                                                   stependtime='%s' % (sTestStepEndTime),
                                                   end_memory='%s' % (WinMemEnd),
                                                   duration='%s' % (TestStepDuration),
                                                   memory_consumed='%s' % (TestStepMemConsumed)
                                                   )
                        conn.close()
                    elif sStepResult.upper() == "WARNING":
                        #Step has Warning, but continue running next test step for this test case
                        print TestStepsList[StepSeq - 1][1] + ": Test Step Warning"
                        CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Warning" % TestStepsList[StepSeq - 1][1], 2)
                        #Update Test Step Results table
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        DBUtil.UpdateRecordInTable(conn, 'test_step_results', "Where run_id = '%s' and tc_id = '%s' and teststep_id = '%s' and teststepsequence = '%d' and testcaseresulttindex = '%d'" % (sTestResultsRunId, TCID, TestStepsList[StepSeq - 1][0], TestStepsList[StepSeq - 1][2], TestCaseResultIndex[0][0]),
                                                   status='Warning',
                                                   stependtime='%s' % (sTestStepEndTime),
                                                   end_memory='%s' % (WinMemEnd),
                                                   duration='%s' % (TestStepDuration),
                                                   memory_consumed='%s' % (TestStepMemConsumed)
                                                   )
                        conn.close()
                        if not testcasecontinue:
                            break
                    elif sStepResult.upper() == "NOT RUN":
                        #Step has Warning, but continue running next test step for this test case
                        print TestStepsList[StepSeq - 1][1] + ": Test Step Not Run"
                        CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Not Run" % TestStepsList[StepSeq - 1][1], 2)
                        #Update Test Step Results table
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        DBUtil.UpdateRecordInTable(conn, 'test_step_results', "Where run_id = '%s' and tc_id = '%s' and teststep_id = '%s' and teststepsequence = '%d' and testcaseresulttindex = '%d'" % (sTestResultsRunId, TCID, TestStepsList[StepSeq - 1][0], TestStepsList[StepSeq - 1][2], TestCaseResultIndex[0][0]),
                                                   status='Not Run',
                                                   stependtime='%s' % (sTestStepEndTime),
                                                   end_memory='%s' % (WinMemEnd),
                                                   duration='%s' % (TestStepDuration),
                                                   memory_consumed='%s' % (TestStepMemConsumed)
                                                   )
                        conn.close()
                    elif sStepResult.upper() == "FAILED":
                        #Step has a Critial failure, fail the test step and test case. go to next test case
                        print TestStepsList[StepSeq - 1][1] + ": Test Step Failed Failure"
                        CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Failed Failure" % TestStepsList[StepSeq - 1][1], 3)
                        #Update Test Step Results table
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        DBUtil.UpdateRecordInTable(conn, 'test_step_results', "Where run_id = '%s' and tc_id = '%s' and teststep_id = '%s' and teststepsequence = '%d' and testcaseresulttindex = '%d'" % (sTestResultsRunId, TCID, TestStepsList[StepSeq - 1][0], TestStepsList[StepSeq - 1][2], TestCaseResultIndex[0][0]),
                                                   status='Failed',
                                                   stependtime='%s' % (sTestStepEndTime),
                                                   end_memory='%s' % (WinMemEnd),
                                                   duration='%s' % (TestStepDuration),
                                                   memory_consumed='%s' % (TestStepMemConsumed)
                                                   )
                        conn.close()
                        #Discontinue this test case
                        #break
                        #for continuing the test cases if failed
                        if not testcasecontinue:
                            break
                    elif sStepResult.upper() == "BLOCKED":
                        #Step is Blocked, Block the test step and test case. go to next test case
                        print TestStepsList[StepSeq - 1][1] + ": Test Step Blocked"
                        CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Blocked" % TestStepsList[StepSeq - 1][1], 3)
                        #Update Test Step Results table
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        DBUtil.UpdateRecordInTable(conn, 'test_step_results', "Where run_id = '%s' and tc_id = '%s' and teststep_id = '%s' and teststepsequence = '%d' and testcaseresulttindex = '%d'" % (sTestResultsRunId, TCID, TestStepsList[StepSeq - 1][0], TestStepsList[StepSeq - 1][2], TestCaseResultIndex[0][0]),
                                                   status='Blocked',
                                                   stependtime='%s' % (sTestStepEndTime),
                                                   end_memory='%s' % (WinMemEnd),
                                                   duration='%s' % (TestStepDuration),
                                                   memory_consumed='%s' % (TestStepMemConsumed)
                                                   )
                        conn.close()
                        #Discontinue this test case
                        #break
                        #for continuing the test cases if failed
                    elif sStepResult.upper() == "CANCELLED":
                        print TestStepsList[StepSeq - 1][1] + ": Test Step Cancelled"
                        CommonUtil.ExecLog(sModuleInfo, "%s : Test Step Cancelled" % TestStepsList[StepSeq - 1][1], 3)
                        #deleting all the run status and loggging
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        print DBUtil.DeleteRecord(conn,"result_master_data",run_id=TestRunID[0])
                        conn.close()
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        print DBUtil.DeleteRecord(conn,"result_test_steps_data",run_id=TestRunID[0])
                        conn.close()
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        print DBUtil.DeleteRecord(conn,"result_container_type_data",run_id=TestRunID[0])
                        conn.close()
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        print DBUtil.DeleteRecord(conn,"result_test_case_datasets",run_id=TestRunID[0])
                        conn.close()
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        print DBUtil.DeleteRecord(conn,"result_test_case_tag",run_id=TestRunID[0])
                        conn.close()
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        print DBUtil.DeleteRecord(conn,"result_test_steps",run_id=TestRunID[0])
                        conn.close()
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        print DBUtil.DeleteRecord(conn,"result_test_steps_list",run_id=TestRunID[0])
                        conn.close()
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        print DBUtil.DeleteRecord(conn,"test_step_results",run_id=TestRunID[0])
                        conn.close()
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        print DBUtil.DeleteRecord(conn,"test_case_results",run_id=TestRunID[0])
                        conn.close()
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        print DBUtil.DeleteRecord(conn,"test_env_results",run_id=TestRunID[0])
                        conn.close()
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        print DBUtil.DeleteRecord(conn,"test_run",run_id=TestRunID[0])
                        conn.close()
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        print DBUtil.DeleteRecord(conn,"test_run_env",run_id=TestRunID[0])
                        conn.close()
                        conn=DBUtil.ConnectToDataBase(sHost=server_id)
                        print DBUtil.DeleteRecord(conn,"result_test_cases",run_id=TestRunID[0])
                        conn.close()
                        return "pass"

                    #End Test Step
                    #increment step counter
                    StepSeq = StepSeq + 1

                    #Check if Test Set status is 'Cancelled' When it is stopped from Website
                    conn=DBUtil.ConnectToDataBase(sHost=server_id)
                    currentTestSetStatus = DBUtil.GetData(conn, "Select status"
                              " From test_run_env"
                              " Where run_id = '%s'" % sTestResultsRunId, False)
                    conn.close()
                    currentTestSetStatus = currentTestSetStatus[0][0]
                    if currentTestSetStatus == 'Cancelled':
                        print "Test Run status is Cancelled. Exiting the current Test Case... ", TCID
                        CommonUtil.ExecLog(sModuleInfo, "Test Run status is Cancelled. Exiting the current Test Case...%s" % TCID, 2)
                        break
                if DataType == 'Performance':
                    PerfQ.put('Stop')
            #else:
            #    print "Unknown client name : ", sClientName

            #End of test case
            #test Case End time
            conn=DBUtil.ConnectToDataBase(sHost=server_id)
            now = DBUtil.GetData(conn, "SELECT CURRENT_TIMESTAMP;", False)
            conn.close()
            sTestCaseEndTime = str(now[0][0])
            iTestCaseEndTime = now[0][0]

            #Decide if Test Case Pass/Failed
            if 'BLOCKED' in sTestStepResultList:
                print "Test Case Blocked"
                CommonUtil.ExecLog(sModuleInfo, "Test Case Blocked", 3)
                sTestCaseStatus = "Blocked"
            elif 'FAILED' in sTestStepResultList:
                print "Test Case Failed"
                step_index=1
                for each in sTestStepResultList:
                    if each=='FAILED':
                        break
                    else:
                        step_index+=1
                datasetid=TestCaseID[0]+'_s'+str(step_index)
                query="select description from master_data where field='verification' and value='point' and id='%s'"%datasetid
                #Conn=GetConnection()
                conn=DBUtil.ConnectToDataBase(sHost=server_id)
                status=DBUtil.GetData(conn,query,False)
                conn.close()
                if status[0][0]=="yes":
                    sTestCaseStatus='Failed'
                else:
                    sTestCaseStatus='Blocked'
                CommonUtil.ExecLog(sModuleInfo, "Test Case "+sTestCaseStatus, 3)
            elif 'WARNING' in sTestStepResultList:
                print "Test Case Contain Warning(s)"
                CommonUtil.ExecLog(sModuleInfo, "Test Case Contain Warning(s)", 2)
                sTestCaseStatus = "Failed"
            elif 'NOT RUN' in sTestStepResultList:
                print "Test Case Contain Not Run Steps"
                CommonUtil.ExecLog(sModuleInfo, "Test Case Contain Warning(s)", 2)
                sTestCaseStatus = "Failed"
            elif 'PASSED' in sTestStepResultList:
                print "Test Case Passed"
                CommonUtil.ExecLog(sModuleInfo, "Test Case Passed", 1)
                sTestCaseStatus = "Passed"
            else:
                print "Test Case Status Unknown"
                CommonUtil.ExecLog(sModuleInfo, "Test Case Status Unknown", 2)
                sTestCaseStatus = "Unknown"

            # Time it took to run the test case
            TimeDiff = iTestCaseEndTime - iTestCaseStartTime
            TimeInSec = TimeDiff.seconds
            TestCaseDuration = CommonUtil.FormatSeconds(TimeInSec)

            #Collect Log if Test case Failed
            #if sTestCaseStatus != "Passed":
            #Get DTS Logs
            #print CommonUtil.GetProductLog()

            #Zip the folder
            #removing duplicates line from here.
            current_log_file=os.path.join(ConfigModule.get_config_value('sectionOne','log_folder',temp_ini_file),'temp.log')
            temp_log_file=os.path.join(ConfigModule.get_config_value('sectionOne','log_folder',temp_ini_file),TCID+'.log')
            lines_seen=set()
            outfile=open(temp_log_file,'w')
            for line in open(current_log_file,'r'):
                if line not in lines_seen:
                    outfile.write(line)
                    lines_seen.add(line)
            outfile.close()
            FL.DeleteFile(current_log_file)
            #FL.RenameFile(ConfigModule.get_config_value('sectionOne','log_folder'), 'temp.log',TCID+'.log')
            TCLogFile = FL.ZipFolder(ConfigModule.get_config_value('sectionOne','test_case_folder',temp_ini_file),ConfigModule.get_config_value('sectionOne','test_case_folder',temp_ini_file) + ".zip")
            #Delete the folder
            FL.DeleteFolder(ConfigModule.get_config_value('sectionOne','test_case_folder',temp_ini_file))

            #upload will go here.
            upload_zip(ConfigModule.get_config_value('Server','server_address'),ConfigModule.get_config_value('Server','server_port'),ConfigModule.get_config_value('sectionOne','temp_run_file_path',temp_ini_file),TestRunID[0],ConfigModule.get_config_value('sectionOne','test_case',temp_ini_file)+".zip",ConfigModule.get_config_value('Temp','_file_upload_path'))
            TCLogFile=os.sep+ConfigModule.get_config_value('Temp','_file_upload_path')+os.sep+TestRunID[0].replace(":",'-')+'/'+ConfigModule.get_config_value('sectionOne','test_case',temp_ini_file)+'.zip'
            FL.DeleteFile(ConfigModule.get_config_value('sectionOne','test_case_folder',temp_ini_file)+'.zip')
            #Find Test case failed reason
            try:
                conn=DBUtil.ConnectToDataBase(sHost=server_id)
                FailReason = CommonUtil.FindTestCaseFailedReason(conn, sTestResultsRunId, TCID)
                conn.close()
            except Exception, e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                print Error_Detail
                print "Unable to find Fail Reason for Test case: ", TCID
                FailReason = ""

            #Update test case result
            conn=DBUtil.ConnectToDataBase(sHost=server_id)
            DBUtil.UpdateRecordInTable(conn, 'test_case_results', "Where run_id = '%s' and tc_id = '%s'" % (sTestResultsRunId, TCID), status='%s' % (sTestCaseStatus), testendtime='%s' % (sTestCaseEndTime), duration='%s' % (TestCaseDuration), failreason='%s' % (FailReason), logid='%s' % (TCLogFile))
            conn.close()
            #Update Performance Results if Its a Performance test case And if test case had Passed
            if DataType == 'Performance' and sTestCaseStatus == 'Passed':
                product_version = CommonUtil.GetProductVersion()
                print "machine_os:", TestRunID[4]
                print "tc_id:", list(TestCaseID)[0]
                print "tc_name:", TestCaseName[0]
                print "tc_section:", list(TestCaseID)[0]
                print "run_id:", sTestResultsRunId
                print "duration:", Global.transaction_duration
                print "memory_avg:", Global.transaction_deltamemory
                print "memory_peak:", Global.transaction_deltamemory
                #HWobj = Performance.ComputerHWInfo()
                #hwmodel = HWobj.CompInfo().HWModel
                #print "HW Model:", hwmodel

                conn=DBUtil.ConnectToDataBase(sHost=server_id)
                DBUtil.InsertNewRecordInToTable(conn, 'performance_results',
                        product_version=product_version,
                        tc_id=list(TestCaseID)[0],
                        run_id=sTestResultsRunId,
                        machine_os=TestRunID[4],
                        duration=Global.transaction_duration,
                        memory_avg=Global.transaction_startmemory,
                        memory_peak=Global.transaction_endmemory,
                        hw_model=hwmodel)
                conn.close()
            #Check if Test Set status is 'Cancelled' When it is stopped from Website
            conn=DBUtil.ConnectToDataBase(sHost=server_id)
            currentTestSetStatus = DBUtil.GetData(conn, "Select status"
                      " From test_run_env"
                      " Where run_id = '%s'" % sTestResultsRunId, False)
            conn.close()
            currentTestSetStatus = currentTestSetStatus[0][0]

            if currentTestSetStatus == 'Cancelled':
                print "Test Run status is Cancelled. Exiting the current Test Set... ", sTestResultsRunId
                CommonUtil.ExecLog(sModuleInfo, "Test Run status is Cancelled. Exiting the current Test Set...%s" % sTestResultsRunId, 2)
                break

        FL.DeleteFolder(ConfigModule.get_config_value('sectionOne','temp_run_file_path',temp_ini_file)+os.sep+TestRunID[0].replace(':','-'))
        #End of Test Set
        #Update entry in the TestResultsEnv table that this run is completed
        #test set end time
        conn=DBUtil.ConnectToDataBase(sHost=server_id)
        now = DBUtil.GetData(conn, "SELECT CURRENT_TIMESTAMP;", False)
        conn.close()
        sTestSetEndTime = str(now[0][0])
        iTestSetEndTime = now[0][0]
        TestSetDuration = CommonUtil.FormatSeconds((iTestSetEndTime - iTestSetStartTime).seconds)

        #Update Test Run tables based on the Test Set Status
        if currentTestSetStatus == 'Cancelled':
            conn=DBUtil.ConnectToDataBase(sHost=server_id)
            DBUtil.UpdateRecordInTable(conn, 'test_env_results', "Where run_id = '%s' and tester_id = '%s'" % (sTestResultsRunId, Userid), status='Cancelled', testendtime='%s' % (sTestSetEndTime), duration='%s' % (TestSetDuration))
            conn.close()
            print "Test Set Cancelled by the User"
            CommonUtil.ExecLog(sModuleInfo, "Test Set Cancelled by the User", 1)
        else:
            if (automation_count>0 or performance_count>0) and (automation_count+performance_count)==len(TestCaseLists):
                conn=DBUtil.ConnectToDataBase(sHost=server_id)
                print DBUtil.UpdateRecordInTable(conn, 'test_env_results', "Where run_id = '%s' and tester_id = '%s'" % (sTestResultsRunId, Userid), status='Complete', testendtime='%s' % (sTestSetEndTime), duration='%s' % (TestSetDuration))
                conn.close()
                #Update test_run_env schedule table with status so that this Test Set will not be run again
                conn=DBUtil.ConnectToDataBase(sHost=server_id)
                print DBUtil.UpdateRecordInTable(conn, 'test_run_env', "Where run_id = '%s' and tester_id = '%s'" % (TestRunID[0], Userid), status='Complete',email_flag=True)
                conn.close()
                print "Test Set Completed"
            #CommonUtil.ExecLog(sModuleInfo, "Test Set Completed", 1)

            ConfigModule.add_config_value('sectionOne','sTestStepExecLogId',"MainDriver",temp_ini_file)
    #Close DB Connection
    conn.close()
    return "pass"
#import dropbox
def upload_zip(server_id,port_id,temp_folder,run_id,file_name,base_path=False):
    """
    :param server_id: the location of the server
    :param port_id: the port it will listen on
    :param temp_folder: the logfiles folder
    :param run_id: respective run_id
    :param file_name: zipfile name for the run
    :param base_path: base_path for file save
    :return:
    """
    url_link='http://'+server_id+':'+str(port_id)+"/Home/UploadZip/"
    total_file_path=temp_folder+os.sep+run_id.replace(':','-')+os.sep+file_name
    fileObj=open(total_file_path,'rb')
    file_list={'docfile':fileObj}
    data_list={'run_id':run_id,'file_name':file_name,'base_path':base_path}
    r=requests.post(url_link,files=file_list,data=data_list)
    if r.status_code==200:
        print "Zip File is uploaded to production successfully"
    else:
        print "Zip File is not uploaded to production successfully"

# if __name__ == "__main__":
#     Global.sTestStepExecLogId = "MainDriver"
#     print main(Global.database_ip)
#     upload_zip('localhost',8000,'E:\Workspace\Framework_0.1\Automationz\Framework_0.1\AutomationFW\CoreFrameWork\LogFiles',"Fri-Aug-21-12:15:35-2015",'VOI-0204.zip')
