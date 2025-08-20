import cv2
import ctypes
from ctypes import *
import cv2
import numpy as np



class cal_dll(object):
    area = 0
    meank = 200
    thresh = 0.3
    cy_dep = 0

    def __init__(self, img, dep):
        super().__init__()
        self.dep = dep
        self.img = img
        self.ret = np.zeros(dtype=np.uint8, shape=(img.shape[0], img.shape[1], 3))
        self.dll = ctypes.cdll.LoadLibrary('Dll/core2.dll')
        self.dll.ret_area.restype = c_float
        self.dll.filter_water(img.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)),
                  dep.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)),
                  self.ret.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)),
                  img.shape[0],img.shape[1])


    def on_EVENT_LBUTTONDOWN(self,event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            xy = "%d,%d" % (x, y)
            self.dll.ret_area.restype = c_float
            area1 = self.dll.ret_area(int(x), int(y), self.meank, c_float(self.thresh), self.img.shape[0],self.img.shape[1])
            self.cy_dep = self.dep[y, x]
            self.area = area1

    # 点击回调
    def choose_point(self):


        cv2.namedWindow("select a point")
        cv2.setMouseCallback("select a point", self.on_EVENT_LBUTTONDOWN)
        cv2.imshow("select a point", self.ret)
        while (1):
            # cv2.imshow("select a point", self.ret)
            if (cv2.getWindowProperty('select a point', 0) == -1
                    or (cv2.waitKey(1) & 0xFF == 32)):
                break
            cv2.waitKey(1)
        cv2.destroyAllWindows()
#
# img = cv2.imread('rgb.jpg',-1)
# dep = cv2.imread('f-1.png',-1)
# a = cal_dll(img,dep)
# a.choose_point()
# print(a.area)
# if __name__ == '__main__':
#     rgb = cv2.imread('D:\PY code\Phenotype measurement system\cache\\rgb.jpg')
#     dep = cv2.imread('D:\PY code\Phenotype measurement system\cache\dep.png',-1)
#     rgb = cv2.resize(rgb,(1024,1024))
#     dep = cv2.resize(dep,(1024,1024))
#     a = cal_dll(rgb,dep)
#     a.choose_point()
#     print(a.area)