import sys
from main_ui import Ui_child
from PyQt5.QtCore import QThread,pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5 import QtGui,QtCore,QtWidgets
import numpy as np
import pyrealsense2 as rs
import cv2


'''
基于realsense的
实时拍照
并且拼接算法
'''
class realsense(QtWidgets.QMainWindow, Ui_child):
    num = 0
    def __init__(self):
        super(realsense, self).__init__()
        self.setupUi(self)
        self.timer = QtCore.QTimer()

        self.pushButton_startcam.clicked.connect(self.init_cam)
        # self.timer.timeout.connect(self.label_show)
        self.pushButton_frame.clicked.connect(self.frame)
        # self.pushButton.clicked.connect(self.pinjie)

    def pinjie(self):
        return 0
        # img = Continuoussplicing.continuous()
        #
        # img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        # img = cv2.resize(img,(1300,500))
        # pix = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888)
        # self.labelrgb_3.setPixmap(QtGui.QPixmap.fromImage(pix))

    def init_cam(self):
        self.pipeline = rs.pipeline()

        # Create a config and configure the pipeline to stream
        #  different resolutions of color and depth streams
        config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))

        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.timer.start(2)
        if device_product_line == 'L500':
            config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
        else:
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        # Start streaming
        profile = self.pipeline.start(config)

        # Getting the depth sensor's depth scale (see rs-align example for explanation)
        depth_sensor = profile.get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()
        print("Depth Scale is: ", depth_scale)

        # We will be removing the background of objects more than
        #  clipping_distance_in_meters meters away
        clipping_distance_in_meters = 1  # 1 meter
        clipping_distance = clipping_distance_in_meters / depth_scale

        # Create an align object
        # rs.align allows us to perform alignment of depth frames to others frames
        # The "align_to" is the stream type to which we plan to align depth frames.
        align_to = rs.stream.color
        self.align = rs.align(align_to)

    def frame(self):
        cv2.imwrite('RGB/'+str(self.num)+'.jpg',self.imgrgb)
        cv2.imwrite('RGB/'+str(self.num) + '.png',self.imgdep)
        self.num += 1
    def label_show(self):
        frames = self.pipeline.wait_for_frames()
        # frames.get_depth_frame() is a 640x360 depth image

        # Align the depth frame to color frame
        aligned_frames = self.align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        # Validate that both frames are valid

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Remove background - Set pixels further than clipping_distance to grey
        grey_color = 153
        # depth_image_3d = np.dstack(
        #     (depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
        # bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)

        # Render images:
        #   depth align to color on left
        #   depth on right
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        # images = np.hstack((bg_removed, depth_colormap))
        self.imgrgb = color_image
        self.imgdep = depth_image
        # cv2.namedWindow('Align Example', cv2.WINDOW_NORMAL)

        # cv2.imshow('Align Example', color_image)
        color_image = cv2.cvtColor(color_image,cv2.COLOR_BGR2RGB)
        dep = cv2.resize(depth_colormap,(480,270))
        self.rgb = cv2.resize(color_image,(480,270))
        pix = QtGui.QImage(self.rgb.data, self.rgb.shape[1], self.rgb.shape[0], QtGui.QImage.Format_RGB888)
        self.labelrgb.setPixmap(QtGui.QPixmap.fromImage(pix))

        dep_pix = QtGui.QImage(dep.data, dep.shape[1], dep.shape[0], QtGui.QImage.Format_RGB888)
        self.labelrgb_2.setPixmap(QtGui.QPixmap.fromImage(dep_pix))
    def SHOW(self):
        self.show()
# if __name__ == '__main__':
#     app = QtWidgets.QApplication(sys.argv)
#     mainwindow = realsense()
#     mainwindow.show()
#     exit(app.exec_())