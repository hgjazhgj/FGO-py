import cv2
import os
import numpy as np

img = cv2.imread("traitlist.png")
alpha = np.sum(img, axis=-1) > 0
mask  = np.dstack((alpha,alpha,alpha))
img*=mask
alpha = np.uint8(alpha * 255)
img = np.dstack((img, alpha))
cv2.imwrite("traitlist.new.png",img)