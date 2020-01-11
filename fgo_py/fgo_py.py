#/************************************************************
#*       $$$$$$$$$$$$$$$$$$$$      $$$$$$$$$$$$$$$$$$%.      *
#*     $$                   &$   =$                   $      *
#*     $                     $$$$$=                   @&     *
#*  B#$$                     $$$$$                     %%$=  *
#*  $$$$        +1s          $$-$$         +1s         $$$   *
#*  $$$$                     $-  $                     $$$   *
#*     $                     $   $                     .B    *
#*     $                     @   $                    .=     *
#*      $                   $     $                   %      *
#*       $                -$       -$                @%      *
#*        #$$$$$$$$$$$$$$$           -@$$$$$$$$$$$$$         *
#*                                                           *
#*                      莫生      莫生                       *
#*                       气        气                        *
#*                                                           *
#*                      代码垃圾非我意,                      *
#*                      自己动手分田地;                      *
#*                      你若气死谁如意?                      *
#*                      谈笑风生活长命.                      *
#************************************************************/

import time
#import PIL.Image
import os
#import subprocess
import functools
import numpy
#import pytesseract
import cv2
import win32con
import win32ui
import win32gui
#from PyQt5.QtWidgets import QApplication
#import sys

slnPath='E:/VisualStudioDocs/fgo_py/'
androidTitle='BlueStacks App Player'#'BlueStacks Android PluginAndroid'
#systemScale=1.25

#os.system('adb connect localhost:5555')
#adbPath='adb -s localhost:5555'
dpx=0
adbPath='adb -s emulator-5554'
#adbPath='adb -s 1e1b7921'
#dpx=120

#app=QApplication(sys.argv)
androidhWnd=win32gui.FindWindow(None,androidTitle)

key={
    '\x09':(1800,304),#tab VK_TAB
    '\x12':(960,943),#alt VK_MENU
    ' ':(1820,1030),
    '0':(70,69),
    '1':(277,640),
    '2':(648,640),
    '3':(974,640),
    '4':(1262,640),
    '5':(1651,640),
    '6':(646,304),
    '7':(976,304),
    '8':(1267,304),
    'A':(109,860),
    'B':(1680,368),
    'C':(845,540),
    'D':(385,860),
    'E':(1493,470),
    'F':(582,860),
    'G':(724,860),
    'H':(861,860),
    'J':(1056,860),
    'K':(1201,860),
    'L':(1336,860),
    'N':(248,1041),
    'P':(1854,69),
    'Q':(1800,475),
    'R':(1626,475),
    'S':(244,860),
    'V':(1105,540),
    'W':(1360,475),
    'X':(259,932),
    '\xA0':(41,197),# VK_LSHIFT
    '\xA1':(41,197),# VK_RSHIFT
    '\xBA':(1247,197),#; VK_OEM_1
    '\xBB':(791,69),#+= VK_OEM_PLUS
    '\xBD':(427,69),#-_ VK_OEM_MINUS
}

IMG_APEMPTY=cv2.imread(slnPath+'asserts/apempty.png')
IMG_ATTACK=cv2.imread(slnPath+'asserts/attack.png')
IMG_BEGIN=cv2.imread(slnPath+'asserts/begin.png')
IMG_HOUGUSEALED=cv2.imread(slnPath+'asserts/hougusealed.png')
IMG_BOUND=cv2.imread(slnPath+'asserts/bound.png')
IMG_BOUNDUP=cv2.imread(slnPath+'asserts/boundup.png')
#IMG_YES=cv2.imread(slnPath+'asserts/yes.png')
#IMG_NO=cv2.imread(slnPath+'asserts/no.png')
IMG_STILL=cv2.imread(slnPath+'asserts/still.png')
IMG_FAILED=cv2.imread(slnPath+'asserts/failed.png')
IMG_STAGE=[cv2.imread(slnPath+'asserts/stage/'+file)for file in os.listdir(slnPath+'asserts/stage')if file.endswith('.png')]
IMG_FRIEND=[[file[:-4],cv2.imread(slnPath+'asserts/friend/'+file)]for file in os.listdir(slnPath+'asserts/friend')if file.endswith('.png')]
IMG_CHOOSEFRIEND=cv2.imread(slnPath+'asserts/choosefriend.png')
IMG_NOFRIEND=cv2.imread(slnPath+'asserts/nofriend.png')
friendPos=4
skillInfo=[[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]]]
#skillInfo=[#minstage,minstageturn,obj
#    [[1,2,0],[1,0,0],[4,0,0]],
#    [[1,0,0],[1,0,0],[1,0,0]],
#    [[1,0,0],[1,0,0],[3,3,0]],
#    [[4,0,0],[4,0,0],[4,0,0]],
#    [[4,0,0],[4,0,0],[4,0,0]],
#    [[4,0,0],[4,0,0],[4,0,0]]]
#houguInfo=[[1,0],[1,0],[1,0],[1,1],[1,1],[1,1]]#minstage,priority
houguInfo=[[2,0],[2,0],[3,0],[1,1],[1,1],[1,1]]#minstage,priority
houguInfo[friendPos]=[3,1]

