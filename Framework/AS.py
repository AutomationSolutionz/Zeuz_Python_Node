import sys,os
sys.path.append(os.path.dirname(os.getcwd()))
print "Connecting to database and verifying user authentication"
from Utilities import DataBaseUtilities as DB
from Utilities import ConfigModule
import os
import time
import MainDriver
from Utilities import FileUtilities, CommonUtil
import base64
def RunProcess(sTesterid):
    DATABASE_TAG='Database'
    server=ConfigModule.get_config_value(DATABASE_TAG,'database_address')
    while (1):
        try:
            conn = DB.ConnectToDataBase(sHost=server)
            status = DB.GetData(conn, "Select status from test_run_env where tester_id = '%s' and status in ('Submitted','Unassigned') limit 1 " % (sTesterid))
            conn.close()
            if len(status) == 0:
                continue
            if status[0] != "Unassigned":
                if status[0] == "Submitted":
                    #creating this folder in the desktop

                    current_path=os.path.join(FileUtilities.get_home_folder(),os.path.join('Desktop','AutomationLog'))
                    retVal= FileUtilities.CreateFolder(current_path,forced=False)
                    if retVal:
                        #now save it in the global_config.ini
                        TEMP_TAG='Temp'
                        file_name=ConfigModule.get_config_value(TEMP_TAG,'_file')
                        current_path_file= os.path.join(current_path,file_name)
                        FileUtilities.CreateFile(current_path_file)
                        ConfigModule.clean_config_file(current_path_file)
                        ConfigModule.add_section('sectionOne',current_path_file)
                        ConfigModule.add_config_value('sectionOne','temp_run_file_path',current_path,current_path_file)
                    value=MainDriver.main(server)
                    print "updating db with parameter"
                    if value=="pass":
                        break
                    print "Successfully updated db with parameter"

            elif status[0] == "Unassigned":
                time.sleep(3)
                conn = DB.ConnectToDataBase(sHost=server)
                last_updated_time= CommonUtil.TimeStamp("string")
                DB.UpdateRecordInTable(conn, "test_run_env", "where tester_id = '%s' and status = 'Unassigned'" % sTesterid, last_updated_time=last_updated_time)
                conn.close()
        except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()        
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
            print Error_Detail
    return True

def Login():
    try:
        authentication='Authentication'
        db_tag='Database'
        username=ConfigModule.get_config_value(authentication,'username')
        password=ConfigModule.get_config_value(authentication,'password')
        project=ConfigModule.get_config_value(authentication,'project')
        team=ConfigModule.get_config_value(authentication,'team')
        server=ConfigModule.get_config_value(db_tag,'database_address')
        port=ConfigModule.get_config_value(db_tag,'database_port')
        #print username,password,project,team,server,port
        print "Username = ",username, " : Project = ",project, " : Team = ", team

        result=Check_Credentials(username,password,project,team,server,port)
        if result:
            tester_id=update_machine(dependency_collection(project,team,server))
            if tester_id!=False:
                RunAgain = RunProcess(tester_id)
                if RunAgain == True:
                    Login()
            else:
                print "machine not generated"
        else:
            print "No User Found"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print Error_Detail

