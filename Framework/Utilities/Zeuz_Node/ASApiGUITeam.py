# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'teamGUI.ui'
#
# Created: Mon Aug 29 16:40:35 2016
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

class Ui_teamForm(object):
    def setupUi(self, teamForm):
        teamForm.setObjectName(_fromUtf8("teamForm"))
        teamForm.resize(584, 356)
        self.SecondNextBtn = QtGui.QPushButton(teamForm)
        self.SecondNextBtn.setGeometry(QtCore.QRect(420, 300, 98, 27))
        self.SecondNextBtn.setStyleSheet(_fromUtf8("background: #4499aa; color: white"))
        self.SecondNextBtn.setObjectName(_fromUtf8("SecondNextBtn"))
        self.firstBackBtn = QtGui.QPushButton(teamForm)
        self.firstBackBtn.setGeometry(QtCore.QRect(300, 300, 98, 27))
        self.firstBackBtn.setObjectName(_fromUtf8("firstBackBtn"))
        self.label = QtGui.QLabel(teamForm)
        self.label.setGeometry(QtCore.QRect(40, 130, 141, 20))
        self.label.setObjectName(_fromUtf8("label"))
        self.listView = QtGui.QListView(teamForm)
        self.listView.setGeometry(QtCore.QRect(220, 20, 301, 251))
        self.listView.setObjectName(_fromUtf8("listView"))

        self.retranslateUi(teamForm)
        QtCore.QMetaObject.connectSlotsByName(teamForm)

    def retranslateUi(self, teamForm):
        teamForm.setWindowTitle(_translate("teamForm", "Form", None))
        self.SecondNextBtn.setText(_translate("teamForm", "Next", None))
        self.firstBackBtn.setText(_translate("teamForm", "Back", None))
        self.label.setText(_translate("teamForm", "Select a team", None))

