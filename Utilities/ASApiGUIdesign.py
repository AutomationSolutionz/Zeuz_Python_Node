# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ASApiGUI.ui'
#
# Created: Mon Aug 29 16:40:13 2016
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
        mainWindow.setObjectName(_fromUtf8("ZeuZ Framework - ASAPI GUI"))
        mainWindow.resize(738, 484)
        self.centralwidget = QtGui.QWidget(mainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(170, 74, 71, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(170, 124, 66, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_6 = QtGui.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(170, 274, 91, 17))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_5 = QtGui.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(170, 214, 111, 17))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.line_2 = QtGui.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(100, 174, 571, 16))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.firstNextBtn = QtGui.QPushButton(self.centralwidget)
        self.firstNextBtn.setGeometry(QtCore.QRect(540, 364, 98, 27))
        self.firstNextBtn.setStyleSheet(_fromUtf8("background: #4499aa; color: white"))
        self.firstNextBtn.setObjectName(_fromUtf8("firstNextBtn"))
        self.cancelBtn = QtGui.QPushButton(self.centralwidget)
        self.cancelBtn.setGeometry(QtCore.QRect(420, 364, 98, 27))
        self.cancelBtn.setObjectName(_fromUtf8("cancelBtn"))
        self.password = QtGui.QLineEdit(self.centralwidget)
        self.password.setGeometry(QtCore.QRect(310, 120, 211, 31))
        self.password.setText(_fromUtf8(""))
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        self.password.setObjectName(_fromUtf8("password"))
        self.username = QtGui.QLineEdit(self.centralwidget)
        self.username.setGeometry(QtCore.QRect(310, 70, 211, 27))
        self.username.setObjectName(_fromUtf8("username"))
        self.server = QtGui.QLineEdit(self.centralwidget)
        self.server.setGeometry(QtCore.QRect(310, 210, 351, 27))
        self.server.setObjectName(_fromUtf8("server"))
        self.port = QtGui.QLineEdit(self.centralwidget)
        self.port.setGeometry(QtCore.QRect(310, 270, 211, 27))
        self.port.setObjectName(_fromUtf8("port"))
        mainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(mainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        mainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(_translate("mainWindow", "ZeuZ Framework - ASAPI GUI", None))
        self.label.setText(_translate("mainWindow", "Username", None))
        self.label_2.setText(_translate("mainWindow", "Password", None))
        self.label_6.setText(_translate("mainWindow", "Server port", None))
        self.label_5.setText(_translate("mainWindow", "Server address", None))
        self.firstNextBtn.setText(_translate("mainWindow", "Next", None))
        self.cancelBtn.setText(_translate("mainWindow", "Cancel", None))
        self.port.setText(_translate("mainWindow", "80", None))

