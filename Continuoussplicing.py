import os


import argparse

import glob
# import the necessary packages
import numpy as np
import imutils
import cv2


class Stitcher:
    def __init__(self):
        # determine if we are using OpenCV v3.X
        self.isv3 = imutils.is_cv3()

    def stitch(self, images, ratio=2, reprojThresh=4.0,
        showMatches=False):
        # unpack the images, then detect keypoints and extract
        # local invariant descriptors from them
        (imageB, imageA) = images
        (kpsA, featuresA) = self.detectAndDescribe(imageA)
        (kpsB, featuresB) = self.detectAndDescribe(imageB)

        # match features between the two images
        M = self.matchKeypoints(kpsA, kpsB,
            featuresA, featuresB, ratio, reprojThresh)

        # if the match is None, then there aren't enough matched
        # keypoints to create a panorama
        if M is None:
            return None

        # otherwise, apply a perspective warp to stitch the images
        # together
        (matches, H, status) = M
        result = cv2.warpPerspective(imageA, H,
            (imageA.shape[1] + imageB.shape[1], imageA.shape[0]))
        result[0:imageB.shape[0], 0:imageB.shape[1]] = imageB

        # check to see if the keypoint matches should be visualized
        if showMatches:
            vis = self.drawMatches(imageA, imageB, kpsA, kpsB, matches,
                status)

            # return a tuple of the stitched image and the
            # visualization
            return (result, vis,H)

        # return the stitched image
        return result

    def detectAndDescribe(self, image):
        # convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # check to see if we are using OpenCV 3.X
        if self.isv3:
            # detect and extract features from the image
            descriptor = cv2.xfeatures2d.SIFT_create()
            (kps, features) = descriptor.detectAndCompute(image, None)

        # otherwise, we are using OpenCV 2.4.X
        else:
            # detect keypoints in the image
            detector = cv2.FeatureDetector_create("SIFT")
            kps = detector.detect(gray)

            # extract features from the image
            extractor = cv2.DescriptorExtractor_create("SIFT")
            (kps, features) = extractor.compute(gray, kps)

        # convert the keypoints from KeyPoint objects to NumPy
        # arrays
        kps = np.float32([kp.pt for kp in kps])

        # return a tuple of keypoints and features
        return (kps, features)

    def matchKeypoints(self, kpsA, kpsB, featuresA, featuresB,
        ratio, reprojThresh):
        # compute the raw matches and initialize the list of actual
        # matches
        matcher = cv2.DescriptorMatcher_create("BruteForce")
        rawMatches = matcher.knnMatch(featuresA, featuresB, 2)
        matches = []

        # loop over the raw matches
        for m in rawMatches:
            # ensure the distance is within a certain ratio of each
            # other (i.e. Lowe's ratio test)
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                matches.append((m[0].trainIdx, m[0].queryIdx))

        # computing a homography requires at least 4 matches
        if len(matches) > 4:
            # construct the two sets of points
            ptsA = np.float32([kpsA[i] for (_, i) in matches])
            ptsB = np.float32([kpsB[i] for (i, _) in matches])

            # compute the homography between the two sets of points
            (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC,
                reprojThresh)

            # return the matches along with the homograpy matrix
            # and status of each matched point
            return (matches, H, status)


        return None

    def drawMatches(self, imageA, imageB, kpsA, kpsB, matches, status):
        # initialize the output visualization image
        (hA, wA) = imageA.shape[:2]
        (hB, wB) = imageB.shape[:2]
        vis = np.zeros((max(hA, hB), wA + wB, 3), dtype="uint8")
        vis[0:hA, 0:wA] = imageA
        vis[0:hB, wA:] = imageB

        # loop over the matches
        for ((trainIdx, queryIdx), s) in zip(matches, status):

            if s == 1:
                # draw the match
                ptA = (int(kpsA[queryIdx][0]), int(kpsA[queryIdx][1]))
                ptB = (int(kpsB[trainIdx][0]) + wA, int(kpsB[trainIdx][1]))
                cv2.line(vis, ptA, ptB, (0, 255, 0), 1)

        # return the visualization
        return vis
def img_add(img1, img2):
    # print(img1.shape,img2.shape)
    img_new = np.ndarray([img1.shape[0], img1.shape[1] + img2.shape[1], 3],dtype=np.uint8)
    img_new[:, 0:img1.shape[1]] = img1
    img_new[:, img1.shape[1]:] = img2
    return np.array(img_new)
def dep_add(img1, img2):
    # print(img1.shape,img2.shape)
    img_new = np.ndarray([img1.shape[0], img1.shape[1] + img2.shape[1]],dtype=np.uint16)
    img_new[:, 0:img1.shape[1]] = img1
    img_new[:, img1.shape[1]:] = img2
    return np.array(img_new)

def continuous():

    img_list = []
    dep_list = []
    for img_name in glob.glob('./RGB/*.jpg'):
        img_list.append(img_name)
    for dep_img in glob.glob('./RGB/*.png'):
        dep_list.append(dep_img)
    img_list.sort(key=lambda x: int(x.split('.')[-2].split('\\')[-1]))
    dep_list.sort(key=lambda x: int(x.split('.')[-2].split('\\')[-1]))
    model = cv2.imread(img_list[0])
    model_d = cv2.imread(dep_list[0],-1)
    model_d = np.array(model_d,np.uint16)

    exist = model.copy()
    exist_d = model_d.copy()
    print(len(img_list))
    for img_num in range(1, len(img_list)):
        imageB = cv2.imread(img_list[img_num])
        depB = cv2.imread(dep_list[img_num],-1)

        stitcher = Stitcher()
        (result, vis, a2) = stitcher.stitch([model, imageB], showMatches=True)
        r = cv2.warpPerspective(imageB, a2,
                                ( imageB.shape[1] + model.shape[1] , imageB.shape[0]))

        r_d = cv2.warpPerspective(depB, a2,
                                ( depB.shape[1] + model_d.shape[1] , depB.shape[0]))

        col = min(np.argwhere(r[10] != 0)[-1][0],np.argwhere(r[-10] != 0)[-1][0])

        if img_num ==1:
            model_d = dep_add(exist_d, r_d[:, model_d.shape[1]: col])
            model = img_add(exist,r[:, model.shape[1]: col , :])
        else:
            model_d = dep_add(model_d, r_d[:, model_d.shape[1]: col])
            model = img_add(model, r[:, model.shape[1]:col, :])

    cv2.imwrite('rgb.jpg', model)
    cv2.imwrite('dep.png', model_d)
    print('拼接完成')
    return model

def read_frame():
    filepath = r'./'  # 视频所在文件夹
    pathDir = os.listdir(filepath)
    a = 1  # 图片计数
    for allDir in pathDir:
        videopath = r'./' + allDir


        if videopath.endswith('.mp4'):

            print(videopath)
            vc = cv2.VideoCapture(videopath)  # 读入视频文件
            c = 1

            if vc.isOpened():  # 判断是否正常打开
                rval, frame = vc.read()
            else:
                rval = False

            timeF = 80 # 视频帧计数间隔频率

            while rval:  # 循环读取视频帧
                rval, frame = vc.read()
                if (c % timeF == 0):  # 每隔timeF帧进行存储操作
                    cv2.imwrite(r'./RGB/' + str(a) + '.jpg', frame)  # 存储为图像
                    a = a + 1
                c = c + 1
                cv2.waitKey(1)
            vc.release()
        else:
            continue

if __name__ == '__main__':
    # read_frame()
    continuous()

