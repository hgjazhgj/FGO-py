import cv2
import os
import numpy as np

os.chdir("FGO-py")
IMG=type('IMG',(),{i[:-4].upper():(lambda x:(x[...,:3],x[...,3]))(cv2.imread(f'fgoImage/{i}',cv2.IMREAD_UNCHANGED))for i in os.listdir('fgoImage')if i.endswith('.png')})
# print(IMG.CROSS)
# os.system("echo $QT_QPA_PLATFORM")
os.chdir("..")
skip = cv2.imread("blank_with_skip.png")
# skip = cv2.cvtColor(skip, cv2.COLOR_RGB2RGBA)
# print(skip.mean())
alpha = np.sum(skip, axis=-1) > 0
mask  = np.dstack((alpha,alpha,alpha))
skip*=mask
alpha = np.uint8(alpha * 255)
skip = np.dstack((skip, alpha))
target = cv2.imread("FGO-py/Screenshot_2023-09-01_05.52.48.744.png")
target2 = cv2.imread("FGO-py/Screenshot_2023-09-01_12.29.28.117.png")
# target.resize(target2.shape)
# # plt.show()

# cv2.imshow("target",target)
# cv2.rectangle(target,(1070,45),(1105,79),cv2.MORPH_BLACKHAT,thickness=2)
# cv2.rectangle(target,(1093,164),(1126,196),cv2.MORPH_BLACKHAT,thickness=2)
# cv2.rectangle(target2,(1070,45),(1105,79),cv2.MORPH_BLACKHAT,thickness=2)
# cv2.rectangle(target2,(1093,164),(1126,196),cv2.MORPH_BLACKHAT,thickness=2)
# cropped_img = target[164:196,1093:1126]
cropped_img = skip[0:75,1120:1280]
# print("shape",target.shape)
# print("shape",cropped_img.shape)
# cv2.imwrite("test.png",target)
# cv2.imwrite("test2.png",target2)
# cv2.imwrite("skip.png",cropped_img,[cv2.IMWRITE_PNG_COMPRESSION,9])
# print(cropped_img)
class Dectect:
    def __init__(self,im) -> None:
        self.im = im
    def _crop(self,rect):
        # cv2.imwrite(time.strftime(f'fgoTemp/Crop_%Y-%m-%d_%H.%M.%S_{rect}.png',time.localtime(self.time)),self.im[rect[1]+2:rect[3]-2,rect[0]+2:rect[2]-2],[cv2.IMWRITE_PNG_COMPRESSION,9])
        return self.im[rect[1]:rect[3],rect[0]:rect[2]]
    def loc(self,img,rect=(0,0,1280,720)):return cv2.minMaxLoc(cv2.matchTemplate(self._crop(rect),img[0],cv2.TM_SQDIFF_NORMED,mask=img[1]))
    def compare(self,img,rect=(0,0,1280,720),threshold=.05):return threshold>self.loc(img,rect)[0]


detect = Dectect(target)
result_t = detect.loc(IMG.CROSS)
# print('match_locs.shape:',result_t.shape) 
print('match_locs:\n',result_t)
detected_img = cv2.circle(target,(1096, 167),5, (0,255,0), -1)
cv2.imwrite("detected_img.png",detected_img)
# print(detect.compare(IMG.CROSS))

KEYMAP={
'\\x70':(527,47),'\\x71':(552,49),'\\x72':(577,49),'\\x73':(602,49),'\\x74':(627,49),'\\x75':(652,49),'\\x76':(677,49),'\\x77':(702,49),'\\x78':(727,49),'\\x79':(752,49), # VK_F1..10
'1':(185,440),'2':(399,440),'3':(649,440),'4':(875,440),'5':(1101,440),'6':(431,203),'7':(651,203),'8':(845,203),'\\xBB':(876,46),'\\x08':(1253,46), # = VK_OEM_PLUS VK_BACK
'Q':(1200,317),'W':(907,317),'E':(995,317),'R':(1084,317),'T':(140,360),'Y':(340,360),'U':(540,360),'I':(740,360),'O':(940,360),'P':(1140,360),'\\xDC':(1213,245), # \ VK_OEM_5
'A':(73,573),'S':(163,573),'D':(257,573),'F':(388,573),'G':(483,573),'H':(574,573),'J':(704,573),'K':(801,573),'L':(891,573),'\\xBA':(927,131), # ; VK_OEM_1
'Z':(640,629),'X':(173,621),'C':(330,320),'V':(1014,500),'N':(165,694),'M':(800,667),'\\xBC':(45,360),'\\xBE':(1235,360), # , VK_OEM_COMMA . VK_OEM_PERIOD
'\\x1B':(40,40),'space':(1231,687), # VK_ESCAPE
'\\x64':(45,142),'\\x65':(295,142),'\\x66':(545,142),'\\x67':(142,40),'\\x68':(342,40),'\\x69':(542,40), # VK_NUMPAD4..9
}
padding = (-40,0)
for text,i in KEYMAP.items():
    target = cv2.circle(target,i,5, (0,255,0), -1)
    target = cv2.putText(target,text,(i[0]+padding[0],i[1]+padding[1]),cv2.FONT_HERSHEY_SIMPLEX,0.75,color=(0,0,255),thickness=2)
cv2.imwrite("keymaps.png",target)