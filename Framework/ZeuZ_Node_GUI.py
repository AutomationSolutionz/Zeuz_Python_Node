# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

import json
import os
import sys
import time
from PyQt4 import QtGui, QtCore

import requests

import MainDriverApi
from Utilities.Zeuz_Node import ASApiGUITeam, ASApiGUIProject, ASApiGUIuser, ASApiGUIdependency, ASApiGUIbranch, ASApiGUIconnect
from Utilities import ConfigModule, CommonUtil, FileUtilities
from Utilities.Zeuz_Node import ASApiGUIdesign
from Utilities import ConfigModule

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
            uniqueid = (oLocalInfo.getUniqueId()).lower()

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
                'machine_name': self.username+"_"+uniqueid,
                'local_ip': local_ip,
                'productVersion': productVersion,
                'dependency': dependency,
                'project': self.project,
                'team': self.team
            }
            try:
                r = self.Get('update_automation_machine_api', update_object)
                if r['registered']:
                    print "Machine is registered as online with name: %s" % (r['name'])
                else:
                    print "Machine is not registered as online"
                return r
            except:
                r = self.Get('update_automation_machine_api', update_object)
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
                print ",".join(missing_list) + " missing from selected dependencies - ZeuZ_Node"
                return False
            else:
                print "All the dependencies present - ZeuZ_Node"
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


class ProjectWidget(QtGui.QWidget, ASApiGUIProject.Ui_projectForm):
    def __init__(self, parent=None):
        super(ProjectWidget, self).__init__(parent)
        self.setupUi(self)


class DependencyWidget(QtGui.QWidget, ASApiGUIdependency.Ui_dependencyForm):
    def __init__(self, parent=None):
        super(DependencyWidget, self).__init__(parent)
        self.setupUi(self)


class BranchWidget(QtGui.QWidget, ASApiGUIbranch.Ui_branchForm):
    def __init__(self, parent=None):
        super(BranchWidget, self).__init__(parent)
        self.setupUi(self)


class ConnectWidget(QtGui.QWidget, ASApiGUIconnect.Ui_connectForm):
    def __init__(self, parent=None):
        super(ConnectWidget, self).__init__(parent)
        self.setupUi(self)


class UserWidget(QtGui.QWidget, ASApiGUIuser.Ui_userForm):
    def __init__(self, parent=None):
        super(UserWidget, self).__init__(parent)
        self.setupUi(self)
        self.central_widget = None


