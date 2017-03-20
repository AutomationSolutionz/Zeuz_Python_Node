# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'branchGUI.ui'
#
# Created: Tue Sep  6 16:15:11 2016
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

class Ui_branchForm(object):
    def setupUi(self, branchForm):
        branchForm.setObjectName(_fromUtf8("branchForm"))
        branchForm.resize(698, 468)
        self.fourthBackBtn = QtGui.QPushButton(branchForm)
        self.fourthBackBtn.setGeometry(QtCore.QRect(430, 400, 98, 27))
        self.fourthBackBtn.setObjectName(_fromUtf8("fourthBackBtn"))
        self.FifthNextBtn = QtGui.QPushButton(branchForm)
        self.FifthNextBtn.setGeometry(QtCore.QRect(550, 400, 98, 27))
        self.FifthNextBtn.setStyleSheet(_fromUtf8("background: #4499aa; color: white"))
        self.FifthNextBtn.setObjectName(_fromUtf8("FifthNextBtn"))

        self.retranslateUi(branchForm)
        QtCore.QMetaObject.connectSlotsByName(branchForm)

    def retranslateUi(self, branchForm):
        branchForm.setWindowTitle(_translate("branchForm", "Form", None))
        self.fourthBackBtn.setText(_translate("branchForm", "Back", None))
        self.FifthNextBtn.setText(_translate("branchForm", "Connect", None))

