# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'userGUI.ui'
#
# Created: Wed Aug 31 15:26:27 2016
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

class Ui_userForm(object):
    def setupUi(self, userForm):
        userForm.setObjectName(_fromUtf8("userForm"))
        userForm.resize(696, 438)
        self.username = QtGui.QLineEdit(userForm)
        self.username.setGeometry(QtCore.QRect(290, 66, 211, 27))
        self.username.setObjectName(_fromUtf8("username"))
        self.password = QtGui.QLineEdit(userForm)
        self.password.setGeometry(QtCore.QRect(290, 116, 211, 31))
        self.password.setText(_fromUtf8(""))
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        self.password.setObjectName(_fromUtf8("password"))
        self.server = QtGui.QLineEdit(userForm)
        self.server.setGeometry(QtCore.QRect(290, 206, 351, 27))
        self.server.setObjectName(_fromUtf8("server"))
        self.port = QtGui.QLineEdit(userForm)
        self.port.setGeometry(QtCore.QRect(290, 266, 211, 27))
        self.port.setObjectName(_fromUtf8("port"))
        self.label_5 = QtGui.QLabel(userForm)
        self.label_5.setGeometry(QtCore.QRect(150, 210, 111, 17))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.line_2 = QtGui.QFrame(userForm)
        self.line_2.setGeometry(QtCore.QRect(80, 170, 571, 16))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.cancelBtn = QtGui.QPushButton(userForm)
        self.cancelBtn.setGeometry(QtCore.QRect(400, 360, 98, 27))
        self.cancelBtn.setObjectName(_fromUtf8("cancelBtn"))
        self.label = QtGui.QLabel(userForm)
        self.label.setGeometry(QtCore.QRect(150, 70, 71, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_6 = QtGui.QLabel(userForm)
        self.label_6.setGeometry(QtCore.QRect(150, 270, 91, 17))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.firstNextBtn = QtGui.QPushButton(userForm)
        self.firstNextBtn.setGeometry(QtCore.QRect(520, 360, 98, 27))
        self.firstNextBtn.setStyleSheet(_fromUtf8("background: #4499aa; color: white"))
        self.firstNextBtn.setObjectName(_fromUtf8("firstNextBtn"))
        self.label_2 = QtGui.QLabel(userForm)
        self.label_2.setGeometry(QtCore.QRect(150, 120, 66, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))

        self.retranslateUi(userForm)
        QtCore.QMetaObject.connectSlotsByName(userForm)

    def retranslateUi(self, userForm):
        userForm.setWindowTitle(_translate("userForm", "Form", None))
        self.label_5.setText(_translate("userForm", "Server address", None))
        self.cancelBtn.setText(_translate("userForm", "Cancel", None))
        self.label.setText(_translate("userForm", "Username", None))
        self.label_6.setText(_translate("userForm", "Server port", None))
        self.firstNextBtn.setText(_translate("userForm", "Next", None))
        self.port.setText(_translate("userForm", "80", None))
        self.label_2.setText(_translate("userForm", "Password", None))

