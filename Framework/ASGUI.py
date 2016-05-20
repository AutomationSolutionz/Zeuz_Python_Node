import time
import sys
import threading
import os
import ConfigParser
import base64

import wx
import wx.wizard
from Utilities import DataBaseUtilities as DB, CommonUtil, FileUtilities
from FrameWork import MainDriver


class RedirectText(object):
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl
    def write(self,string):
        self.out.WriteText(string)

class WizardPage(wx.wizard.PyWizardPage):
    def __init__(self, parent, title):
        wx.wizard.PyWizardPage.__init__(self, parent)
        self.next = None
        self.prev = None
        self.initializeUI(title)

    def initializeUI(self, title):
        # create grid layout manager
        self.sizer = wx.GridBagSizer(5)
        self.SetSizerAndFit(self.sizer)

    def addWidget(self, widget, pos, span):
        self.sizer.Add(widget, pos, span, wx.EXPAND)

    # getters and setters
    def SetPrev(self, prev):
        self.prev = prev

    def SetNext(self, next):
        self.next = next

    def GetPrev(self):
        return self.prev

    def GetNext(self):
        return self.next
class MyWizard(wx.wizard.Wizard):
    def __init__(self):
        """Constructor"""
        wx.wizard.Wizard.__init__(self, None, -1, "Automation Solutionz")
        self.SetPageSize((500, 350))
        self.login_page=self.create_login_page()
        self.project_team_page=self.create_project_team_page()
        self.dependency_page=self.create_dependency_page()
        self.version_page=self.create_version_page()
        self.console_log=self.create_log_page()
        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGED,self.pageChanged)
        self.Bind(wx.wizard.EVT_WIZARD_FINISHED,self.Destruction)
        self.login_page.SetNext(self.project_team_page)
        self.project_team_page.SetNext(self.dependency_page)
        self.dependency_page.SetNext(self.version_page)
        self.version_page.SetNext(self.console_log)
        self.RunWizard(self.login_page)
    def create_project_team_page(self):
        project_team_page=WizardPage(self,'project_team_page')
        project_team_page.SetName('projectPage')
        return project_team_page
    def create_version_page(self):
        version_page=WizardPage(self,'version_page')
        version_page.SetName('versionPage')
        return version_page
    def Destruction(self):
        self.Destroy()
    def create_dependency_page(self):
        dependency_page=WizardPage(self,"dependency_page")
        dependency_page.SetName('dependencyPage')
        return dependency_page
    def create_login_page(self):
        login_page=WizardPage(self,"login_page")
        Username_label=wx.StaticText(login_page,label="Username: ")
        login_page.addWidget(Username_label,(1,10),(1,10))
        self.username = wx.TextCtrl(login_page)
        self.username.SetValue('riz')
        login_page.addWidget(self.username,(1,20),(1,20))
        password_label = wx.StaticText(login_page,label="Password: ")
        login_page.addWidget(password_label,(2,10),(1,10))
        self.password = wx.TextCtrl(login_page,style=wx.TE_PASSWORD)
        self.password.SetValue('.')
        login_page.addWidget(self.password,(2,20),(1,20))
        server_text=wx.StaticText(login_page,label="Server: ")
        login_page.addWidget(server_text,(3,10),(1,10))
        self.ServerText=wx.TextCtrl(login_page)
        self.ServerText.SetValue('127.0.0.1')
        login_page.addWidget(self.ServerText,(3,20),(1,20))
        port_text=wx.StaticText(login_page,label="Port: ")
        login_page.addWidget(port_text,(4,10),(1,10))
        self.port=wx.TextCtrl(login_page)
        self.port.SetValue('5432')
        login_page.addWidget(self.port,(4,20),(1,20))
        return login_page
    def create_log_page(self):
        console_log=WizardPage(self,"console_page")
        console_log.SetName("consolePage")
        self.log=wx.TextCtrl(console_log,style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_AUTO_SCROLL,size=(500,350))
        #self.log.Disable()
        dir=RedirectText(self.log)
        sys.stdout=dir
        sys.stderr=dir
        return console_log
    def OnUpdate(self,event):
        username = self.username.GetValue()
        password = self.password.GetValue()
        server = self.ServerText.GetValue()
        port = self.port.GetValue()
        forward_btn = self.FindWindowById(wx.ID_FORWARD)
        if username and password and server and port:
            forward_btn.Enable()
        else:
            forward_btn.Disable()

    def onChoice(self,evt):
        temp=str(evt.GetId()).split('1000')[1].strip()
        choice=(int(temp),int(evt.GetEventObject().GetCurrentSelection()))
        selected_data=self.dependency[choice[0]-1][1][choice[1]]
        c=[str(x[0]) for x in selected_data[1]]
        v=getattr(self,'version_'+str(choice[0]))
        t=getattr(self,'bit_'+str(choice[0]))
        t.Clear()
        v.Clear()
        #print c
        if c:
            for each in c:
                t.Append(each)
        else:
            t.Append("N/A")
            v.Append("N/A")
        self.check_valid()
    def check_valid(self):
        temp_object={}
        okay=False
        forward_btn=self.FindWindowById(wx.ID_FORWARD)
        for each in range(1,len(self.dependency)+1):
            temp=getattr(self,'dependency_'+str(each))
            bit=getattr(self,'bit_'+str(each))
            version=getattr(self,'version_'+str(each))
            if temp.GetCurrentSelection()==-1 or bit.GetCurrentSelection()==-1 or version.GetCurrentSelection()==-1 :
                okay=False
            else:
                name=temp.GetString(temp.GetCurrentSelection())
                bit=bit.GetString(bit.GetCurrentSelection())
                version=version.GetString(version.GetCurrentSelection())
                tmp_string=name+":"+bit+":"+version
                temp_object.update({self.dependency[each-1][0]:tmp_string})
                okay=True
        if okay:
            self.selected_dependency=temp_object
            #print self.selected_dependency
            forward_btn.Enable()
        else:
            forward_btn.Disable()

    def onBit(self,evt):
        temp_id=str(evt.GetId()).split('2000')[1].strip()
        b=getattr(self,'bit_'+temp_id)
        #print temp_id
        #print b.GetCurrentSelection()
        d=getattr(self,'dependency_'+temp_id)
        if b.GetString(b.GetCurrentSelection())!='N/A':
            index=int(temp_id)
            selected_data=self.dependency[index-1][1][d.GetCurrentSelection()][1][b.GetCurrentSelection()][1]
            #print selected_data
            v=getattr(self,'version_'+temp_id)
            v.Clear()
            for each in selected_data:
                v.Append(str(each))
        self.check_valid()
    def onVersion(self,evt):
        self.check_valid()
    def onBranch_Version(self,evt):
        self.check_version_valid()
    def onBranch(self,evt):
        obj=getattr(self,'branch_name')
        data=self.branch[obj.GetCurrentSelection()][1]
        v=getattr(self,'branch_version')
        v.Clear()
        for each in data:
            v.Append(each)
        self.check_version_valid()
    def check_version_valid(self):
        branch_okay=False
        branch_name=getattr(self,'branch_name')
        branch_version=getattr(self,'branch_version')
        forward_btn=self.FindWindowById(wx.ID_FORWARD)
        #print branch_name.GetCurrentSelection()
        #print branch_version.GetCurrentSelection()
        if branch_name.GetCurrentSelection()==-1 or branch_version.GetCurrentSelection()==-1:
            branch_okay=False
        else:
            tmp_string=branch_name.GetString(branch_name.GetCurrentSelection())+":"+branch_version.GetString(branch_version.GetCurrentSelection())
            #print tmp_string
            branch_okay=True
        if branch_okay:
            self.product_version=tmp_string
            forward_btn.Enable()
        else:
            forward_btn.Disable()
    def on_team_change(self,evt):
        self.check_project()
    def check_project(self):
        project_elem=getattr(self,'project_name')
        t=getattr(self,'team_name')
        forward_btn=self.FindWindowById(wx.ID_FORWARD)
        if project_elem.GetCurrentSelection()==-1 or t.GetCurrentSelection()==-1:
            forward_btn.Disable()
        else:
            self.project_name_full=project_elem.GetString(project_elem.GetCurrentSelection())
            self.team_name_full=t.GetString(t.GetCurrentSelection())
            forward_btn.Enable()
    def on_project_change(self,evt):
        project_elem=getattr(self,'project_name')
        project_name = project_elem.GetString(project_elem.GetCurrentSelection())
        username=self.username.GetValue()
        password=self.password.GetValue()
        server = self.ServerText.GetValue()
        query="select distinct team_name from team_info ti, team t where ti.team_id =t.id and t.project_id=(select project_id from projects where project_name='%s') and ti.user_id=(select user_id::text from permitted_user_list pul, user_info ui where ui.full_name=pul.user_names and ui.username='%s' and ui.password='%s')"%(project_name,username,base64.b64encode(password))
        #print query
        Conn=DB.ConnectToDataBase(sHost=server)
        team_list=DB.GetData(Conn,query)
        Conn.close()
        t=getattr(self,'team_name')
        t.Clear()
        for each in team_list:
            t.Append(str(each))
        self.check_project()
    def pageChanged(self,evt):
        page=evt.GetPage()
        if page.GetName()=='projectPage':
            username = self.username.GetValue()
            password = self.password.GetValue()
            server = self.ServerText.GetValue()
            port = self.port.GetValue()
            query="select distinct p.project_name from projects p,user_project_map upm, project_team_map  ptm where p.project_id=upm.project_id and p.project_id=ptm.project_id and upm.project_id=ptm.project_id  and upm.user_id=(select user_id from permitted_user_list pul, user_info ui where ui.full_name=pul.user_names and ui.username='%s' and ui.password='%s')"%(username,base64.b64encode(password))
            Conn=DB.ConnectToDataBase(sHost=server)
            project_list=DB.GetData(Conn,query)
            Conn.close()
            final_list=[]
            for each in project_list:
                query="select count(*) from project_team_map where project_id=(select project_id from projects where project_name='%s')"%each
                Conn=DB.ConnectToDataBase(sHost=server)
                count=DB.GetData(Conn,query)
                Conn.close()
                if len(count)==1 and count[0]>0:
                    final_list.append(each)
            project_list=final_list
            forward_btn=self.FindWindowById(wx.ID_FORWARD)
            forward_btn.Disable()
            count=1
            project_span=wx.StaticText(self.project_team_page,label='Project: ')
            self.project_team_page.addWidget(project_span,(count,1),(count,1))
            project_choice=wx.Choice(self.project_team_page,choices=project_list)
            self.project_team_page.addWidget(project_choice,(count,10),(count,20))
            count+=1
            team_span=wx.StaticText(self.project_team_page,label='Team: ')
            self.project_team_page.addWidget(team_span,(count,1),(count,1))
            team_choice=wx.Choice(self.project_team_page,choices=[])
            self.project_team_page.addWidget(team_choice,(count,10),(count,20))
            self.Bind(wx.EVT_CHOICE,self.on_project_change,project_choice)
            self.Bind(wx.EVT_CHOICE,self.on_team_change,team_choice)
            setattr(self,'project_name',project_choice)
            setattr(self,'team_name',team_choice)

        if page.GetName()=='versionPage':
            username = self.username.GetValue()
            password = self.password.GetValue()
            server = self.ServerText.GetValue()
            port = self.port.GetValue()
            project = self.project_name_full
            team = self.team_name_full
            branch_query="select branch_name,array_agg(version_name) from branch_management bm,branch b,versions v where bm.branch=b.id and b.id =v.id and bm.project_id=(select project_id from projects where project_name='%s') and bm.team_id=(select id from team where project_id=(select project_id from projects where project_name='%s') and team_name='%s') group by b.branch_name"%(project,project,team)
            Conn=DB.ConnectToDataBase(sHost=server)
            branch_version=DB.GetData(Conn,branch_query,False)
            Conn.close()
            self.branch=branch_version
            #print self.branch
            count=1
            forward_btn=self.FindWindowById(wx.ID_FORWARD)
            #forward_btn.Disable()
            branch_span=wx.StaticText(self.version_page,label='Branch: ')
            b=[x[0] for x in self.branch]
            self.version_page.addWidget(branch_span,(count,1),(count,1))
            branch_choice=wx.Choice(self.version_page,choices=b)
            self.version_page.addWidget(branch_choice,(count,10),(count,10))
            branch_version_choice=wx.Choice(self.version_page,choices=[])
            self.version_page.addWidget(branch_version_choice,(count,22),(count,8))
            self.Bind(wx.EVT_CHOICE,self.onBranch,branch_choice)
            self.Bind(wx.EVT_CHOICE,self.onBranch_Version,branch_version_choice)
            setattr(self,'branch_name',branch_choice)
            setattr(self,'branch_version',branch_version_choice)

        if page.GetName()=='dependencyPage':
            username = self.username.GetValue()
            password = self.password.GetValue()
            server = self.ServerText.GetValue()
            port = self.port.GetValue()
            project = self.project_name_full
            team = self.team_name_full
            forward_btn=self.FindWindowById(wx.ID_FORWARD)
            forward_btn.Disable()
            query="select dependency_name,array_agg(distinct name) from dependency_management dm,dependency d,dependency_name dn where d.project_id=dm.project_id and d.id=dm.dependency and dm.project_id=(select project_id from projects where project_name='%s') and dm.team_id=(select id from team where project_id=(select project_id from projects where project_name='%s') and team_name='%s') and dn.dependency_id=d.id group by dependency_name"%(project,project,team)
            #print query
            Conn=DB.ConnectToDataBase(sHost=server)
            dependency=DB.GetData(Conn,query,False)
            Conn.close()
            final=[]
            for each in dependency:
                tag=each[0]
                temp=[]
                for eachitem in each[1]:
                    query="select bit_name,array_agg(distinct version) from dependency_values dv, dependency_name dn,dependency d,dependency_management dm where dv.id=dn.id and d.id=dn.dependency_id and dm.dependency=d.id and dm.project_id=(select project_id from projects where project_name='%s') and dm.team_id=(select id from team where project_id=(select project_id from projects where project_name='%s') and team_name='%s') and d.dependency_name='%s' and dn.name='%s' group by bit_name"%(project,project,team,tag,eachitem)
                    Conn=DB.ConnectToDataBase(sHost=server)
                    bit_version=DB.GetData(Conn,query,False)
                    Conn.close()
                    temp.append((eachitem,bit_version))
                final.append((tag,temp))
            #dependency=[('Browser',[('Chrome',[(32,[53,65.63]),(64,[56,76,73])]),('Firefox',[(32,[])])]),('Platform',[('Android',[]),('PC',[])])]
            #print final
            self.dependency=final
            count=1
            #print self.dependency
            for each in self.dependency:
                c=[x[0] for x in each[1]]
                span=wx.StaticText(self.dependency_page,label=each[0]+":")
                temp_id='1000'+str(count)
                choices=wx.Choice(self.dependency_page,id=int(temp_id),choices=c)#,pos=(x_pos+20,y_pos+5))
                temp_id='2000'+str(count)
                bit=wx.Choice(self.dependency_page,id=int(temp_id),choices=[])
                temp_id='3000'+str(count)
                versiont=wx.Choice(self.dependency_page,id=int(temp_id),choices=[])
                #print count
                self.dependency_page.addWidget(span,(count,1),(count,1))
                self.dependency_page.addWidget(choices,(count,10),(count,10))
                self.dependency_page.addWidget(bit,(count,22),(count,8))
                self.dependency_page.addWidget(versiont,(count,32),(count,8))
                self.Bind(wx.EVT_CHOICE,self.onChoice,choices)
                self.Bind(wx.EVT_CHOICE,self.onBit,bit)
                self.Bind(wx.EVT_CHOICE,self.onVersion,versiont)
                setattr(self,'dependency_'+str(int(count)),choices)
                setattr(self,'bit_'+str(int(count)),bit)
                setattr(self,'version_'+str(int(count)),versiont)
                count+=1
        if page.GetName()=='consolePage':
            username=self.username.GetValue()
            password=self.password.GetValue()
            server = self.ServerText.GetValue()
            port = self.port.GetValue()
            project = self.project_name_full
            team = self.team_name_full
            worker=AS(username,password,project,team,server,port,self.selected_dependency,self.product_version)
            worker.setName("Automation Solutionz is running")
            worker.start()
