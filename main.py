import ctypes
import os
import time
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets

# from main_realsense import realsense
from system_his import Ui_MainWindow
from menu.zhichi_m import menu_zhichi
# from menu.main_realsense import realsense
import sys
import cv2


class main(QtWidgets.QMainWindow, Ui_MainWindow):
    id = 0
    history_5 = []
    soil_dep = 0.0
    root_length_list = []


    def __init__(self):
        super(main, self).__init__()
        self.setupUi(self)
        self.csize = 420
        self.setFixedSize(1920, 1080)
        self.showMaximized()
        self.init()

    def __del__(self):
        # os.remove('cache/out.jpg')
        # os.remove('cache/leaf.pcd')
        # os.remove('cache/leaf_one.pcd')
        # os.remove('cache/pers.jpg')
        # os.remove('cache/wei.jpg')
        '''
        初始化
        关联信号与槽
        '''

    def init(self):
        self.c21_thread = process_all()  # 初始化进程
        self.c21_thread.yepianshu.connect(self.yepianshu)
        self.c21_thread.yemianji.connect(self.yemianji)
        self.c21_thread.leaf_rate.connect(self.zhishu)
        # self.c2_thread.erzu.connect(self.jindu2)

        self.c21_thread.guanceng.connect(self.guanceng)
        self.c21_thread.jingcu.connect(self.jingcu)
        self.c21_thread.jindu.connect(self.progressBar_show)
        self.c21_thread.his.connect(self.set_history)
        # self.c1_thread.yizu.connect(self.jindu2)
        self.c21_thread.zhugao.connect(self.zhugao)
        self.c21_thread.length_list.connect(self.length_list)


        self.c3_thread = process_onearea()
        self.c3_thread.one_area.connect(self.onearea)
        self.c3_thread.cy_dep.connect(self.cy_dep)

        # self.show_thread = process_showcloud()

        # self.process_plt_thread = process_plt()

        # self.pushButton_11.clicked.connect(self.showplt)

        self.pushButton_8.clicked.connect(self.xuandian)

        self.pushButton_2.clicked.connect(self.openfile_rgb2)

        self.pushButton_3.clicked.connect(self.openfile_dep2)

        self.pushButton_4.clicked.connect(self.openfile_rgb1)

        self.pushButton_5.clicked.connect(self.openfile_dep1)

        self.pushButton_6.clicked.connect(self.show_history)

        self.pushButton.clicked.connect(self.calculate)

        self.pushButton_7.clicked.connect(self.showcloud)

        self.radioButton.toggled.connect(self.set_id)

    '''
    具体槽函数
    开启进程
    '''
    # def showplt(self):
    #     self.process_plt_thread.set_input(self.root_length_list)
    #     self.process_plt_thread.start()
    def show_history(self):
        if (os.path.exists("history.xls")):
            os.remove("history.xls")
        history = np.array(self.history_5)
        import xlwt
        book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        sheet = book.add_sheet(str(time.strftime("%Y.%m.%d ", time.localtime())), cell_overwrite_ok=True)
        sheet.write(0, 0, '组别')
        sheet.write(0, 1, '叶片数')
        sheet.write(0, 2, '叶片面积')
        sheet.write(0, 3, '叶面积指数')
        sheet.write(0, 4, '茎粗')
        sheet.write(0, 5, '冠层高')
        sheet.write(0, 6, '抽样面积')
        for i in range(history.shape[0]):
            for j in range(history.shape[1]):
                sheet.write(i + 1, 0, i + 1)
                sheet.write(i + 1, 1, history[i, 0])
                sheet.write(i + 1, 2, history[i, 1])
                sheet.write(i + 1, 3, history[i, 2])
                sheet.write(i + 1, 4, history[i, 3])
                sheet.write(i + 1, 5, history[i, 4])
                sheet.write(i + 1, 6, history[i, 5])
                # if (history[i].shape[0] ) > 6:
                #     for m in range(6,history[i].shape[0]):
                #         sheet.write(i + 1, m, history[i,m])
                # elif(history[i].shape[0]==6):
                #     sheet.write(i + 1, 6, history[i,5])
                # elif(history[i].shape[0]==5):
                #     sheet.write(i + 1, 6, 0)
        book.save("history.xls")
        os.startfile("history.xls")

    def set_history(self, list):
        self.history_5.append(list)

    def xuandian(self):
        deps = self.lineEdit_2.text()
        self.c3_thread.set_input(deps)
        self.c3_thread.start()

    def calculate(self):
        self.textBrowser.setText('')
        self.textBrowser_2.setText('')
        self.textBrowser_3.setText('')
        self.textBrowser_4.setText('')
        self.textBrowser_5.setText('')
        self.textBrowser_6.setText('')
        self.textBrowser_cyzg.setText('')
        self.textBrowser_zg.setText('')

        str_rgb2 = self.lineEdit.text()
        str_dep2 = self.lineEdit_2.text()
        str_rgb1 = self.lineEdit_3.text()
        str_dep1 = self.lineEdit_4.text()

        '''
        开 线程
        '''
        self.c21_thread.set_input(str_rgb2, str_dep2, str_rgb1, str_dep1)
        self.c21_thread.start()

    def set_id(self):
        if self.radioButton.isChecked():
            self.id = 1
        else:
            self.id = 0

    def showcloud(self):
        if self.id == 0:  # group
            self.webwidget.load(QUrl("http://localhost:63342/Phenotype%20measurement%20system/group.html?_ijt=l4kr7m5q596spinj11n422ft0s"))
        else:  # single
            self.webwidget.load(QUrl("http://localhost:63342/Phenotype%20measurement%20system/single.html?_ijt=bc6t5g8kptb5osmc3ri1ejv007"))
        # self.show_thread.set_input(self.id)
        # self.show_thread.start()

    '''
    主进程中的方法
    在UI中显示
    '''

    def length_list(self,value):
        self.root_length_list.extend(value)

    def cy_dep(self, value):
        self.textBrowser_cyzg.setText(str(self.soil_dep - value))

    def zhugao(self, value):
        self.textBrowser_zg.setText(str(value[0]))
        self.soil_dep = value[1]


    def progressBar_show(self, value):
        self.progressBar.setValue(value)

    def zhishu(self, value):
        self.textBrowser_6.setText(str(value))

    def onearea(self, value):
        self.textBrowser_5.setText(str(value))

        # self.history_5[len(self.history_5)-1].append(value)

        self.history_5[len(self.history_5) - 1][-1] = value

    def yepianshu(self, value):
        self.textBrowser.setText(str(value))

    def yemianji(self, value):
        self.textBrowser_2.setText(str(value))

    def jingcu(self, value):
        self.textBrowser_3.setText(str(value))

    def guanceng(self, value):
        self.textBrowser_4.setText(str(value))

    def openfile_dep2(self):
        openfile_name, _ = QFileDialog.getOpenFileName(self, '选择图片', '', 'Image File(*.png)')
        self.lineEdit_2.setText(str(openfile_name))

    def openfile_rgb2(self):
        openfile_name, _ = QFileDialog.getOpenFileName(self, '选择图片', '', 'Image File(*.jpeg)')
        self.lineEdit.setText(str(openfile_name))
        jpg = QtGui.QPixmap(openfile_name).scaled(self.csize, self.csize)
        self.label_6.setPixmap(jpg)
        if (self.checkBox_2.isChecked()):
            str_dep2 = openfile_name.replace('jpeg', 'png')
            self.lineEdit_2.setText(str_dep2)

        '''
        初始化
        '''
        self.textBrowser.setText('')
        self.textBrowser_2.setText('')
        self.textBrowser_3.setText('')
        self.textBrowser_4.setText('')
        self.textBrowser_5.setText('')
        self.textBrowser_6.setText('')
        self.textBrowser_cyzg.setText('')
        self.textBrowser_zg.setText('')

    def openfile_rgb1(self):
        openfile_name, _ = QFileDialog.getOpenFileName(self, '选择图片', '', 'Image File(*.jpeg)')
        self.lineEdit_3.setText(str(openfile_name))
        jpg = QtGui.QPixmap(openfile_name).scaled(self.csize, self.csize)
        self.label_7.setPixmap(jpg)
        if (self.checkBox_2.isChecked()):
            str_dep1 = openfile_name.replace('jpeg', 'png')
            self.lineEdit_4.setText(str_dep1)

    def openfile_dep1(self):
        openfile_name, _ = QFileDialog.getOpenFileName(self, '选择图片', '', 'Image File(*.png)')
        self.lineEdit_4.setText(str(openfile_name))