def rangeInf(start=0,step=1):
    i=start
    while True:
        yield i
        i+=step
class Fuse(object):
    def __init__(self,fv=300):
        self.__value=0
        self.__max=fv
    @property
    def value():
        return self.__value
    def increase(self):
        self.__value+=1
        if self.__value>self.__max:
            print('fused')
            beep()
            exit(0)
    def reset(self):
        self.__value=0
        return True
    def show(self):
        print(self.__value,'/',self.__max,sep='',flush=True)
fuse=Fuse()
def cmd(x):
    os.system(x)
def rgb2hsv(x):
    '''
    R,G,B:[0,255]
    H:[0,359]
    S,V:[0,100]
    '''
    R=x[2]
    G=x[1]
    B=x[0]
    cmax=max(R,G,B)
    delta=cmax-min(R,G,B)
    H=0if delta==0else((G-B)/delta if R==cmax else(B-R)/delta+2if G==cmax else(R-G)/delta+4)*60%360
    S=0if cmax==0else delta/cmax
    V=cmax
    return(int(H),int(100*S),int(V*100/255))
def tap(x,y):
    cmd(adbPath+' shell input tap {} {}'.format(x+dpx,y))
def press(c):
    tap(*key[c])
def swipe(rect,interval=500):
    cmd(adbPath+' shell input swipe {} {} {} {} {}'.format(rect[0]+dpx,rect[1],rect[2]+dpx,rect[3],interval))
def screenShot(path=slnPath,name=''):
    cmd(adbPath+' shell screencap /sdcard/adbtemp/screen.png')
    cmd(adbPath+' pull /sdcard/adbtemp/screen.png "{path}ScreenShots/{name}.png"'.format(path=path,name=name if name!=''else time.strftime("%Y-%m-%d_%H.%M.%S",time.localtime())))
def doit(touch,wait):
    for i in range(len(touch)):
        press(touch[i])
        time.sleep(wait[i]/1000)
def beep():
    cmd('echo \x07')
    time.sleep(.5)
def show(img):
    cv2.imshow('imshow',img)
    cv2.waitKey()
    cv2.destroyAllWindows()
def windowCapture(save=False,hWnd=androidhWnd):
    hWndDC=win32gui.GetWindowDC(hWnd)
    #left,top,right,bot=win32gui.GetWindowRect(hwnd)
    #width=int((right-left)*scale+.001)
    #height=int((bot-top)*scale+.001)
    width=1920
    height=1080
    mfcDC=win32ui.CreateDCFromHandle(hWndDC)
    saveDC=mfcDC.CreateCompatibleDC()
    saveBitMap=win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC,width,height)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0),(width,height),mfcDC,(0,0),win32con.SRCCOPY)
    img=numpy.frombuffer(saveBitMap.GetBitmapBits(True),dtype='uint8').reshape(height,width,4)[:,:,0:3]
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hWnd,hWndDC)
    #img=QApplication.primaryScreen().grabWindow(hwnd).toImage().constBits()
    #img.setsize(8302080)#img.byteCount(),1920*1081*4
    #img=numpy.array(img).reshape(1081,1920,4)[1:1081,0:1920,0:3]
    if save:
        cv2.imwrite(slnPath+time.strftime("ScreenShots/%Y-%m-%d_%H.%M.%S.png",time.localtime()),img)
    #fuse.show()
    return img

