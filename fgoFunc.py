'Full-automatic FGO Script'
__author__='hgjazhgj'
import time,os,numpy,cv2,re,functools
from airtest.core.android.android import Android
from airtest.core.android.constant import CAP_METHOD,ORI_METHOD
IMG_APEMPTY=cv2.imread('image/apempty.png')
IMG_ATTACK=cv2.imread('image/attack.png')
IMG_BEGIN=cv2.imread('image/begin.png')
IMG_BOUND=cv2.imread('image/bound.png')
IMG_BOUNDUP=cv2.imread('image/boundup.png')
IMG_CARDSEALED=cv2.imread('image/cardsealed.png')
IMG_CHOOSEFRIEND=cv2.imread('image/choosefriend.png')
IMG_END=cv2.imread('image/end.png')
IMG_FAILED=cv2.imread('image/failed.png')
IMG_FRIEND=[[file[:-4],cv2.imread('image/friend/'+file)]for file in os.listdir('image/friend')if file.endswith('.png')]
IMG_HOUGUSEALED=cv2.imread('image/hougusealed.png')
IMG_NOFRIEND=cv2.imread('image/nofriend.png')
IMG_STILL=cv2.imread('image/still.png')
IMG_STAGE=[cv2.imread('image/stage/'+file)for file in os.listdir('image/stage')if file.startswith('stage')and file.endswith('.png')]
skillInfo=[[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]]]#minstage,minstageturn,obj
houguInfo=[[1,1],[1,1],[1,1],[1,1],[1,1],[1,1]]#minstage,priority
dangerPos=[0,0,1]
friendPos=4
terminateFlag=False
suspendFlag=False
def getTime():return time.strftime('%Y-%m-%d_%H.%M.%S',time.localtime())
def printer(*args,**kwargs):print(getTime(),*args,**kwargs)
def beep():os.system('echo \x07')
def show(img):cv2.imshow('imshow',img),cv2.waitKey(),cv2.destroyAllWindows()
class Fuse:
    def __init__(self,fv=600):
        self.__value=0
        self.__max=fv
    @property
    def value():return self.__value
    @property
    def max():return self.__max
    def increase(self):
        assert self.__value<self.__max
        self.__value+=1
    def reset(self):
        self.__value=0
        return True
fuse=Fuse()
class Base(Android):
    def __init__(self,serialno=None):
        try:super().__init__(serialno,cap_method=CAP_METHOD.JAVACAP,ori_method=ORI_METHOD.ADB)
        except:
            self.serialno=None
            return
        self.tapOffset,self.tapScale=(lambda size:((0,round(960*size[0]/size[1])-540),1920/size[1])if size[1]*1080<size[0]*1920else((round(540*size[1]/size[0])-960,0),1080/size[0]))(sorted(self.get_current_resolution()))
        self.key={c:[round((p[i]+self.tapOffset[i])/self.tapScale)for i in range(2)]for c,p in
           {' ':(1820,1030),'1':(277,640),'2':(648,640),'3':(974,640),'4':(1262,640),'5':(1651,640),'6':(646,304),'7':(976,304),'8':(1267,304),
            'A':(109,860),'B':(1680,368),'C':(845,540),'D':(385,860),'E':(1493,470),'F':(582,860),'G':(724,860),'H':(861,860),'J':(1056,860),'K':(1201,860),
            'L':(1336,860),'N':(248,1041),'P':(1854,69),'Q':(1800,475),'R':(1626,475),'S':(244,860),'V':(1105,540),'W':(1360,475),'X':(259,932),
            '\x64':(70,221),'\x65':(427,221),'\x66':(791,221),'\x67':(70,69),'\x68':(427,69),'\x69':(791,69),#NUM4 #NUM5 #NUM6 #NUM7 #NUM8 #NUM9
            '\x09':(1800,304),'\x12':(960,943),'\xA0':(41,197),'\xA1':(41,197),'\xBA':(1247,197)}.items()}# VK_LSHIFT # VK_RSHIFT #; VK_OEM_1 #tab VK_TAB #alt VK_MENU
    def tap(self,x,y):self.touch([round(i*self.tapScale)for i in[x+self.tapOffset[0],y+self.tapOffset[1]]])
    def swipe(self,rect):super().swipe(*[[round((rect[(i<<1)+j]+self.tapOffset[j])*self.tapScale)for j in range(2)]for i in range(2)])
    def press(self,c):self.touch(self.key[c])
