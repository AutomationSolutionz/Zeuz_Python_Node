# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ASApiGUI.ui'
#
# Created: Wed Aug 17 12:08:40 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName(_fromUtf8("ASApiGUI"))
        mainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(mainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.username = QtGui.QTextEdit(self.centralwidget)
        self.username.setGeometry(QtCore.QRect(350, 80, 181, 31))
        self.username.setObjectName(_fromUtf8("username"))
        self.team = QtGui.QTextEdit(self.centralwidget)
        self.team.setGeometry(QtCore.QRect(350, 270, 181, 31))
        self.team.setObjectName(_fromUtf8("team"))
        self.server = QtGui.QTextEdit(self.centralwidget)
        self.server.setGeometry(QtCore.QRect(350, 350, 321, 31))
        self.server.setObjectName(_fromUtf8("server"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(200, 90, 66, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(200, 140, 66, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(200, 220, 91, 17))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_6 = QtGui.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(200, 420, 91, 17))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_5 = QtGui.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(200, 360, 111, 17))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.line_2 = QtGui.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(130, 320, 571, 16))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.label_4 = QtGui.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(200, 280, 81, 17))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.project = QtGui.QTextEdit(self.centralwidget)
        self.project.setGeometry(QtCore.QRect(350, 210, 181, 31))
        self.project.setObjectName(_fromUtf8("project"))
        self.port = QtGui.QTextEdit(self.centralwidget)
        self.port.setGeometry(QtCore.QRect(350, 410, 181, 31))
        self.port.setObjectName(_fromUtf8("port"))
        self.line = QtGui.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(130, 180, 571, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.connect = QtGui.QPushButton(self.centralwidget)
        self.connect.setGeometry(QtCore.QRect(570, 510, 98, 27))
        self.connect.setStyleSheet(_fromUtf8("background: #4499aa; color: white"))
        self.connect.setObjectName(_fromUtf8("connect"))
        self.cancel = QtGui.QPushButton(self.centralwidget)
        self.cancel.setGeometry(QtCore.QRect(450, 510, 98, 27))
        self.cancel.setObjectName(_fromUtf8("cancel"))
        self.password = QtGui.QLineEdit(self.centralwidget)
        self.password.setGeometry(QtCore.QRect(350, 136, 181, 31))
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        self.password.setObjectName(_fromUtf8("password"))
        mainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(mainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        mainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(_translate("mainWindow", "ZeuZ Framework - ASApiGUI", None))
        self.label.setText(_translate("mainWindow", "Username", None))
        self.label_2.setText(_translate("mainWindow", "Password", None))
        self.label_3.setText(_translate("mainWindow", "Project name", None))
        self.label_6.setText(_translate("mainWindow", "Server port", None))
        self.label_5.setText(_translate("mainWindow", "Server address", None))
        self.label_4.setText(_translate("mainWindow", "Team name", None))
        self.port.setHtml(_translate("mainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">80</p></body></html>", None))
        self.connect.setText(_translate("mainWindow", "Connect", None))
        self.cancel.setText(_translate("mainWindow", "Cancel", None))

