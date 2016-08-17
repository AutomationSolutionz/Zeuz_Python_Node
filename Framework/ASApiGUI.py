'''
Created on August 17, 2016

@author: minar
'''

import sys
from PyQt4 import QtGui
from Utilities import ASApiGUIdesign

import os
import time
import requests
import json
import MainDriverApi
from Utilities import ConfigModule, CommonUtil, FileUtilities
sys.path.append(os.path.dirname(os.getcwd()))


class GUIApp(QtGui.QMainWindow, ASApiGUIdesign.Ui_mainWindow):
    def __init__(self, parent=None):
        super(GUIApp, self).__init__(parent)
        self.setupUi(self)
        self.connectBtn.clicked.connect(self.connect_server)
        self.cancelBtn.clicked.connect(self.close_gui)

    def connect_server(self):
        username = unicode(self.username.toPlainText()).strip()
        password = unicode(self.password.text()).strip()
        project = unicode(self.project.toPlainText()).strip()
        team = unicode(self.team.toPlainText()).strip()

        user_info_object = {
            'username': username,
            'password': password,
            'project': project,
            'team': team
        }

        """self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        logged_in_widget = LoggedWidget(self)
        self.central_widget.addWidget(logged_in_widget)
        self.central_widget.setCurrentWidget(logged_in_widget)"""

        r = self.Get('login_api', user_info_object)
        print "Authentication check for user='%s', project='%s', team='%s'" % (username, project, team)
        if r:
            print "Authentication Successful"
            machine_object = self.update_machine(self.dependency_collection())
            if machine_object['registered']:
                tester_id = machine_object['name']
                run_again = self.RunProcess(tester_id)
                if run_again:
                    self.connect_server()
            else:
                return False
        else:
            print "Authentication Failed"
            return False

    def form_uri(self, resource_path):
        server = unicode(self.server.toPlainText()).strip()
        port = int(unicode(self.port.toPlainText()).strip())
        base_server_address = 'http://%s:%s/' % (str(server), str(port))
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

            project = unicode(self.project.toPlainText())
            team = unicode(self.team.toPlainText())

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
                'project': project,
                'team': team
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
            project = unicode(self.project.toPlainText())
            team = unicode(self.team.toPlainText())
            r = self.Get('get_all_dependency_name_api', {'project': project, 'team': team})
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

        """def new_window(self):
        app = QtGui.QApplication(sys.argv)
        w = QtGui.QWidget()
        b = QtGui.QLabel(w)
        b.setText("Welcome to ZeuZ Framework!")
        w.setGeometry(300, 300, 600, 150)
        b.move(50, 20)
        w.setWindowTitle("PyQT")
        w.show()
        sys.exit(app.exec_())"""

    def close_gui(self):
        print "Closed"
        self.close()


"""class LoggedWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LoggedWidget, self).__init__(parent)
        layout = QtGui.QHBoxLayout()
        self.label = QtGui.QLabel('Logging in...')
        layout.addWidget(self.label)
        self.setLayout(layout)"""


def main():
    app = QtGui.QApplication(sys.argv)
    form = GUIApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()