class GUIApp(QtGui.QMainWindow, ASApiGUIdesign.Ui_mainWindow):
    def __init__(self, parent=None):
        super(GUIApp, self).__init__(parent)
        self.setupUi(self)
        self.threads = []
        self.user_info_object = {}
        self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.start_screen = UserWidget(self)
        self.second_screen = TeamWidget(self)
        self.third_screen = ProjectWidget(self)
        self.fourth_screen = DependencyWidget(self)
        self.fifth_screen = BranchWidget(self)
        self.final_screen = ConnectWidget(self)
        self.central_widget.addWidget(self.start_screen)
        self.central_widget.addWidget(self.second_screen)
        self.central_widget.addWidget(self.third_screen)
        self.central_widget.addWidget(self.fourth_screen)
        self.central_widget.addWidget(self.fifth_screen)
        self.central_widget.addWidget(self.final_screen)
        self.central_widget.setCurrentWidget(self.start_screen)

        self.start_screen.firstNextBtn.clicked.connect(self.user_action)
        self.start_screen.cancelBtn.clicked.connect(lambda: self.close())
        self.second_screen.firstBackBtn.clicked.connect(self.back_to_user)
        self.second_screen.SecondNextBtn.clicked.connect(self.team_action)
        self.third_screen.secondBackBtn.clicked.connect(self.back_to_team)
        self.third_screen.ThirdNextBtn.clicked.connect(self.project_action)
        self.fourth_screen.thirdBackBtn.clicked.connect(self.back_to_project)
        self.fourth_screen.FourthNextBtn.clicked.connect(self.dependency_action)
        self.fifth_screen.fourthBackBtn.clicked.connect(self.back_to_dependency)
        self.fifth_screen.FifthNextBtn.clicked.connect(self.connect_server)
        self.final_screen.fifthBackBtn.clicked.connect(self.back_to_branch)
        self.final_screen.closeBtn.clicked.connect(lambda: self.close())

    def user_action(self):
        username = unicode(self.start_screen.username.text()).strip()
        password = unicode(self.start_screen.password.text()).strip()
        server = unicode(self.start_screen.server.text()).strip()
        port = int(unicode(self.start_screen.port.text()).strip())

        self.user_info_object = {
            'username': username,
            'password': password,
            'server': server,
            'port': port
        }

        ConfigModule.add_config_value('Authentication', 'username', username)
        #ConfigModule.add_config_value('Authentication', 'password', password)
        ConfigModule.add_config_value('Server', 'server_address', server)
        ConfigModule.add_config_value('Server', 'server_port', str(port))

        teams = self.Get('get_user_teams_api', self.user_info_object)
        print teams

        layout = QtGui.QFormLayout()
        for each in teams:
            self.second_screen.listView.rb = QtGui.QRadioButton("%s" % each[0])
            layout.addWidget(self.second_screen.listView.rb)
        self.second_screen.listView.setLayout(layout)
        self.start_screen.hide()
        self.second_screen.show()

    def team_action(self):
        for radioButton in self.second_screen.findChildren(QtGui.QRadioButton):
            if radioButton.isChecked():
                team = unicode(radioButton.text())
                print "Team Selected: ", team
                self.user_info_object.update({'team': team})
                ConfigModule.add_config_value('Authentication', 'team', team)

        projects = self.Get('get_user_projects_api', self.user_info_object)
        print projects

        layout = QtGui.QFormLayout()
        for each in projects:
            self.third_screen.listView.rb = QtGui.QRadioButton("%s" % each[0])
            layout.addWidget(self.third_screen.listView.rb)
        self.third_screen.listView.setLayout(layout)
        self.second_screen.hide()
        self.third_screen.show()

    def project_action(self):
        for radioButton in self.third_screen.findChildren(QtGui.QRadioButton):
            if radioButton.isChecked():
                project = unicode(radioButton.text())
                print "Project Selected: ", project
                self.user_info_object.update({'project': project})
                ConfigModule.add_config_value('Authentication', 'project', project)

        dependencies = self.Get('get_dependency_lists_api', self.user_info_object)
        print dependencies

        layout = QtGui.QFormLayout()
        for each in dependencies:
            self.fourth_screen.label = QtGui.QLabel("%s" % each[0])
            layout.addWidget(self.fourth_screen.label)
            for element in each[1]:
                self.fourth_screen.cb = QtGui.QCheckBox("%s" % element)
                layout.addWidget(self.fourth_screen.cb)
        self.fourth_screen.setLayout(layout)
        self.third_screen.hide()
        self.fourth_screen.show()

    def dependency_action(self):
        dependencies = []
        for dep in self.fourth_screen.findChildren(QtGui.QLabel):
            dependencies.append(unicode(dep.text()))
        print dependencies

        dep_options = []
        for checkBox in self.fourth_screen.findChildren(QtGui.QCheckBox):
            if checkBox.isChecked():
                dep = unicode(checkBox.text())
                print "Dependency selected: ", dep
                dep_options.append(dep)
        print dep_options

        branches = self.Get('get_branch_version_list_api', self.user_info_object)
        print branches

        layout = QtGui.QFormLayout()
        for each in branches:
            self.fifth_screen.label = QtGui.QLabel("%s" % each[0])
            layout.addWidget(self.fifth_screen.label)
            for element in each[1]:
                self.fifth_screen.cb = QtGui.QCheckBox("%s" % element)
                layout.addWidget(self.fifth_screen.cb)
        self.fifth_screen.setLayout(layout)
        self.fourth_screen.hide()
        self.fifth_screen.show()

    def connect_server(self):
        api = ApiThread(self.user_info_object)
        self.threads.append(api)
        api.begin()

        branch_options = []
        for checkBox in self.fifth_screen.findChildren(QtGui.QCheckBox):
            if checkBox.isChecked():
                dep = unicode(checkBox.text())
                print "Branch version selected: ", dep
                branch_options.append(dep)
        print branch_options

        self.fifth_screen.hide()
        self.final_screen.show()

    def back_to_user(self):
        self.second_screen.close()
        self.clear_layout(self.second_screen.listView.layout())
        QtCore.QObjectCleanupHandler().add(self.second_screen.listView.layout())
        self.start_screen.show()
        self.central_widget.setCurrentWidget(self.start_screen)

    def back_to_team(self):
        self.third_screen.close()
        self.clear_layout(self.third_screen.listView.layout())
        QtCore.QObjectCleanupHandler().add(self.third_screen.listView.layout())
        self.second_screen.show()
        self.central_widget.setCurrentWidget(self.second_screen)

    def back_to_project(self):
        self.fourth_screen.close()
        self.clear_layout(self.fourth_screen.layout())
        QtCore.QObjectCleanupHandler().add(self.fourth_screen.layout())
        self.third_screen.show()
        self.central_widget.setCurrentWidget(self.third_screen)

    def back_to_dependency(self):
        self.fifth_screen.close()
        self.clear_layout(self.fifth_screen.layout())
        QtCore.QObjectCleanupHandler().add(self.fifth_screen.layout())
        self.fourth_screen.show()
        self.central_widget.setCurrentWidget(self.fourth_screen)

    def back_to_branch(self):
        self.final_screen.close()
        self.clear_layout(self.final_screen.layout())
        QtCore.QObjectCleanupHandler().add(self.final_screen.layout())
        self.fifth_screen.show()
        self.central_widget.setCurrentWidget(self.fifth_screen)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def form_uri(self, resource_path):
        base_server_address = 'http://%s:%s/' % (
            str(unicode(self.start_screen.server.text()).strip()), str(unicode(self.start_screen.port.text()).strip()))
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
