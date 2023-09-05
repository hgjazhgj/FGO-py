import cv2
import os
import numpy as np

os.chdir("FGO-py")
IMG=type('IMG',(),{i[:-4].upper():(lambda x:(x[...,:3],x[...,3]))(cv2.imread(f'fgoImage/{i}',cv2.IMREAD_UNCHANGED))for i in os.listdir('fgoImage')if i.endswith('.png')})
CLASS={100:[(lambda x:(x[...,:3],x[...,3]))(cv2.imread(f'fgoImage/class/{i}{j}.png',cv2.IMREAD_UNCHANGED))for i in['shielder','saber','archer','lancer','rider','caster','assassin','berserker']for j in range(1,2)]}
for scale in [75,87,93,125]:CLASS[scale]=[[cv2.resize(j,(0,0),fx=scale/100,fy=scale/100,interpolation=cv2.INTER_CUBIC)for j in i]for i in CLASS[100]]
os.chdir("..")

class Dectect:
    def __init__(self,im) -> None:
        self.im = im
    def crop(self,rect):
        # cv2.imwrite(time.strftime(f'fgoTemp/Crop_%Y-%m-%d_%H.%M.%S_{rect}.png',time.localtime(self.time)),self.im[rect[1]+2:rect[3]-2,rect[0]+2:rect[2]-2],[cv2.IMWRITE_PNG_COMPRESSION,9])
        return self.im[rect[1]:rect[3],rect[0]:rect[2]]
    def loc(self,img,rect=(0,0,1280,720)):return cv2.minMaxLoc(cv2.matchTemplate(self.crop(rect),img[0],cv2.TM_SQDIFF_NORMED,mask=img[1]))
    def compare(self,img,rect=(0,0,1280,720),threshold=.05):return threshold>self.loc(img,rect)[0]
    def select(self,img,rect=(0,0,1280,720),threshold=.2):return(lambda x:np.argmin(x)if threshold>min(x)else None)([self.loc(i,rect)[0]for i in img])
    def test(self):return not None in [(lambda x:x if x is None else divmod(x,3))(self.select(CLASS[87],(58,93,595,165),threshold=.4))for i in range(6)]

target = cv2.imread("FGO-py/Screenshot_2023-09-03_06.44.59.106.png")
area = (58,93,595,165)
detect_obj = IMG.BATTLECONTINUE
detect = Dectect(target)
result_t = detect.loc(detect_obj)
# target = detect.crop(area)
print("target.shape: ",target.shape)
# print(detect.test())
print(result_t)
detected_img = cv2.circle(target,result_t[2],5, (0,255,0), -1)
# # # next_shape = detect_obj[1].shape
# # # detected_img = cv2.circle(target,(144+round(next_shape[0]/2), 309+round(next_shape[1]+30)),5, (0,0,255), -1)
cv2.imwrite("detected_img.png",detected_img)
# print(IMG.NEXT[1].shape)
