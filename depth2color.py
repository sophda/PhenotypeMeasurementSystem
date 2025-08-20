import cv2
import os.path
import glob
import numpy as np
from PIL import Image


pngfile = 'd:/1/c/1.png'
# READ THE DEPTH
im_depth = cv2.imread(pngfile,-1)
# apply colormap on deoth image(image must be converted to 8-bit per pixel first)
m = 0.1
while 1:
    im_color = cv2.applyColorMap(cv2.convertScaleAbs(im_depth, alpha=m), cv2.COLORMAP_JET)
    # convert to mat png
    m += 0.3
    print(m)
    cv2.imshow('',im_color)
    if cv2.waitKey(20)==27:
        cv2.imwrite('dep2c.jpg', im_color)
        break