class process_all(QThread):
    jingcu = pyqtSignal(float)
    guanceng = pyqtSignal(float)
    yepianshu = pyqtSignal(int)
    yemianji = pyqtSignal(float)
    leaf_rate = pyqtSignal(float)
    his = pyqtSignal(list)
    jindu = pyqtSignal(int)
    zhugao = pyqtSignal(list)
    length_list = pyqtSignal(list)

    def __init__(self):
        super(process_all, self).__init__()

    def set_input(self, str3, str4, str1, str2):
        self.str_rgb2 = str3
        self.str_dep2 = str4
        self.str_rgb1 = str1
        self.str_dep1 = str2

    def run(self):

        self.jindu.emit(20)
        import length_of_root
        import num_of_leaf
        self.jindu.emit(30)

        once = []
        if self.str_rgb2 != '':
            meank = 70  # 设置在进行统计时考虑查询点临近点数
            thresh = 0.5  # 设置判断是否为离群点的阀值
            rgb2 = cv2.imread(self.str_rgb2)  # 俯视RGB
            dep2 = cv2.imread(self.str_dep2, -1)  # 俯视深度图
            img, sum, area, txt_img, leaf_rate, img_afterseg, zhugao = \
                num_of_leaf.caculate_num_and_area(rgb2, dep2, meank, thresh)

        else:
            sum = 0
            area = 0
        self.yepianshu.emit(sum)
        once.append(sum)
        self.yemianji.emit(area)
        once.append(area)
        self.leaf_rate.emit(leaf_rate)
        once.append(leaf_rate)
        self.jindu.emit(60)
        if self.str_rgb1 != '':
            rgb1 = cv2.imread(self.str_rgb1, -1)  # 平视RGB
            dep1 = cv2.imread(self.str_dep1, -1)  # 平视深度图
            root, jingcu, guanceng, length_list = length_of_root.calculate_length_of_root(rgb1, dep1)
        else:
            jingcu = 0
            guanceng = 0
            length_list = []
        self.jingcu.emit(jingcu)
        once.append(jingcu)
        self.guanceng.emit(guanceng)
        once.append(guanceng)
        once.append(0)
        self.jindu.emit(100)
        self.his.emit(once)
        self.zhugao.emit(zhugao)
        self.length_list.emit(length_list)


class process_onearea(QThread):
    one_area = pyqtSignal(float)
    cy_dep = pyqtSignal(int)

    def __int__(self):
        super(process_onearea, self).__int__()

    def set_input(self, deps):  # img是保存后的语义分割图  dep则是原图
        img_seged = cv2.imread('cache/rgb.jpg')
        dep = cv2.imread(str(deps), -1)
        # print(img_seged)
        self.img = img_seged
        self.dep = dep

    def run(self):
        import true_area
        self.dll = true_area.cal_dll(self.img, self.dep)
        self.dll.choose_point()
        self.one_area.emit(self.dll.area)
        self.cy_dep.emit(self.dll.cy_dep)


class process_showcloud(QThread):
    def __int__(self, id):
        super(process_showcloud, self).__int__()

    def set_input(self, id):
        self.id = id

    def run(self):
        dll = ctypes.cdll.LoadLibrary('Dll/core3s.dll')
        dll.show(self.id)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mianwindow = main()
    mianwindow.show()
    zhichi = menu_zhichi()
    mianwindow.actionAppreciate_us.triggered.connect(zhichi.SHOW)

    # realsense = main_realsense()
    # mianwindow.actionc.triggered.connect(zhichi.SHOW)

    exit(app.exec_())
