import sys

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from zhichi import Ui_MainWindow

class menu_zhichi(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(menu_zhichi, self).__init__()
        self.setupUi(self)
        self.pushButton_frame.clicked.connect(self.cv)
    def cv(self):
        import cv2
    def SHOW(self):
        self.show()
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mianwindow = menu_zhichi()
    mianwindow.show()
    exit(app.exec_())

