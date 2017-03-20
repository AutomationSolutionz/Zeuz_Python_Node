# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'projectGUI.ui'
#
# Created: Mon Aug 29 16:40:48 2016
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

class Ui_projectForm(object):
    def setupUi(self, projectForm):
        projectForm.setObjectName(_fromUtf8("projectForm"))
        projectForm.resize(584, 356)
        self.secondBackBtn = QtGui.QPushButton(projectForm)
        self.secondBackBtn.setGeometry(QtCore.QRect(300, 300, 98, 27))
        self.secondBackBtn.setObjectName(_fromUtf8("secondBackBtn"))
        self.label = QtGui.QLabel(projectForm)
        self.label.setGeometry(QtCore.QRect(40, 130, 141, 20))
        self.label.setObjectName(_fromUtf8("label"))
        self.ThirdNextBtn = QtGui.QPushButton(projectForm)
        self.ThirdNextBtn.setGeometry(QtCore.QRect(420, 300, 98, 27))
        self.ThirdNextBtn.setStyleSheet(_fromUtf8("background: #4499aa; color: white"))
        self.ThirdNextBtn.setObjectName(_fromUtf8("ThirdNextBtn"))
        self.listView = QtGui.QListView(projectForm)
        self.listView.setGeometry(QtCore.QRect(220, 20, 301, 251))
        self.listView.setObjectName(_fromUtf8("listView"))

        self.retranslateUi(projectForm)
        QtCore.QMetaObject.connectSlotsByName(projectForm)

    def retranslateUi(self, projectForm):
        projectForm.setWindowTitle(_translate("projectForm", "Form", None))
        self.secondBackBtn.setText(_translate("projectForm", "Back", None))
        self.label.setText(_translate("projectForm", "Select a project", None))
        self.ThirdNextBtn.setText(_translate("projectForm", "Next", None))

