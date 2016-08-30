'''
Created on August 17, 2016

@author: minar
'''

import sys
from PyQt4 import QtGui, QtCore
import os
import time
import requests
import json
import MainDriverApi
from Utilities import ASApiGUIdesign, ASApiGUITeam, ASApiGUIProject
from Utilities import ConfigModule, CommonUtil, FileUtilities
sys.path.append(os.path.dirname(os.getcwd()))


class ApiThread(QtCore.QThread):
    def __init__(self, user_info):
        QtCore.QThread.__init__(self)
        self.user_info = user_info
        self.username = user_info['username']
        self.password = user_info['password']
        self.project = user_info['project']
        self.team = user_info['team']
        self.server = user_info['server']
        self.port = user_info['port']

    def run(self):
        r = self.Get('login_api', self.user_info)
        print "Authentication check for user='%s', project='%s', team='%s'" % (self.username, self.project, self.team)
        if r:
            print "Authentication Successful"
            machine_object = self.update_machine(self.dependency_collection())
            if machine_object['registered']:
                tester_id = machine_object['name']
                run_again = self.RunProcess(tester_id)
                if run_again:
                    ApiThread(self.user_info)
            else:
                return False
        else:
            print "Authentication Failed"
            return False

    def begin(self):
        self.start()

    def __del__(self):
        self.wait()

    def end(self):
        self.terminate()

    def form_uri(self, resource_path):
        base_server_address = 'http://%s:%s/' % (str(self.server), str(self.port))
        return base_server_address + resource_path + '/'

    def Get(self, resource_path, payload={}):
        return requests.get(self.form_uri(resource_path), params=json.dumps(payload)).json()

    def RunProcess(self, sTesterid):
        while 1:
            try:
                r = self.Get('is_run_submitted_api', {'machine_name': sTesterid})
                if r['run_submit']:
                    self.PreProcess()
                    value = MainDriverApi.main()
                    print "updating db with parameter"
                    if value == "pass":
                        break
                    print "Successfully updated db with parameter"
                else:
                    time.sleep(3)
                    if r['update']:
                        _r = self.Get('update_machine_with_time_api', {'machine_name': sTesterid})
            except Exception, e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
                    exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
                print Error_Detail
        return True

    def PreProcess(self):
        current_path = os.path.join(FileUtilities.get_home_folder(), os.path.join('Desktop', 'AutomationLog'))
        retVal = FileUtilities.CreateFolder(current_path, forced=False)
        if retVal:
            # now save it in the global_config.ini
            TEMP_TAG = 'Temp'
            file_name = ConfigModule.get_config_value(TEMP_TAG, '_file')
            current_path_file = os.path.join(current_path, file_name)
            FileUtilities.CreateFile(current_path_file)
            ConfigModule.clean_config_file(current_path_file)
            ConfigModule.add_section('sectionOne', current_path_file)
            ConfigModule.add_config_value('sectionOne', 'temp_run_file_path', current_path, current_path_file)

    def update_machine(self, dependency):
        try:
            # Get Local Info object
            oLocalInfo = CommonUtil.MachineInfo()

            local_ip = oLocalInfo.getLocalIP()
            testerid = (oLocalInfo.getLocalUser()).lower()

            product_ = 'ProductVersion'
            branch = ConfigModule.get_config_value(product_, 'branch')
            version = ConfigModule.get_config_value(product_, 'version')
            productVersion = branch + ":" + version

            if not dependency:
                dependency = ""
            _d = {}
            for x in dependency:
                t = []
                for i in x[1]:
                    _t = ['name', 'bit', 'version']
                    __t = {}
                    for index, _i in enumerate(i):
                        __t.update({_t[index]: _i})
                    if __t:
                        t.append(__t)
                _d.update({x[0]: t})
            dependency = _d
            update_object = {
                'machine_name': testerid,
                'local_ip': local_ip,
                'productVersion': productVersion,
                'dependency': dependency,
                'project': self.project,
                'team': self.team
            }
            r = self.Get('update_automation_machine_api', update_object)
            if r['registered']:
                print "Machine is registered as online with name: %s" % (r['name'])
            else:
                print "Machine is not registered as online"
            return r
        except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
                exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
            print Error_Detail

    def dependency_collection(self):
        try:
            dependency_tag = 'Dependency'
            dependency_option = ConfigModule.get_all_option(dependency_tag)
            r = self.Get('get_all_dependency_name_api', {'project': self.project, 'team': self.team})
            obtained_list = [x.lower() for x in r]
            # print "Dependency: ",dependency_list
            missing_list = list(set(obtained_list) - set(dependency_option))
            # print missing_list
            if missing_list:
                print ",".join(missing_list) + " missing from the configuration file - settings.conf"
                return False
            else:
                print "All the dependency present in the configuration file - settings.conf"
                final_dependency = []
                for each in r:
                    temp = []
                    each_dep_list = ConfigModule.get_config_value(dependency_tag, each).split(",")
                    # print each_dep_list
                    for each_item in each_dep_list:
                        if each_item.count(":") == 2:
                            name, bit, version = each_item.split(":")

                        else:
                            name = each_item.split(":")[0]
                            bit = 0
                            version = ''
                            # print name,bit,version
                        temp.append((name, bit, version))
                    final_dependency.append((each, temp))
                return final_dependency
        except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
                exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
            print Error_Detail


