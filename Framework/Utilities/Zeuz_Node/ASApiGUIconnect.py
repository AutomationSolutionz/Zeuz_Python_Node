# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'connectGUI.ui'
#
# Created: Tue Sep  6 16:15:24 2016
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

class Ui_connectForm(object):
    def setupUi(self, connectForm):
        connectForm.setObjectName(_fromUtf8("connectForm"))
        connectForm.resize(697, 456)
        self.fifthBackBtn = QtGui.QPushButton(connectForm)
        self.fifthBackBtn.setGeometry(QtCore.QRect(430, 390, 98, 27))
        self.fifthBackBtn.setObjectName(_fromUtf8("fifthBackBtn"))
        self.closeBtn = QtGui.QPushButton(connectForm)
        self.closeBtn.setGeometry(QtCore.QRect(560, 390, 98, 27))
        self.closeBtn.setObjectName(_fromUtf8("closeBtn"))
        self.label = QtGui.QLabel(connectForm)
        self.label.setGeometry(QtCore.QRect(140, 90, 111, 21))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(connectForm)
        QtCore.QMetaObject.connectSlotsByName(connectForm)

    def retranslateUi(self, connectForm):
        connectForm.setWindowTitle(_translate("connectForm", "Form", None))
        self.fifthBackBtn.setText(_translate("connectForm", "Back", None))
        self.closeBtn.setText(_translate("connectForm", "Close", None))
        self.label.setText(_translate("connectForm", "Running...", None))

