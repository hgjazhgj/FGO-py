import cv2
import os
import numpy as np

img = cv2.imread("skillpos.png")
upper_left = (35+318*2+88*0,598)#(1120,0)
lowwer_down = (55+318*2+88*0,618)#(1280,75)
cropped_img = img[upper_left[1]:lowwer_down[1],upper_left[0]:lowwer_down[0]]
cv2.imwrite("still.png",cropped_img)