class TeamWidget(QtGui.QWidget, ASApiGUITeam.Ui_teamForm):
    def __init__(self, parent=None):
        super(TeamWidget, self).__init__(parent)
        self.setupUi(self)
        self.SecondNextBtn.clicked.connect(self.connect_server)
        self.firstBackBtn.clicked.connect(self.close_gui)

    def connect_server(self):
        #team = unicode(self.listView.toPlainText()).strip()
        #user_info_object.update({'team': team})

        projects = self.Get('get_user_projects_api', user_info_object)

        self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        project_widget = ProjectWidget(self)
        self.central_widget.addWidget(project_widget)
        self.central_widget.setCurrentWidget(project_widget)

    def close_gui(self):
        print "Closed"
        self.close()

    def form_uri(self, resource_path):
        base_server_address = 'http://%s:%s/' % (
        str(user_info_object['server']), str(user_info_object['port']))
        return base_server_address + resource_path + '/'

    def Get(self, resource_path, payload={}):
        return requests.get(self.form_uri(resource_path), params=json.dumps(payload)).json()


class ProjectWidget(QtGui.QWidget, ASApiGUIProject.Ui_projectForm):
    def __init__(self, parent=None):
        super(ProjectWidget, self).__init__(parent)
        self.setupUi(self)
        self.ThirdNextBtn.clicked.connect(self.connect_server)
        self.secondBackBtn.clicked.connect(self.close_gui)

    def connect_server(self):
        project = unicode(self.listView.text()).strip()
        user_info_object.update({'project': project})

        self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        project_widget = ProjectWidget(self)
        self.central_widget.addWidget(project_widget)
        self.central_widget.setCurrentWidget(project_widget)

    def close_gui(self):
        print "Closed"
        self.close()

    def form_uri(self, resource_path):
        base_server_address = 'http://%s:%s/' % (
        str(unicode(self.server.text()).strip()), str(unicode(self.port.text()).strip()))
        return base_server_address + resource_path + '/'

    def Get(self, resource_path, payload={}):
        return requests.get(self.form_uri(resource_path), params=json.dumps(payload)).json()


class GUIApp(QtGui.QMainWindow, ASApiGUIdesign.Ui_mainWindow):
    def __init__(self, parent=None):
        super(GUIApp, self).__init__(parent)
        self.setupUi(self)
        self.threads = []
        self.central_widget = None
        self.firstNextBtn.clicked.connect(self.connect_server)
        self.cancelBtn.clicked.connect(self.close_gui)

    def connect_server(self):
        username = unicode(self.username.text()).strip()
        password = unicode(self.password.text()).strip()
        server = unicode(self.server.text()).strip()
        port = int(unicode(self.port.text()).strip())

        user_info_object = {
            'username': username,
            'password': password,
            'server': server,
            'port': port
        }
        global user_info_object

        teams = self.Get('get_user_teams_api', user_info_object)

        self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        team_widget = TeamWidget(self)
        for each in teams:
            layout = QtGui.QHBoxLayout()
            team_widget.listView.rb = QtGui.QRadioButton("%s"%each[1])
            layout.addWidget(team_widget.listView.rb)
            team_widget.listView.setLayout(layout)
        self.central_widget.addWidget(team_widget)
        self.central_widget.setCurrentWidget(team_widget)

        """api = ApiThread(user_info_object)
        self.threads.append(api)
        api.begin()"""

    def close_gui(self):
        print "Closed"
        self.close()

    def form_uri(self, resource_path):
        base_server_address = 'http://%s:%s/' % (str(unicode(self.server.text()).strip()), str(unicode(self.port.text()).strip()))
        return base_server_address + resource_path + '/'

    def Get(self, resource_path, payload={}):
        return requests.get(self.form_uri(resource_path), params=json.dumps(payload)).json()


def main():
    app = QtGui.QApplication(sys.argv)
    form = GUIApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