class AS(threading.Thread):
    def __init__(self,username,password,project,team,server,port,dependency,product):
        threading.Thread.__init__(self)
        self.username=username
        self.password=password
        self.project=project
        self.team=team
        self.server=server
        self.port=port
        self.dep=dependency
        self.p=product
    def run(self):
        print threading.currentThread().getName()
        if self.check_credential():
            value = self.run_process(self.update_machine(self.dep,self.p))
            if value:
                self.run()
        else:
            self.update_machine(self.dep,self.p)
    def run_process(self,sTesterid):
        while (1):
            try:
                conn = DB.ConnectToDataBase(sHost=self.server)
                status = DB.GetData(conn, "Select status from test_run_env where tester_id = '%s' and status in ('Submitted','Unassigned') limit 1 " % (sTesterid))
                conn.close()
                if len(status) == 0:
                    continue
                if status[0] != "Unassigned":
                    if status[0] == "Submitted":
                        #first Create a temp folder in the samefolder
                        current_path=os.getcwd()+os.sep+'LogFiles'
                        retVal= FileUtilities.CreateFolder(current_path,forced=False)
                        if retVal:
                            Global.RunIdTempPath=current_path
                            #now save it in the global_config.ini
                            current_path_file=os.getcwd()+os.sep+'global_config.ini'
                            config=ConfigParser.SafeConfigParser()
                            config.add_section('sectionOne')
                            config.set('sectionOne','temp_run_file_path',current_path)
                            with (open(current_path_file,'w')) as configFile:
                                config.write(configFile)
                        value=MainDriver.main(self.server)
                        print "updating db with parameter"
                        if value=="pass":
                            break
                        print "Successfully updated db with parameter"

                elif status[0] == "Unassigned":
                    time.sleep(3)
                    conn = DB.ConnectToDataBase(sHost=self.server)
                    last_updated_time= CommonUtil.TimeStamp("string")
                    DB.UpdateRecordInTable(conn, "test_run_env", "where tester_id = '%s' and status = 'Unassigned'" % sTesterid, last_updated_time=last_updated_time)
                    conn.close()
            except Exception, e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
                print Error_Detail
        return True

    def update_machine(self,dependency,product_version):
        try:
            #Get Local Info object
            oLocalInfo = CommonUtil.LocalInfo()

            if os.path.isdir(Global.NetworkFolder) != True:
                print "Failed to access Network folder"
                #return False
                local_ip = oLocalInfo.getLocalIP() #+ " - Network Error"
            else:
                local_ip = oLocalInfo.getLocalIP()
            testerid = (oLocalInfo.getLocalUser()).lower()
            #product_version = ' '
            productVersion=product_version
            UpdatedTime = CommonUtil.TimeStamp("string")
            query="select count(*) from permitted_user_list where user_level='Automation' and user_names='%s'"%testerid
            Conn=DB.ConnectToDataBase(sHost=self.server)
            count=DB.GetData(Conn,query)
            Conn.close()
            if isinstance(count,list) and count[0]==0:
                #insert to the permitted_user_list
                temp_Dict={
                    'user_names':testerid,
                    'user_level':'Automation',
                    'email':testerid+"@machine.com"
                }
                Conn=DB.ConnectToDataBase(sHost=self.server)
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
            conn=DB.ConnectToDataBase(sHost=self.server)
            status = DB.GetData(conn, "Select status from test_run_env where tester_id = '%s'" % testerid)
            conn.close()
            for eachitem in status:
                if eachitem == "In-Progress":
                    conn=DB.ConnectToDataBase(sHost=self.server)
                    DB.UpdateRecordInTable(conn, "test_run_env", "where tester_id = '%s' and status = 'In-Progress'" % testerid, status="Cancelled")
                    conn.close()
                    conn=DB.ConnectToDataBase(sHost=self.server)
                    DB.UpdateRecordInTable(conn, "test_env_results", "where tester_id = '%s' and status = 'In-Progress'" % testerid, status="Cancelled")
                    conn.close()
                elif eachitem == "Submitted":
                    conn=DB.ConnectToDataBase(sHost=self.server)
                    DB.UpdateRecordInTable(conn, "test_run_env", "where tester_id = '%s' and status = 'Submitted'" % testerid, status="Cancelled")
                    conn.close()
                    conn=DB.ConnectToDataBase(sHost=self.server)
                    DB.UpdateRecordInTable(conn, "test_env_results", "where tester_id = '%s' and status = 'Submitted'" % testerid, status="Cancelled")
                    conn.close()
                elif eachitem == "Unassigned":
                    conn=DB.ConnectToDataBase(sHost=self.server)
                    DB.DeleteRecord(conn, "test_run_env", tester_id=testerid, status='Unassigned')
                    conn.close()
            conn=DB.ConnectToDataBase(sHost=self.server)
            result=DB.InsertNewRecordInToTable(conn,"test_run_env",**dict)
            conn.close()
            if result:
                conn=DB.ConnectToDataBase(sHost=self.server)
                machine_id=DB.GetData(conn,"select id from test_run_env where tester_id='%s' and status='Unassigned'"%testerid)
                conn.close()
                if isinstance(machine_id,list) and len(machine_id)==1:
                    machine_id=machine_id[0]
                for each in dependency.keys():
                    type_name=each
                    listings=dependency[each]
                    listings=listings.split(":")
                    name=listings[0]
                    if listings[1].strip()=='N/A':
                        bit=0
                    else:
                        bit=int(listings[1])
                    if listings[1].strip()=='N/A':
                        version='Nil'
                    else:
                        version=listings[2].strip()

                    temp_dict={
                        'name':name,
                        'bit':bit,
                        'version':version,
                        'type':type_name,
                        'machine_serial':machine_id
                    }
                    conn=DB.ConnectToDataBase(sHost=self.server)
                    result=DB.InsertNewRecordInToTable(conn,"machine_dependency_settings",**temp_dict)
                    conn.close()
                query="select project_id from projects where project_name='%s'"%self.project
                Conn=DB.ConnectToDataBase(sHost=self.server)
                project_id=DB.GetData(Conn,query)
                Conn.close()
                if isinstance(project_id,list) and len(project_id):
                    project_id=project_id[0]
                else:
                    project_id=''
                conn=DB.ConnectToDataBase(sHost=self.server)
                teamValue=DB.GetData(conn,"select id from team where team_name='%s' and project_id='%s'"%(self.team,project_id))
                conn.close()
                if isinstance(teamValue,list) and len(teamValue)==1:
                    team_identity=teamValue[0]
                temp_dict={
                    'machine_serial':machine_id,
                    'project_id':project_id,
                    'team_id':team_identity
                }
                conn=DB.ConnectToDataBase(sHost=self.server)
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
    def check_credential(self):
        try:
            query="select distinct user_id::text from user_project_map upm, projects p where upm.project_id=p.project_id and p.project_name='%s'"%(self.project.strip())
            Conn=DB.ConnectToDataBase(sHost=self.server)
            user_list=DB.GetData(Conn, query)
            Conn.close()
            #user_list=user_list[0]
            message=",".join(user_list)
            query="select count(*) from user_info ui, permitted_user_list pul where ui.full_name=pul.user_names and username='%s' and password='%s' and user_level not in ('email','Automation', 'Manual') and user_id in (%s)"%(self.username,base64.b64encode(self.password),message)
            Conn=DB.ConnectToDataBase(sHost=self.server)
            count=DB.GetData(Conn,query)
            Conn.close()
            if len(count)==1 and count[0]==1:
                return True
            else:
                print "No user found with Name: %s"%self.username
                return False
        except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
            print Error_Detail

def main():
    """"""
    wizard = MyWizard()

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(redirect=True)
    main()
    app.MainLoop()
    print 'ok'