def update_machine(dependency):
    try:
        #Get Local Info object
        oLocalInfo = CommonUtil.MachineInfo()

        local_ip = oLocalInfo.getLocalIP()
        testerid = (oLocalInfo.getLocalUser()).lower()

        product_='ProductVersion'
        branch=ConfigModule.get_config_value(product_,'branch')
        version=ConfigModule.get_config_value(product_,'version')
        productVersion= branch+":"+version
        DATABASE_TAG='Database'
        server=ConfigModule.get_config_value(DATABASE_TAG,'database_address')
        UpdatedTime = CommonUtil.TimeStamp("string")
        query="select count(*) from permitted_user_list where user_level='Built_In_Automation' and user_names='%s'"%testerid
        Conn=DB.ConnectToDataBase(sHost=server)
        count=DB.GetData(Conn,query)
        Conn.close()
        if isinstance(count,list) and count[0]==0:
            #insert to the permitted_user_list
            temp_Dict={
                'user_names':testerid,
                'user_level':'Built_In_Automation',
                'email':testerid+"@machine.com"
            }
            Conn=DB.ConnectToDataBase(sHost=server)
            result=DB.InsertNewRecordInToTable(Conn,"permitted_user_list",**temp_Dict)
            Conn.close()
            
        #update the test_run_env table
        dict={
            'tester_id':testerid,
            'status':'Unassigned',
            'last_updated_time':UpdatedTime,
            'machine_ip':local_ip,
            'branch_version':productVersion
        }
        conn=DB.ConnectToDataBase(sHost=server)
        status = DB.GetData(conn, "Select status from test_run_env where tester_id = '%s'" % testerid)
        conn.close()
        for eachitem in status:
            if eachitem == "In-Progress":
                conn=DB.ConnectToDataBase(sHost=server)
                DB.UpdateRecordInTable(conn, "test_run_env", "where tester_id = '%s' and status = 'In-Progress'" % testerid, status="Cancelled")
                conn.close()
                conn=DB.ConnectToDataBase(sHost=server)
                DB.UpdateRecordInTable(conn, "test_env_results", "where tester_id = '%s' and status = 'In-Progress'" % testerid, status="Cancelled")
                conn.close()
            elif eachitem == "Submitted":
                conn=DB.ConnectToDataBase(sHost=server)
                DB.UpdateRecordInTable(conn, "test_run_env", "where tester_id = '%s' and status = 'Submitted'" % testerid, status="Cancelled")
                conn.close()
                conn=DB.ConnectToDataBase(sHost=server)
                DB.UpdateRecordInTable(conn, "test_env_results", "where tester_id = '%s' and status = 'Submitted'" % testerid, status="Cancelled")
                conn.close()
            elif eachitem == "Unassigned":
                conn=DB.ConnectToDataBase(sHost=server)
                DB.DeleteRecord(conn, "test_run_env", tester_id=testerid, status='Unassigned')
                conn.close()
        conn=DB.ConnectToDataBase(sHost=server)
        result=DB.InsertNewRecordInToTable(conn,"test_run_env",**dict)
        conn.close()
        if result:
            conn=DB.ConnectToDataBase(sHost=server)
            machine_id=DB.GetData(conn,"select id from test_run_env where tester_id='%s' and status='Unassigned'"%testerid)
            conn.close()
            if isinstance(machine_id,list) and len(machine_id)==1:
                machine_id=machine_id[0]
            if dependency:
                for each in dependency:
                    type_name=each[0]
                    listings=each[1]
                    for eachitem in listings:
                        temp_dict={
                            'name':eachitem[0],
                            'bit':eachitem[1],
                            'version':eachitem[2],
                            'type':type_name,
                            'machine_serial':machine_id
                        }
                        conn=DB.ConnectToDataBase(sHost=server)
                        result=DB.InsertNewRecordInToTable(conn,"machine_dependency_settings",**temp_dict)
                        conn.close()
            authentication_tag='Authentication'
            project=ConfigModule.get_config_value(authentication_tag,'project')
            team=ConfigModule.get_config_value(authentication_tag,'team')
            query="select project_id from projects where project_name='%s'"%project
            Conn=DB.ConnectToDataBase(sHost=server)
            project_id=DB.GetData(Conn,query)
            Conn.close()
            if isinstance(project_id,list) and len(project_id):
                project_id=project_id[0]
            else:
                project_id=''
            conn=DB.ConnectToDataBase(sHost=server)
            teamValue=DB.GetData(conn,"select id from team where team_name='%s' and project_id='%s'"%(team,project_id))
            conn.close()
            if isinstance(teamValue,list) and len(teamValue)==1:
                team_identity=teamValue[0]
            temp_dict={
                'machine_serial':machine_id,
                'project_id':project_id,
                'team_id':team_identity
            }
            conn=DB.ConnectToDataBase(sHost=server)
            result=DB.InsertNewRecordInToTable(conn,"machine_project_map",**temp_dict)
            conn.close()
            if result:
                return testerid
        return False
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print Error_Detail
    
def Check_Credentials(username,password,project,team,server,port):
    #get all the person enlisted with this project
    try:
        query="select distinct user_id::text from user_project_map upm, projects p where upm.project_id=p.project_id and p.project_name='%s'"%(project.strip())
        Conn=DB.ConnectToDataBase(sHost=server)
        user_list=DB.GetData(Conn, query)
        Conn.close()
        #user_list=user_list[0]
        message=",".join(user_list)
        #print message
        query="select count(*) from user_info ui, permitted_user_list pul where ui.full_name=pul.user_names and username='%s' and password='%s' and user_level not in ('email','Built_In_Automation', 'Manual') and user_id in (%s)"%(username,base64.b64encode(password),message)
        Conn=DB.ConnectToDataBase(sHost=server)
        count=DB.GetData(Conn,query)
        Conn.close()
        #print count
        if len(count)==1 and count[0]==1:
            return True 
        else:
            print "No user found with Name: %s"%username
            return False
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print Error_Detail

def dependency_collection(project,team,server):
    try:
        dependency_tag='Dependency'
        dependency_option=ConfigModule.get_all_option(dependency_tag)
        #print dependency_option
        query="select distinct project_id from projects where project_name='%s'"%project
        Conn=DB.ConnectToDataBase(sHost=server)
        project_id=DB.GetData(Conn,query)
        Conn.close()
        if isinstance(project_id,list) and len(project_id)==1:
            project_id=project_id[0]
        else:
            project_id=''
        query="select distinct dependency_name from dependency d ,dependency_management dm where d.id=dm.dependency and dm.project_id='%s' and dm.team_id=(select id from team where team_name='%s' and project_id='%s')"%(project_id,team,project_id)
        #print query
        Conn=DB.ConnectToDataBase(sHost=server)
        dependency_list=DB.GetData(Conn, query)
        Conn.close()
        obtained_list=[x.lower() for x in dependency_list]
        #print "Dependency: ",dependency_list
        missing_list=list(set(obtained_list)-set(dependency_option))
        #print missing_list
        if missing_list:
            print ",".join(missing_list)+" missing from the configuration file - settings.conf"
            return False
        else:
            print "All the dependency present in the configuration file - settings.conf"
            final_dependency=[]
            for each in dependency_list:
                temp=[]
                each_dep_list=ConfigModule.get_config_value(dependency_tag,each).split(",")
                #print each_dep_list
                for each_item in each_dep_list:
                    if each_item.count(":")==2:
                        name,bit,version=each_item.split(":")
                        #print name,bit,version
                    else:
                        name=each_item.split(":")[0]
                        bit=0
                        version=''
                        #print name,bit,version
                    temp.append((name,bit,version))
                final_dependency.append((each,temp))
            return  final_dependency
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print Error_Detail

if __name__=='__main__':
    Login()