class Check(object):
    def __init__(self):
        fuse.increase()
        #screenShot(name='chk')
        #self.im=cv2.imread(slnPath+'ScreenShots/chk.png')[0:1080,dpx:dpx+1920]
        time.sleep(.08)
        self.im=windowCapture()
    def compare(self,img,rect=(0,0,1920,1080),delta=.03):
        return cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],img,cv2.TM_SQDIFF_NORMED))[0]<delta
    def select(self,img,rect=(0,0,1920,1080)):
        return (lambda x:x.index(min(x)))([cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],i,cv2.TM_SQDIFF_NORMED))[0]for i in img])
    def tapOnCmp(self,img,rect=(0,0,1920,1080),delta=.03):
        loc=cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],img,cv2.TM_SQDIFF_NORMED))
        if loc[0]>=delta:
            return False
        tap(rect[0]+loc[2][0]+img.shape[1]//2,rect[1]+loc[2][1]+img.shape[0]//2)
        time.sleep(.5)
        return fuse.reset()
    def isTurnBegin(self):
        return self.compare(IMG_ATTACK,(1567,932,1835,1064))and fuse.reset()
    def isBattleOver(self):
        return(self.compare(IMG_BOUND,(95,235,460,318))or self.compare(IMG_BOUNDUP,(978,517,1491,596),.06))and fuse.reset()
    def isBegin(self):
        return self.compare(IMG_BEGIN,(1630,950,1919,1079))and fuse.reset()
    def isHouguReady(self):
        return[rgb2hsv(self.im[1004][290+480*i])[1]>2for i in range(3)]
    def isHouguSealed(self):
        return[self.compare(IMG_HOUGUSEALED,(470+i*346,258,768+i*346,387),.3)for i in range(3)]
    def isSkillReady(self):
        return[[not self.compare(IMG_STILL,(65+480*i+141*j,895,107+480*i+141*j,927))for j in range(3)]for i in range(3)]
    def isApEmpty(self):
        return self.compare(IMG_APEMPTY,(800,50,1120,146))and fuse.reset()
    def isChooseFriend(self):
        return self.compare(IMG_CHOOSEFRIEND,(1628,314,1772,390))and fuse.reset()
    def isNoFriend(self):
        return self.compare(IMG_NOFRIEND,(369,545,1552,797),.1)and fuse.reset()
    def getABQ(self):
        return[(lambda x:x.index(max(x)))((lambda tc:[int(numpy.mean([j[i]for k in tc for j in k]))for i in(2,1,0)])(self.im[771:919,108+386*i:318+386*i]))for i in range(5)]
    def getStage(self):
        return self.select(IMG_STAGE,(1290,14,1348,60))+1
    def getPortrait(self):
        return[self.im[640:740,195+480*i:296+480*i]for i in range(3)]

def chooseFriend():
    while True:
        for i in range(6):
            chk=Check()
            for img in IMG_FRIEND:
                if chk.tapOnCmp(img[1],delta=.015):
                    print('  Friend :',img[0])
                    try:
                        skillInfo[friendPos]={
                            'km':[[2,0,1],[1,0,0],[1,0,0]],
                            'cba':[[3,0,2],[3,0,0],[1,0,1]],
                            'ml':[[1,0,0],[1,0,0],[3,0,1]],
                        }[img[0][0:img[0].find('_')]]
                    except KeyError:
                        skillInfo[friendPos]=[[4,0,0],[4,0,0],[4,0,0]]
                    time.sleep(1)
                    return
            swipe((220,960,220,457))
            time.sleep(.2)
        doit('\xBAJ',(500,1000))

def draw():
    while True:
        for i in range(320):
            press('2')
            time.sleep(.2)
        #doit('_L',(300,1500))

def setSkillInfo(s):
    if s=='saber':#muzashi/modoredo/okita
        skillInfo[0]=[[1,0,0],[1,0,0],[3,5,0]]
        skillInfo[1]=[[1,0,0],[1,2,0],[1,0,0]]
        skillInfo[2]=[[1,0,0],[1,2,0],[3,5,0]]
    elif s=='archer':#arutoria/erio/atera
        skillInfo[0]=[[1,0,0],[4,0,0],[1,0,0]]
        skillInfo[1]=[[1,0,0],[3,0,0],[3,5,0]]
        skillInfo[2]=[[1,0,1],[1,0,2],[4,0,0]]
    elif s=='lancer':#ere/tamamo/jyanu
        skillInfo[0]=[[3,4,0],[1,0,0],[2,0,0]]
        skillInfo[1]=[[1,0,0],[3,0,0],[4,0,0]]
        skillInfo[2]=[[3,0,1],[1,0,0],[3,4,0]]
    elif s=='rider':#arutoria/asutorufo/maruta
        skillInfo[0]=[[3,0,1],[2,0,0],[1,0,0]]
        skillInfo[1]=[[1,0,0],[3,0,0],[1,0,0]]
        skillInfo[2]=[[3,0,0],[3,0,0],[3,0,0]]
    elif s=='caster':#malin/girugyameshi/mari
        skillInfo[0]=[[1,0,0],[3,4,0],[1,0,2]]
        skillInfo[1]=[[1,0,0],[1,0,0],[1,0,0]]
        skillInfo[2]=[[1,0,0],[1,0,0],[1,0,0]]
    elif s=='assassin':#kurobatera/hiroinx/jakku
        skillInfo[0]=[[1,0,0],[1,0,0],[3,6,0]]
        skillInfo[1]=[[2,0,0],[3,6,0],[4,0,0]]
        skillInfo[2]=[[3,6,0],[3,2,0],[3,0,3]]
    elif s=='ex':#hokusai/bb/hiroinx
        skillInfo[0]=[[1,0,0],[1,0,0],[1,0,0]]
        skillInfo[1]=[[1,2,0],[1,0,0],[4,0,0]]
        skillInfo[2]=[[3,6,0],[2,0,0],[1,0,0]]

def oneBattle(danger=(0,0,1)):
    turn=0
    stage=0
    servant=[[0,1,2],[]]
    while True:
        chk=Check()
        if chk.isTurnBegin():
            time.sleep(.3)
            chk=Check()
            newStage=chk.getStage()
            if stage!=newStage:
                stage=newStage
                stageTurn=0
            turn+=1
            stageTurn+=1
            skill=chk.isSkillReady()
            if stageTurn==1 and danger[stage-1]!=0:
                doit('\xBB\xBD0'[danger[stage-1]]+'P',(50,500))
            if turn==1:
                servant[1]=chk.getPortrait()
            else:
                port=chk.getPortrait()
                for i in range(3):
                    if cv2.matchTemplate(servant[1][i],port[i],cv2.TM_SQDIFF_NORMED)[0][0]>=.1:
                        servant[1][i]=port[i]
                        servant[0][i]=max(servant[0])+1
            for i in range(3):
                if servant[0][i]>=6:
                    continue
                for j in range(3):
                    if skill[i][j]and(stage>skillInfo[servant[0][i]][j][0]or stage==skillInfo[servant[0][i]][j][0]and stageTurn>=skillInfo[servant[0][i]][j][1]):
                        doit((('A','S','D'),('F','G','H'),('J','K','L'))[i][j],(300,))
                        if skillInfo[servant[0][i]][j][2]!=0:
                            doit(chr(skillInfo[servant[0][i]][j][1]+50),(300,))
                        time.sleep(2)
                        while not Check().isTurnBegin():
                            time.sleep(.2)
            hougu=(lambda x,y:[servant[0][i]<6and x[i]and y[i]for i in range(3)])(Check().isHouguReady(),Check().isHouguReady())
            doit(' ',(1800,))
            chk=Check()
            color=chk.getABQ()
            hougu=(lambda x,y:[x[i]^y[i]for i in range(3)])(hougu,chk.isHouguSealed())
            card=[chr(i+54)for pri in(2,1,0)for i in range(3)if hougu[i]and stage>=houguInfo[servant[0][i]][0]and houguInfo[servant[0][i]][1]==pri]
            if len(card)==0:
                card=[chr(j+49)for i in range(3)if color.count(i)>=3for j in range(5)if color[j]==i]
            if len(card)<3:
                card+=[chr(j+49)for i in(0,2,1)for j in range(5)if color[j]==i]
            print('    ',turn,stage,stageTurn,servant[0],skill,hougu,'\n          ',color,card)
            doit(card[:3],(80,80,10000))
        elif chk.isBattleOver():
            print('  Battle Finished')
            break
        elif chk.tapOnCmp(IMG_FAILED,rect=(277,406,712,553)):
            print('  Battle Failed')
            doit('VJ  F ',(500,500,500,500,500,10000))
            return
        else:
            time.sleep(.2)
    doit('             F ',(200,200,200,200,200,200,200,200,200,200,200,200,200,200,8000))
    while not Check().isBegin():
        doit(' ',(200,))

def main(appleCount=0,appleKind=0,battleFunc=oneBattle,*args,**kwargs):
    apple=appleCount
    for i in rangeInf(1):
    #for i in range(1,4):
        doit('8',(1000,))
        if Check().isApEmpty():
            if apple==0:
                print('Ap Empty')
                press('\x12')
                return
            else:
                doit('W4K8'[appleKind]+'L',(600,1500))
                apple-=1
                print('Apple :',appleCount-apple)
        print('  Battle',i)
        while True:
            chk=Check()
            if chk.isNoFriend():
                doit('\xBAJ',(500,1000))
                while True:
                    chk=Check()
                    if chk.isNoFriend():
                        return
                    if chk.isChooseFriend():
                        break
                    time.sleep(.2)
            if chk.isChooseFriend():
                break
            time.sleep(.2)
        #chooseFriend()
        doit('8',(1000,))
        doit(' ',(15000,))
        battleFunc(*args,**kwargs)
        while not Check().isBegin():
            doit(' ',(200,))

def otk():
    while not Check().isTurnBegin():
        time.sleep(.5)
    doit("S2F2GH2J2KL2QE2 654",(300,2600,300,2600,2600,300,2600,300,2600,2600,300,2600,300,300,2600,1200,100,100,17000))
    while not Check().isBattleOver():
        time.sleep(.5)
    doit('     F ',(200,200,200,200,200,200,10000))

#main()
setSkillInfo('assassin')
oneBattle((0,2,2))
#main()
main(5,0,danger=(0,2,2))
#main(battleFunc=otk)
#otk()
beep()
