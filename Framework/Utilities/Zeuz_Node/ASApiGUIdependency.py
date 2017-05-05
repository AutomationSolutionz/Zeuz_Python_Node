# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dependencyGUI.ui'
#
# Created: Tue Sep  6 11:44:18 2016
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


class Ui_dependencyForm(object):
    def setupUi(self, dependencyForm):
        dependencyForm.setObjectName(_fromUtf8("dependencyForm"))
        dependencyForm.resize(702, 471)
        self.FourthNextBtn = QtGui.QPushButton(dependencyForm)
        self.FourthNextBtn.setGeometry(QtCore.QRect(560, 410, 98, 27))
        self.FourthNextBtn.setStyleSheet(_fromUtf8("background: #4499aa; color: white"))
        self.FourthNextBtn.setObjectName(_fromUtf8("FourthNextBtn"))
        self.thirdBackBtn = QtGui.QPushButton(dependencyForm)
        self.thirdBackBtn.setGeometry(QtCore.QRect(440, 410, 98, 27))
        self.thirdBackBtn.setObjectName(_fromUtf8("thirdBackBtn"))

        self.retranslateUi(dependencyForm)
        QtCore.QMetaObject.connectSlotsByName(dependencyForm)

    def retranslateUi(self, dependencyForm):
        dependencyForm.setWindowTitle(_translate("dependencyForm", "Form", None))
        self.FourthNextBtn.setText(_translate("dependencyForm", "Next", None))
        self.thirdBackBtn.setText(_translate("dependencyForm", "Back", None))

