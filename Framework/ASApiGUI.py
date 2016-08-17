'''
Created on August 17, 2016

@author: minar
'''

import sys
from PyQt4 import QtGui
from Utilities import ASApiGUIdesign


class GUIApp(QtGui.QMainWindow, ASApiGUIdesign.Ui_mainWindow):
    def __init__(self, parent=None):
        super(GUIApp, self).__init__(parent)
        self.setupUi(self)

def window():
    app = QtGui.QApplication(sys.argv)
    w = QtGui.QWidget()
    b = QtGui.QLabel(w)
    b.setText("Welcome to ZeuZ Framework!")
    w.setGeometry(300, 300, 600, 150)
    b.move(50, 20)
    w.setWindowTitle("PyQT")
    w.show()
    sys.exit(app.exec_())


def main():
    # window()
    app = QtGui.QApplication(sys.argv)
    form = GUIApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()