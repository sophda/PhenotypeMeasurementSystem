import cv2
import tensorflow as tf
import numpy as np
import os
# os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
deeplab_model = tf.keras.models.load_model("./model/deeplabv3q.h5")
def transform(resized_img, predicted_img):
    predict = np.zeros((predicted_img.shape[0], predicted_img.shape[1]), np.uint8)
    img_leaf_oneclass = np.zeros((predicted_img.shape[0], predicted_img.shape[1], 3), np.uint8)
    img_gen_twoclass = np.zeros((predicted_img.shape[0], predicted_img.shape[1], 3), np.uint8)
    for i in range(predicted_img.shape[0]):
        for j in range(predicted_img.shape[1]):
            predict[i][j] = 100 * np.argmax(predicted_img[i][j])
    for i in range(resized_img.shape[0]):
        for j in range(resized_img.shape[1]):
            if (predict[i, j] == 100):  # one class --leaf
                img_leaf_oneclass[i, j] = resized_img[i, j]
            if (predict[i, j] == 200):  # two class -- gen
                img_gen_twoclass[i, j] = resized_img[i, j]
    cv2.imwrite('./predict.jpg', predict)
    return predict, img_leaf_oneclass, img_gen_twoclass


def predict(rgb):
    width, height = rgb.shape[1], rgb.shape[0]
    size = 512
    a = cv2.resize(rgb, (size, size))
    # b = a.copy()
    a = a.reshape(1, size, size, 3)
    # a = tf.cast(a,tf.float16)
    a = a.astype(float)
    a = a / 255
    result = deeplab_model.predict(a)
    # result = cv2.resize(result,(256,256))
    print(result.shape)
    result = result.reshape(size, size, 3)  # 去掉BATCH_SIZE 维度
    # b = cv2.resize(rgb,(width,height))
    result = cv2.resize(result,(width,height))
    predicted, leaf, gen = transform(rgb, result)
    return predicted, leaf, gen


def calculate_length_of_root(rgb, dep):
    # gen = np.zeros((512,512),np.uint8)
    predicted, leaf, gen = predict(rgb)
    # gen[:,:]  = 200*(predicted[:,:] == 200).astype(int)
    # cv2.imwrite('./gen.jpg',gen)
    gen = cv2.resize(gen, (dep.shape[1], dep.shape[0]))
    leaf = cv2.resize(leaf, (dep.shape[1], dep.shape[0]))
    img = gen.copy()

    huabu = cv2.cvtColor(gen, cv2.COLOR_BGR2GRAY)
    dst = cv2.Canny(huabu, 50, 200)
    # dst = cv2.threshold(huabu,10,255,cv2.THRESH_BINARY)
    img_contours, contours, heridency = cv2.findContours(dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.imshow('',dst)
    # print(dst.shape)
    id_list = []
    length_lsit = []
    allnum = 0
    whole_length_root = 0
    for num, contour in enumerate(contours):

        ranctangle = cv2.boundingRect(contour)
        # print('Root Bounding box：', ranctangle)
        single_img = img[ranctangle[1]:ranctangle[1] + ranctangle[3],
                     ranctangle[0]:ranctangle[0] + ranctangle[2]]
        cv2.rectangle(img, (ranctangle[0], ranctangle[1]),
                      (ranctangle[0] + ranctangle[2], ranctangle[1] + ranctangle[3]),
                      (0, 255, 0), 2)
        single_img = cv2.resize(single_img, (ranctangle[2], ranctangle[3]))
        ranctangle = cv2.minAreaRect(contour)
        # print("Root pix width：", ranctangle[1][0], "Root pix height：", ranctangle[1][1])
        #cv2.drawContours(img, contours, -1, (0, 0, 255), 3)
        #
        # cv2.imshow('mat2', single_img)
        # cv2.imshow('gen', img)
        # print('Coordinates of center point of minimum bounding box：', ranctangle[0])
        # import matplotlib.pyplot as plt # plt 用于显示图片
        # plt.imshow(img)
        # plt.show()
        a = int(ranctangle[0][0])
        b = int(ranctangle[0][1])
        # m = 0.236291 * (dep[a, b] / 77.86361 - 1) * min(ranctangle[1][0],ranctangle[1][1])
        m = min(ranctangle[1][0],ranctangle[1][1]) * dep[a,b] / 979.8
        if m>0:
            allnum += 1
            whole_length_root = whole_length_root + m

            id_list.append(allnum)
            length_lsit.append(m)
        # print(m)
    # print('Depth value of corresponding point：', dep[a, b])
    # plt.plot(id_list, length_lsit, 'ro-', color='blue')
    #
    # plt.savefig('testblueline.jpg')
    #
    # plt.cla()
    # print('True length of root:', whole_length_root / allnum, 'mm')
    # cv2.waitKey(0)
    cv2.imwrite('gen.jpg',img)
    gray_leaf = cv2.cvtColor(leaf, cv2.COLOR_BGR2GRAY)
    ret,binary_leaf = cv2.threshold(gray_leaf,10,255,cv2.THRESH_BINARY)
    # binary_leaf = cv2.Canny(gray_leaf, 50, 200)
    # binary_leaf = cv2.adaptiveThreshold(gray_leaf, 210, cv2.BORDER_REPLICATE, cv2.THRESH_BINARY_INV, 3, 10)
    # cv2.imwrite('binary leaf.jpg',binary_leaf)
    leaf_img, leaf_contours, hierarchy = cv2.findContours(binary_leaf,
                                                          cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    leaf_list = []
    for leaf_contour in leaf_contours:
        leaf_2d_area = cv2.contourArea(leaf_contour)
        leaf_list.append(leaf_2d_area)
    leaf_id = leaf_list.index(max(leaf_list))
    leaf_ranctangle = cv2.boundingRect(leaf_contours[leaf_id])
    for m in range(gray_leaf.shape[0]):
        for n in range(gray_leaf.shape[1]):
            if (gray_leaf[m, n] != 0) and (dep[m, n] != 0):
                leaf_x = m
                leaf_y = n
                break
    # print('Leaf Bounding box：', leaf_ranctangle)
    leaf_height = leaf_ranctangle[3]
    # true_leaf_height = 0.0623 * (dep[leaf_x, leaf_y] / 26.36 - 1) * leaf_height
    # true_leaf_height = 0.236291 * (dep[leaf_x, leaf_y] / 77.86361 - 1) * leaf_height
    true_leaf_height = leaf_height * dep[leaf_x, leaf_y] / 979.8
    jingcu = whole_length_root / allnum
    return img, jingcu, true_leaf_height, length_lsit