base=Base()
def doit(touch,wait):[(base.press(i),time.sleep(j*.001))for i,j in zip(touch,wait)]
class Check:
    def __init__(self,lagency=.02):
        global suspendFlag
        while suspendFlag:time.sleep(.05)
        if terminateFlag:exit(0)
        time.sleep(lagency)
        fuse.increase()
        #self.im=(lambda im:im[(im.shape[0]>>1)-540:(im.shape[0]>>1)+540,(im.shape[1]>>1)-960:(im.shape[1]>>1)+960])((lambda scale:cv2.resize(img,(0,0),None,scale,scale,cv2.INTER_CUBIC))(max(1920/img.shape[1],1080/img.shape[0])))
        self.im=cv2.resize(base.snapshot()[base.tapOffset[1]:-base.tapOffset[1]if base.tapOffset[1]else None,base.tapOffset[0]:-base.tapOffset[0]if base.tapOffset[0]else None],(0,0),None,base.tapScale,base.tapScale,cv2.INTER_CUBIC)
    def compare(self,img,rect=(0,0,1920,1080),delta=.03):return cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],img,cv2.TM_SQDIFF_NORMED))[0]<delta
    def select(self,img,rect=(0,0,1920,1080)):return(lambda x:x.index(min(x)))([cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],i,cv2.TM_SQDIFF_NORMED))[0]for i in img])
    def tapOnCmp(self,img,rect=(0,0,1920,1080),delta=.03):return(lambda loc:loc[0]<delta and(base.tap(rect[0]+loc[2][0]+img.shape[1]//2,rect[1]+loc[2][1]+img.shape[0]//2),time.sleep(.5),fuse.reset())[2])(cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],img,cv2.TM_SQDIFF_NORMED)))
    def save(self,name=''):cv2.imwrite('ScreenShots/'+(getTime()+'.png'if name==''else name),self.im);return self
    def show(self):show(cv2.resize(self.im,(800,450)));return self
    def isTurnBegin(self):return self.compare(IMG_ATTACK,(1567,932,1835,1064))and fuse.reset()
    def isBattleOver(self):return(self.compare(IMG_BOUND,(95,235,460,318))or self.compare(IMG_BOUNDUP,(978,517,1491,596),.06))and fuse.reset()
    def isBegin(self):return self.compare(IMG_BEGIN,(1630,950,1919,1079))and fuse.reset()
    def isHouguReady(self):return(lambda im:[not any([self.compare(j,(470+346*i,258,768+346*i,387),.3)for j in(IMG_HOUGUSEALED,IMG_CARDSEALED)])and(numpy.mean(self.im[1014:1021,217+480*i:235+480*i])>90or numpy.mean(im[1014:1021,217+480*i:235+480*i])>90)for i in range(3)])(Check(.8).im)
    def isSkillReady(self):return[[not self.compare(IMG_STILL,(65+480*i+141*j,895,107+480*i+141*j,927),.06)for j in range(3)]for i in range(3)]
    def isApEmpty(self):return self.compare(IMG_APEMPTY,(800,50,1120,146))and fuse.reset()
    def isChooseFriend(self):return self.compare(IMG_CHOOSEFRIEND,(1628,314,1772,390))and fuse.reset()
    def isNoFriend(self):return self.compare(IMG_NOFRIEND,(369,545,1552,797),.1)and fuse.reset()
    def getABQ(self):return[-1if self.compare(IMG_CARDSEALED,(43+386*i,667,345+386*i,845),.3)else(lambda x:x.index(max(x)))([numpy.mean(self.im[771:919,108+386*i:318+386*i,j])for j in(2,1,0)])for i in range(5)]
    def getStage(self):return self.select(IMG_STAGE,(1290,14,1348,60))+1
    def getPortrait(self):return[self.im[640:740,195+480*i:296+480*i]for i in range(3)]
def draw():
    while True:base.press('2')
def chooseFriend():
    if len(IMG_FRIEND)==0:
        doit('8',(1000,))
        return
    while True:
        for _ in range(16):
            chk=Check(.3)
            for name,img in functools.filter(lambda img:chk.tapOnCmp(img,delta=.015),IMG_FRIEND):
                printer('  Friend:',name)
                try:p=re.search('[0-9x]{11}$',name,re.I).group()
                except AttributeError:pass
                else:
                    skillInfo[friendPos]=[[skillInfo[friendPos][i][j]if p[i*3+j]=='x'else int(p[i*3+j])for j in range(3)]for i in range(3)]
                    houguInfo[friendPos]=[houguInfo[friendPos][i]if p[i]=='x'else int(p[i])for i in range(9,11)]
                time.sleep(1)
                return
            base.swipe((220,960,220,550))
        doit('\xBAJ',(500,1000))
        while True:
            chk=Check(.2)
            assert not chk.isNoFriend()
            if chk.isChooseFriend():break
def oneBattle():
    turn,stage,stageTurn,servant=0,0,0,[0,1,2]
    while True:
        chk=Check(.1)
        if chk.isTurnBegin():
            turn,stage,stageTurn,skill,newPortrait=[turn+1]+(lambda chk:(lambda x:[x,stageTurn+1if stage==x else 1])(chk.getStage())+[chk.isSkillReady(),chk.getPortrait()])(Check(.3))
            if stageTurn==1:doit('\x69\x68\x67\x66\x65\x64'[dangerPos[stage-1]]+'P',(250,500))
            if turn>1:servant=(lambda m,p:[m+p.index(i)+1if i in p else servant[i]for i in range(3)])(max(servant),[i for i in range(3)if servant[i]<6and cv2.matchTemplate(newPortrait[i],portrait[i],cv2.TM_SQDIFF_NORMED)[0][0]>=.03])
            portrait=newPortrait
            printer('   ',turn,stage,stageTurn,servant)
            for i,j in((i,j)for i in range(3)if servant[i]<6for j in range(3)if skill[i][j]and stage<<8|stageTurn>=skillInfo[servant[i]][j][0]<<8|skillInfo[servant[i]][j][1]):
                doit(('ASD','FGH','JKL')[i][j],(300,))
                if skillInfo[servant[i]][j][2]:doit(chr(skillInfo[servant[i]][j][2]+49),(300,))
                time.sleep(2)
                while not Check(.1).isTurnBegin():pass
            doit(' ',(2250,))
            doit((lambda chk:(lambda c,h:([chr(i+54)for i in sorted((i for i in range(3)if h[i]),key=lambda x:-houguInfo[servant[x]][1])]if any(h)else[chr(j+49)for i in range(3)if c.count(i)>=3for j in range(5)if c[j]==i])+[chr(i+49)for i in sorted(range(5),key=lambda x:(c[x]&2)>>1|(c[x]&1)<<1)])(chk.getABQ(),(lambda h:[servant[i]<6and h[i]and stage>=houguInfo[servant[i]][0]for i in range(3)])(chk.isHouguReady())))(Check())[:3],(200,200,10000))
        elif chk.isBattleOver():
            printer('  Battle Finished')
            return True
        elif chk.tapOnCmp(IMG_FAILED,rect=(277,406,712,553)):
            printer('  Battle Failed')
            beep()
            return False
def main(appleCount=0,appleKind=0,battleFunc=oneBattle):
    apple,battle=0,0
    while True:
        battle+=1
        doit('8',(800,))
        if Check().isApEmpty():
            if apple==appleCount:
                printer('Ap Empty')
                base.press('\x12')
                return
            else:
                apple+=1
                printer('Apple',apple)
                doit('W4K8'[appleKind]+'L',(400,1200))
        printer('  Battle',battle)
        flush=True
        while True:
            chk=Check(.1)
            if chk.isNoFriend():
                if flush:
                    doit('\xBAJ',(500,1000))
                    flush=False
                else:raise AssertionError
            if chk.isChooseFriend():break
        chooseFriend()
        doit(' ',(10000,))
        if not battleFunc():doit('VJ',(500,500))
        doit('    ',(200,200,200,200))
        while True:
            chk=Check()
            if chk.isBegin():break
            chk.tapOnCmp(IMG_END,rect=(243,863,745,982))
            doit(' ',(300,))
