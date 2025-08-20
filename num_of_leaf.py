import cv2
import ctypes
from ctypes import *
import tensorflow as tf
import numpy as np

# os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
new_model = tf.keras.models.load_model('./model/unet.h5')


def kong(img, i, j):
    img[i - 4:i + 4, j - 4:j + 4] = 0
    # dep[i-2:i+2,j-2:j+2] = 0


def predict(rgb, dep):
    # print("semantic segmentation...")
    size = 512
    width, height = rgb.shape[1], rgb.shape[0]
    soil = []  # 存储土壤深度信息
    resized = cv2.resize(rgb, (size, size))
    copyed = resized.copy()
    resized = resized.reshape(1, size, size, 3)
    # a = tf.cast(a,tf.float16)
    resized = resized.astype(float)
    resized = resized / 255
    result = new_model.predict(resized)
    # result = np.array(result)
    result = result.reshape(size, size, 3)
    pix_num = 0
    for i in range(size):
        for j in range(size):
            # print(result[i,j])
            if result[i, j, 0] == 0:
                copyed[i, j] = 0
                pix_num += 1
    leaf_rate = (1 - pix_num / 262144) * 100
    copyed = cv2.resize(copyed, (width, height))
    for i in range(height):
        for j in range(width):
            if copyed[i, j, 0] == 0:
                if dep[i, j] != 0:
                    soil.append(dep[i, j])
                dep[i, j] = 0
    cv2.imwrite('cache/rgb.jpg', copyed)
    return copyed, dep, leaf_rate, np.mean(soil)


def caculate_num_and_area(rgb, dep, meank, thresh):  # a为俯视RGB  dep为俯视深度图
    img_aftersegmentation, dep, leaf_rate, soil_dep = predict(rgb, dep)
    img_copyed = img_aftersegmentation.copy()
    img, sum, area, txt_img, zhugao = \
        calculate_after_segmentation(img_aftersegmentation, dep, meank, thresh, soil_dep)
    return img, sum, area, txt_img, leaf_rate, img_copyed, zhugao


def calculate_after_segmentation(huabu, dep, meank, thresh, soil_dep):  # huabu为予以分割rgb  dep为对应深度图
    # huabu = cv2.imread('./seg.jpg')
    # dep = cv2.imread('./dep.png')
    # print(soil_dep)
    op_img = huabu.copy()
    img = huabu.copy()
    txt_img = huabu.copy()
    # huabu = cv2.cvtColor(huabu,cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (3, 3), 0)  # 用高斯平滑处理原图像降噪
    canny = cv2.Canny(img, 65, 183)  # 70.200
    # cv2.imshow('1',canny)
    # cv2.waitKey(0)
    # print(canny.shape)
    for i in range(huabu.shape[0]):
        for j in range(huabu.shape[1]):
            if (canny[i, j] == 255):
                kong(huabu, i, j)
    # cv2.imwrite('./rgb.jpg',op_img)
    cv2.imwrite('cache/dep.png', dep)
    huabu = cv2.cvtColor(huabu, cv2.COLOR_BGR2GRAY)
    dst = cv2.adaptiveThreshold(huabu, 210, cv2.BORDER_REPLICATE, cv2.THRESH_BINARY_INV, 3, 10)
    img_contours, contours, heridency = cv2.findContours(dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    list = []
    leaf_list = []
    sum = 0
    for num, contour in enumerate(contours):
        i = cv2.contourArea(contour)
        if i > 23:   # 23
            sum += 1
            # print(i)
            list.append(num)
            x, y, w, h = cv2.boundingRect(contour)
            row, col = int(y + h / 2), int(x + w / 2)  # float -> int
            if dep[row, col] != 0:
                leaf_list.append(dep[row, col])
                # print(dep[row, col])
            #     txt_img = cv2.putText(txt_img,'.'+str(num),(int(x+w/2),int(y+h/2)),
            #                           cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
            #     leaf_bounding_dict[num] = [x,y,w,h]
            # cv2.drawContours(op_img,contours,num,(0,255,255))

    cv2.imwrite('./cache/txt_img.jpg', txt_img)
    dll = ctypes.cdll.LoadLibrary('Dll/core.dll')
    dll.construct_pcd.restype = c_float
    area = dll.construct_pcd(meank, c_float(thresh), sum * 2, op_img.shape[0], op_img.shape[1],
                             op_img.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)))
    # print('-----------------------------Done-------------------------------')
    return op_img, sum, area, txt_img, [soil_dep - np.mean(leaf_list), soil_dep]
