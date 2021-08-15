# Stars  Cosmos Gods  Animus    Antrum       Unbirth    Anima Animusphere
# 星の形.宙の形.神の形.我の形.天体は空洞なり.空洞は虚空なり.虚空には神ありき.
# 地を照らし,空に在り,天上の座標を示せ.
# カルディアの灯よ.
# どうか今一度,旅人の標とならん事を.
# ここで,Bgo運営の敗北を宣言する!
# .        OO---O---O-o\
# .       // \ / \ / \ \\
# .      OO   O   O   O \\
# .     // \   \ /   / \ \\
# .    oO---O---O---O---O-Oo
# .     \\ /   / \   \ / //
# .      \O   O   O   O //
# .       \\ / \ / \ / //
# .        oO---O---Oo-O
# .             ^^
# .  Grand Order/Anima Animusphere
# .     冠位指定/人理保障天球
'Full-automatic FGO Script'
__author__='hgjazhgj'
__version__='v6.3.4'
# 素に銀と鉄.礎に石と契約の大公.
import logging
# 降り立つ風には壁を.
import os
# 四方の門は閉じ,王冠より出で,王国に至る三叉路は循環せよ.
import re
# 満たせ.満たせ.満たせ.満たせ.満たせ.
import threading
# 繰り返すつどに五度.
import time
# ただ,満たされる刻を破却する.
from functools import wraps,reduce
# ――――告げる.
from itertools import permutations
# 汝の身は我が下に,我が命運は汝の剣に.
import cv2
# 聖杯の寄るべに従い,この意,この理に従うならば応えよ!
import numpy
# 誓いを此処に.
import win32con
# 我は常世総ての善と成る者,我は常世総ての悪を敷く者.
import win32file
# 汝三大の言霊を纏う七天,抑止の輪より来たれ,
from airtest.core.android.adb import ADB
# 天秤の守り手よ―――！
from airtest.core.android.android import Android
(lambda logger:(logger.setLevel(logging.INFO),logger)[-1])(logging.getLogger('airtest')).handlers[0].setFormatter(type('ColoredFormatter',(logging.Formatter,),{'__init__':lambda self,*args,**kwargs:logging.Formatter.__init__(self,*args,**kwargs),'format':lambda self,record:(setattr(record,'levelname','\033[{}m[{}]'.format({'WARNING':'33','INFO':'34','DEBUG':'37','CRITICAL':'35','ERROR':'31'}.get(record.levelname,'0'),record.levelname)),logging.Formatter.format(self,record))[-1]})('\033[32m[%(asctime)s]%(levelname)s\033[36m<%(name)s>\033[0m %(message)s','%H:%M:%S'))
(lambda logger:(logger.setLevel(logging.DEBUG),logger.addHandler((lambda handler:(handler.setFormatter(type('ColoredFormatter',(logging.Formatter,),{'__init__':lambda self,*args,**kwargs:logging.Formatter.__init__(self,*args,**kwargs),'format':lambda self,record:(setattr(record,'levelname','\033[{}m[{}]'.format({'WARNING':'33','INFO':'34','DEBUG':'37','CRITICAL':'35','ERROR':'31'}.get(record.levelname,'0'),record.levelname)),logging.Formatter.format(self,record))[-1]})('\033[32m[%(asctime)s]%(levelname)s\033[36m<%(name)s>\033[0m %(message)s','%H:%M:%S')),handler)[-1])(logging.StreamHandler()))))(logging.getLogger('fgo'))
logger=logging.getLogger('fgo.Func')
bilibili=[1,2,3,4,5,6,7,8,10,11,12]
IMG=(lambda t:([setattr(t,i[:-4].upper(),cv2.imread(f'fgoImage/{i}'))for i in os.listdir('fgoImage')if i[-4:]=='.png'],t)[-1])(type('IMG',(),{}))
DebugMeta=type('DebugMeta',(type,),{'__new__':lambda cls,name,bases,attrs:type(name,bases,{i:cls.logit()(j)if callable(j)and i[0]!='_'else j for i,j in attrs.items()}),'logit':staticmethod(lambda level=logging.DEBUG:lambda func:wraps(func)(lambda*args,**kwargs:(lambda x:(logger.log(level,' '.join((func.__name__,str(x)[:100].split("\n",1)[0]))),x)[-1]if x is not None else x)(func(*args,**kwargs))))})
ScriptTerminate=type('ScriptTerminate',(Exception,),{'__init__':lambda self,msg='Unknown Reason':Exception.__init__(self,f'Script Stopped: {msg}')})
class Control:
    def __init__(self):
        self.reset()
        self.__stopOnDefeatedFlag=True
        self.__stopOnSpecialDropFlag=True
    def reset(self):
        self.__terminateFlag=False
        self.__suspendFlag=False
        self.__terminateLaterFlag=-1
    def terminate(self):self.__terminateFlag=True
    def checkTerminate(self):
        if self.__terminateFlag:raise ScriptTerminate('Terminate Command Effected')
    def suspend(self):self.__suspendFlag=not self.__suspendFlag
    def checkSuspend(self):
        while self.__suspendFlag:
            self.checkTerminate()
            time.sleep(.07)
    def terminateLater(self,count=-1):self.__terminateLaterFlag=count
    def checkTerminateLater(self):
        if not self.__terminateLaterFlag:raise ScriptTerminate('Terminate Appointment Effected')
        self.__terminateLaterFlag-=1
    def sleep(self,x,part=.07):
        timer=time.time()+x-part
        while time.time()<timer:
            self.checkSuspend()
            self.checkTerminate()
            time.sleep(part)
        time.sleep(max(0,timer+part-time.time()))
    def stopOnDefeated(self):self.__stopOnDefeatedFlag=not self.__stopOnDefeatedFlag
    def checkDefeated(self):
        if self.__stopOnDefeatedFlag:raise ScriptTerminate('Battle Defeated')
    def stopOnSpecialDrop(self):self.__stopOnSpecialDropFlag=not self.__stopOnSpecialDropFlag
    def checkSpecialDrop(self):
        if self.__stopOnSpecialDropFlag:raise ScriptTerminate('Special Drop')
control=Control()
class Fuse:
    def __init__(self,fv=400,show=3,logsize=10):
        self.__value=0
        self.__max=fv
        self.show=show
        self.logsize=logsize
        self.log=[None]*logsize
        self.logptr=0
    @property
    def value(self):return self.__value
    @property
    def max(self):return self.__max
    def increase(self):
        if self.__value>self.__max:
            self.save()
            raise ScriptTerminate('Fused')
        self.__value+=1
    def reset(self):
        if self.__value>self.show:logger.debug(f'Fuse {self.__value}')
        self.__value=0
        if check is not self.log[(self.logptr-1)%self.logsize]:
            self.log[self.logptr]=check
            self.logptr=(self.logptr+1)%self.logsize
        return True
    def save(self,path='.'):
        for i in(i for i in range(self.logsize)if self.log[(i+self.logptr)%self.logsize]):self.log[(i+self.logptr)%self.logsize].save(f'{path}/fuselog_%Y-%m-%d_%H.%M.%S_{i:02}.jpg')
        check.save(f'{path}/fuselog_%Y-%m-%d_%H.%M.%S.jpg')
fuse=Fuse()
class DirListener:
    def __init__(self,dir):
        self.hDir=win32file.CreateFile(dir,win32con.GENERIC_READ,win32con.FILE_SHARE_READ|win32con.FILE_SHARE_WRITE|win32con.FILE_SHARE_DELETE,None,win32con.OPEN_EXISTING,win32con.FILE_FLAG_BACKUP_SEMANTICS,None)
        self.msg=[]
        self.lock=threading.Lock()
        self.ren=''
        def f():
            while True:self.add(win32file.ReadDirectoryChangesW(self.hDir,0x1000,False,win32con.FILE_NOTIFY_CHANGE_FILE_NAME|win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,None,None))
        threading.Thread(target=f,daemon=True,name=f'DirListener({dir})').start()
    def add(self,x):
        def onCreated(file):
            for i in(i for i in range(len(self.msg)-1,-1,-1)if self.msg[i][1]==file):
                if self.msg[i][0]==2:
                    self.msg[i][0]=3
                    return
                break
            self.msg.append([1,file])
        def onDeleted(file):
            for i in(i for i in range(len(self.msg)-1,-1,-1)if self.msg[i][1]==file):
                if self.msg[i][0]==1:
                    del self.msg[i]
                    return
                if self.msg[i][0]==3:
                    del self.msg[i]
                    break
                temp=self.msg[i-1][1]
                del self.msg[i-1:i+1]
                return onDeleted(temp)
            self.msg.append([2,file])
        def onUpdated(file):
            for i in(i for i in range(len(self.msg)-1,-1,-1)if self.msg[i][1]==file):
                if self.msg[i][0]==1or self.msg[i][0]==3:return
                if self.msg[i][0]==5:
                    temp=self.msg[i-1][1]
                    del self.msg[i-1:i+1]
                    onDeleted(temp)
                    return onCreated(file)
                break
            self.msg.append([3,file])
        def onRenamedFrom(file):self.ren=file
        def onRenamedTo(file):
            for i in range(len(self.msg)-1,-1,-1):
                if self.msg[i][1]==file:break
                if self.msg[i][1]==self.ren:
                    if self.msg[i][0]==1:
                        del self.msg[i]
                        return onCreated(file)
                    if self.msg[i][0]==3:
                        self.msg[i][0]=2
                        return onCreated(file)
                    if self.msg[i][0]==5:
                        self.ren=self.msg[i-1][1]
                        del self.msg[i-1:i+1]
                        if self.ren==file:return
                    break
            self.msg+=[[4,self.ren],[5,file]]
        with self.lock:[{1:onCreated,2:onDeleted,3:onUpdated,4:onRenamedFrom,5:onRenamedTo}.get(i[0],lambda _:logger.warning(f'Unknown Operate {i}'))(i[1])for i in x]
    def get(self):
        with self.lock:ans,self.msg=self.msg,[]
        return ans
class ImageListener(dict):
    def __init__(self,path,ends='.png'):
        super().__init__((file[:-len(ends)],cv2.imread(path+file))for file in os.listdir(path)if file.endswith(ends))
        self.path=path
        self.ends=ends
        self.listener=DirListener(path)
    def flush(self):
        lastAction=0
        oldName=None
        def onCreated(name):self[name]=cv2.imread(self.path+name+self.ends)
        def onDeleted(name):del self[name]
        def onUpdated(name):self[name]=cv2.imread(self.path+name+self.ends)
        def onRenamedFrom(name):
            nonlocal oldName
            if oldName is not None:del self[oldName]
            oldName=name
        def onRenamedTo(name):self[name]=self[oldName]if lastAction==4else cv2.imread(self.path+name+self.ends)
        for action,name in((action,file[:-len(self.ends)])for action,file in self.listener.get()if file.endswith(self.ends)):
            {1:onCreated,2:onDeleted,3:onUpdated,4:onRenamedFrom,5:onRenamedTo}.get(action,lambda _:None)(name)
            lastAction=action
        if oldName is not None:del self[oldName]
        return self
friendImg=ImageListener('fgoImage/friend/')
mailFilterImg=ImageListener('fgoImage/mailfilter/')
class Base(Android):
    def __init__(self,serialno=None):
        self.lock=threading.Lock()
        try:
            super().__init__(serialno,cap_method='JAVACAP')
            self.rotation_watcher.reg_callback(lambda _:self.refreshOrientation())
            self.touch_proxy
        except Exception:self.serialno=None
    @property
    def avaliable(self):
        if not self.serialno:return False
        # if self.rotation_watcher._t.is_alive():return True # More out-sync
        if self.touch_proxy.server_proc.poll()is None:return True # Only compatible with minitouch & maxtouch
        self.serialno=None
        return False
    @staticmethod
    def enumDevices():return[i for i,_ in ADB().devices('device')]
    def refreshOrientation(self):
        self.render=[round(i)for i in self.get_render_resolution(True)]
        self.scale,self.border=(1080/self.render[3],(round(self.render[2]-self.render[3]*16/9)>>1,0))if self.render[2]*9>self.render[3]*16else(1920/self.render[2],(0,round(self.render[3]-self.render[2]*9/16)>>1))
        self.key={c:[round(p[i]/self.scale+self.border[i]+self.render[i])for i in range(2)]for c,p in{
            '\x70':(790,74),'\x71':(828,74),'\x72':(866,74),'\x73':(903,74),'\x74':(940,74),'\x75':(978,74),'\x76':(1016,74),'\x77':(1053,74),'\x78':(1091,74),'\x79':(1128,74), # VK_F1..10
            '1':(277,640),'2':(598,640),'3':(974,640),'4':(1312,640),'5':(1651,640),'6':(646,304),'7':(976,304),'8':(1267,304),'0':(1819,367),
            'Q':(1800,475),'W':(1360,475),'E':(1493,475),'R':(1626,475),'T':(210,540),'Y':(510,540),'U':(810,540),'I':(1110,540),'O':(1410,540),'P':(1710,540),'\xDC':(1880,40), # \ VK_OEM_5
            'A':(109,860),'S':(244,860),'D':(385,860),'F':(582,860),'G':(724,860),'H':(861,860),'J':(1056,860),'K':(1201,860),'L':(1336,860),'\xBA':(1247,197), # ; VK_OEM_1
            'Z':(960,943),'X':(259,932),'B':(495,480),'N':(248,1041),'M':(1200,1000),
            ' ':(1846,1030),
            '\x64':(70,221),'\x65':(427,221),'\x66':(791,221),'\x67':(70,69),'\x68':(427,69),'\x69':(791,69), # VK-NUMPAD4..9
            }.items()}
    def touch(self,pos):
        with self.lock:super().touch([round(pos[i]/self.scale+self.border[i]+self.render[i])for i in range(2)])
    # def swipe(self,rect):
    #     with self.lock:super().swipe(*[[rect[i<<1|j]/self.scale+self.border[j]+self.render[j]for j in range(2)]for i in range(2)])
    def swipe(self,rect): # If this doesn't work, use the above one instead
        p1,p2=[numpy.array(self._touch_point_by_orientation([rect[i<<1|j]/self.scale+self.border[j]+self.render[j]for j in range(2)]))for i in range(2)]
        vd=p2-p1
        lvd=numpy.linalg.norm(vd)
        vd/=.2*self.scale*lvd
        vx=numpy.array([0.,0.])
        def send(method,pos):self.touch_proxy.handle(' '.join((method,'0',*[str(i)for i in self.touch_proxy.transform_xy(*pos)],'50\nc\n')))
        with self.lock:
            send('d',p1)
            time.sleep(.01)
            for _ in range(2):
                send('m',p1+vx)
                vx+=vd
                time.sleep(.02)
            vd*=5
            while numpy.linalg.norm(vx)<lvd:
                send('m',p1+vx)
                vx+=vd
                time.sleep(.008)
            send('m',p2)
            time.sleep(.35)
            self.touch_proxy.handle('u 0\nc\n')
            time.sleep(.02)
    def press(self,key):
        with self.lock:super().touch(self.key[key])
    def perform(self,pos,wait):[(self.press(i),control.sleep(j*.001))for i,j in zip(pos,wait)]
    def screenshot(self):return cv2.resize(super().snapshot()[self.render[1]+self.border[1]:self.render[1]+self.render[3]-self.border[1],self.render[0]+self.border[0]:self.render[0]+self.render[2]-self.border[0]],(1920,1080),interpolation=cv2.INTER_CUBIC)
base=Base()
check=None
class Check(metaclass=DebugMeta):
    def retryOnError(interval=.1,err=TypeError):
        def wrapper(func):
            @wraps(func)
            def wrap(self,*args,**kwargs):
                try:
                    if(ans:=func(self,*args,**kwargs))is not None:return ans
                except err:pass
                logger.warning(f'Retry {getattr(func,"__qualname__",getattr(type(func),"__qualname__","Unknown"))}({",".join(repr(i)for i in args)}{","if kwargs else""}{",".join("%s=%r"%i for i in kwargs.items())})')
                return wrap(Check(interval),*args,**kwargs)
            return wrap
        return wrapper
    def __init__(self,forwordLagency=.1,backwordLagency=0):
        control.sleep(forwordLagency)
        self.im=base.screenshot()
        global check
        check=self
        fuse.increase()
        control.sleep(backwordLagency)
    def __call__(self,img,rect=(0,0,1920,1080),threshold=.05):return(lambda loc:loc[0]<threshold and(base.touch((rect[0]+loc[2][0]+(img.shape[1]>>1),rect[1]+loc[2][1]+(img.shape[0]>>1))),fuse.reset())[1])(cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],img,cv2.TM_SQDIFF_NORMED)))
    def _compare(self,img,rect=(0,0,1920,1080),threshold=.05):return threshold>cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],img,cv2.TM_SQDIFF_NORMED))[0]and fuse.reset()
    def _select(self,img,rect=(0,0,1920,1080),threshold=.2):return(lambda x:numpy.argmin(x)if threshold>min(x)else None)([cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],i,cv2.TM_SQDIFF_NORMED))[0]for i in img])
    def _ocr(self,rect):return reduce(lambda x,y:x*10+y[1],(lambda contours,hierarchy:sorted(((pos,loc[2][0]//20)for pos,loc in((clip[0],cv2.minMaxLoc(cv2.matchTemplate(IMG.OCR,numpy.array([[[255*(cv2.pointPolygonTest(contours[i],(clip[0]+x,clip[1]+y),False)>=0and(hierarchy[0][i][2]==-1or cv2.pointPolygonTest(contours[hierarchy[0][i][2]],(clip[0]+x,clip[1]+y),False)<0))]*3for x in range(clip[2])]for y in range(clip[3])],dtype=numpy.uint8),cv2.TM_SQDIFF_NORMED)))for i,clip in((i,cv2.boundingRect(contours[i]))for i in range(len(contours))if hierarchy[0][i][3]==-1)if 8<clip[2]<20<clip[3]<27)if loc[0]<.3),key=lambda x:x[0]))(*cv2.findContours(cv2.threshold(cv2.cvtColor(self.im[rect[1]:rect[3],rect[0]:rect[2]],cv2.COLOR_BGR2GRAY),150,255,cv2.THRESH_BINARY)[1],cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)),0)
    def save(self,file=''):cv2.imwrite(time.strftime(file if file else'%Y-%m-%d_%H.%M.%S.jpg'),self.im)
    def show(self):
        cv2.imshow('Check Screenshot - Press S to save',cv2.resize(self.im,(0,0),fx=.4,fy=.4))
        if cv2.waitKey()==ord('s'):self.save()
        cv2.destroyAllWindows()
    def isAddFriend(self):return self._compare(IMG.END,(243,863,745,982))
    def isApEmpty(self):return self._compare(IMG.APEMPTY,(906,897,1017,967))
    def isBattleBegin(self):return self._compare(IMG.BATTLEBEGIN,(1673,959,1899,1069))
    def isBattleContinue(self):return self._compare(IMG.BATTLECONTINUE,(1072,805,1441,895))
    def isBattleDefeated(self):return self._compare(IMG.DEFEATED,(445,456,702,523))
    def isBattleFinished(self):return self._compare(IMG.BOUND,(112,250,454,313))or self._compare(IMG.BOUNDUP,(987,350,1468,594))
    def isChooseFriend(self):return self._compare(IMG.CHOOSEFRIEND,(1249,270,1387,650))
    def isCardSealed(self):return[any(self._compare(j,(43+386*i,667,350+386*i,845),.3)for j in(IMG.CHARASEALED,IMG.CARDSEALED))for i in range(5)]
    def isGacha(self):return self._compare(IMG.GACHA,(973,960,1312,1052))
    def isHouguReady(self):return[(numpy.mean(self.im[1019:1026,217+478*i:235+478*i])>55or numpy.mean(Check(.2).im[1019:1026,217+478*i:235+478*i])>55)and not any(self._compare(j,(470+346*i,258,773+346*i,387),.4)for j in(IMG.HOUGUSEALED,IMG.CHARASEALED,IMG.CARDSEALED))for i in range(3)]
    def isListEnd(self,pos):return any(self._compare(i,(pos[0]-30,pos[1]-20,pos[0]+30,pos[1]+1),.25)for i in(IMG.LISTEND,IMG.LISTNONE))
    def isMainInterface(self):return self._compare(IMG.MENU,(1630,950,1919,1079))
    def isNextJackpot(self):return self._compare(IMG.JACKPOT,(1556,336,1859,397))
    def isNoFriend(self):return self._compare(IMG.NOFRIEND,(369,545,1552,797),.1)
    def isSkillReady(self):return[[not self._compare(IMG.STILL,(54+476*i+132*j,897,83+480*i+141*j,927),.1)for j in range(3)]for i in range(3)]
    def isSpecialDrop(self):return self._compare(IMG.CLOSE,(8,18,102,102))
    def isTurnBegin(self):return self._compare(IMG.ATTACK,(1567,932,1835,1064))
    def getCardColor(self):return[[.8,1.,1.5][self._select((IMG.QUICK,IMG.ARTS,IMG.BUSTER),(120+386*i,806,196+386*i,871))]for i in range(5)]
    def getCardGroup(self):
        universe={0,1,2,3,4}
        result=[-1]*5
        index=0
        while universe:
            group=(lambda item:{item}|{i for i in universe if cv2.minMaxLoc(cv2.matchTemplate(self.im[660:737,160+386*item:225+386*item],self.im[690:707,170+386*i:215+386*i],cv2.TM_SQDIFF_NORMED))[0]<.01})(universe.pop())
            for i in group:result[i]=index
            index+=1
            universe-=group
        return result
    def getCardResist(self):return[{0:2.,1:.5}.get(self._select((IMG.WEAK,IMG.RESIST),(263+386*i,530,307+386*i,630)),1.)for i in range(5)]
    def getEnemyHP(self):return[self._ocr((150+375*i,61,332+375*i,97))for i in range(3)]
    def getHP(self):return[self._ocr((300+476*i,930,439+476*i,965))for i in range(3)]
    def getNP(self):return[self._ocr((330+476*i,983,411+476*i,1020))for i in range(3)]
    def getPortrait(self):return[self.im[640:740,195+480*i:296+480*i]for i in range(3)]
    @retryOnError()
    def getStage(self):return self._select((IMG.STAGE1,IMG.STAGE2,IMG.STAGE3),(1296,20,1342,56),.5)+1
    @retryOnError()
    def getStageTotal(self):return self._select((IMG.STAGETOTAL1,IMG.STAGETOTAL2,IMG.STAGETOTAL3),(1325,20,1372,56),.5)+1
    def getTeamIndex(self):return cv2.minMaxLoc(cv2.matchTemplate(self.im[58:92,768:1152],IMG.TEAMINDEX,cv2.TM_SQDIFF_NORMED))[2][0]//37+1
    def isEnemyDanger(self):raise NotImplementedError
    def getEnemyHPGauge(self):raise NotImplementedError
    def getEnemyNP(self):raise NotImplementedError
def gacha():
    while fuse.value<30:
        if Check().isGacha():base.perform('MK',(200,2700))
        base.press('\xDC')
def jackpot():
    while fuse.value<70:
        if Check().isNextJackpot():base.perform('0KK',(600,1800,0))
        for _ in range(40):base.press('2')
def mailFiltering():
    if not mailFilterImg.flush():return
    while not Check(1).isListEnd((1406,1079)):
        if not any(check(i[1],threshold=.016)for i in mailFilterImg.items()):base.swipe((400,900,400,300))
class Battle:
    skillInfo=[[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]]]
    houguInfo=[[1,1],[1,1],[1,1],[1,1],[1,1],[1,1]]
    dangerPos=[0,0,1]
    masterSkill=[[0,0,0],[0,0,0],[0,0,0,0]]
    def __init__(self):
        self.turn=0;
        self.stage=0
        self.stageTurn=0
        self.servant=[0,1,2]
        self.orderChange=[0,1,2,3,4,5]
    def __call__(self):
        while True:
            if Check(0,.3).isTurnBegin():
                self.turn+=1
                self.stage,self.stageTurn=(lambda x:[x,1+self.stageTurn*(self.stage==x)])(Check(.2).getStage())
                skill,newPortrait=check.isSkillReady(),check.getPortrait()
                check.getHP(),check.getNP(),check.getEnemyHP()
                if self.turn==1:self.stageTotal=check.getStageTotal()
                else:self.servant=(lambda m,p:[m+p.index(i)+1if i in p else self.servant[i]for i in range(3)])(max(self.servant),[i for i in range(3)if self.servant[i]<6and cv2.matchTemplate(newPortrait[i],portrait[i],cv2.TM_SQDIFF_NORMED)[0][0]>.04])
                if self.stageTurn==1and self.dangerPos[self.stage-1]:base.perform('\x69\x68\x67\x66\x65\x64'[self.dangerPos[self.stage-1]-1]+'\xDC',(250,500))
                portrait=newPortrait
                logger.info(f'Turn {self.turn} Stage {self.stage} StageTurn {self.stageTurn} {self.servant}')
                for i,j in((i,j)for i in range(3)if self.servant[i]<6for j in range(3)if skill[i][j]and self.skillInfo[self.orderChange[self.servant[i]]][j][0]and min(self.skillInfo[self.orderChange[self.servant[i]]][j][0],self.stageTotal)<<8|self.skillInfo[self.orderChange[self.servant[i]]][j][1]<=self.stage<<8|self.stageTurn):
                    base.perform(('ASD','FGH','JKL')[i][j],(300,))
                    if self.skillInfo[self.orderChange[self.servant[i]]][j][2]:base.perform('234'[self.skillInfo[self.orderChange[self.servant[i]]][j][2]-1],(300,))
                    control.sleep(2.3)
                    while not Check().isTurnBegin():pass
                for i in(i for i in range(3)if self.stage==min(self.masterSkill[i][0],self.stageTotal)and self.stageTurn==self.masterSkill[i][1]):
                    base.perform('Q'+'WER'[i],(300,300))
                    if self.masterSkill[i][2]:
                        if i==2and self.masterSkill[2][3]:
                            if self.masterSkill[2][2]-1not in self.servant or self.masterSkill[2][3]-1in self.servant:
                                base.perform('\xDC',(300,))
                                continue
                            base.perform(('TYUIOP'[self.servant.index(self.masterSkill[2][2]-1)],'TYUIOP'[self.masterSkill[2][3]-max(self.servant)+1],'Z'),(300,300,2600))
                            self.orderChange[self.masterSkill[2][2]-1],self.orderChange[self.masterSkill[2][3]-1]=self.orderChange[self.masterSkill[2][3]-1],self.orderChange[self.masterSkill[2][2]-1]
                            control.sleep(2.3)
                            while not Check().isTurnBegin():pass
                            portrait=Check(.5).getPortrait()
                            for j in(j for j in range(3)if self.skillInfo[self.masterSkill[2][3]-1][j][0]and min(self.skillInfo[self.masterSkill[2][3]-1][j][0],self.stageTotal)<<8|self.skillInfo[self.masterSkill[2][3]-1][j][1]<=self.stage<<8|self.stageTurn):
                                base.perform(('ASD','FGH','JKL')[self.servant.index(self.masterSkill[2][2]-1)][j],(300,))
                                if self.skillInfo[self.masterSkill[2][3]-1][j][2]:base.perform('234'[self.skillInfo[self.masterSkill[2][3]-1][j][2]-1],(300,))
                                control.sleep(2.3)
                                while not Check().isTurnBegin():pass
                            continue
                        base.perform('234'[self.masterSkill[i][2]-1],(300,))
                    control.sleep(2.3)
                    while not Check().isTurnBegin():pass
                base.perform(' ',(2000,))
                base.perform(self.selectCard(),(270,270,2270,1270,6000))
            elif check.isBattleFinished():
                logger.info('Battle Finished')
                return True
            elif check.isBattleDefeated():
                logger.warning('Battle Defeated')
                return False
    @DebugMeta.logit(logging.INFO)
    def selectCard(self):return''.join((lambda hougu,sealed,color,resist:['678'[i]for i in sorted((i for i in range(3)if hougu[i]),key=lambda x:-self.houguInfo[self.orderChange[self.servant[x]]][1])]+['12345'[i]for i in sorted(range(5),key=(lambda x:-color[x]*resist[x]*(not sealed[x])))]if any(hougu)else(lambda group:['12345'[i]for i in(lambda choice:choice+tuple({0,1,2,3,4}-set(choice)))(logger.debug('cardRank'+','.join(('  'if i%5else'\n')+f'({j}, {k:5.2f})'for i,(j,k)in enumerate(sorted([(card,(lambda colorChain,firstCardBonus:sum((firstCardBonus+[1.,1.2,1.4][i]*color[j])*resist[j]*(not sealed[j])for i,j in enumerate(card))+(not(sealed[card[0]]or sealed[card[1]]or sealed[card[2]]))*(5.*colorChain+(firstCardBonus+1.)*(3.5if colorChain else 2.)*(group[card[0]]==group[card[1]]==group[card[2]])*resist[card[0]]))(color[card[0]]==color[card[1]]==color[card[2]],.5*(color[card[0]]==1.5)))for card in permutations(range(5),3)],key=lambda x:-x[1]))))or max(permutations(range(5),3),key=lambda card:(lambda colorChain,firstCardBonus:sum((firstCardBonus+[1.,1.2,1.4][i]*color[j])*resist[j]*(not sealed[j])for i,j in enumerate(card))+(not(sealed[card[0]]or sealed[card[1]]or sealed[card[2]]))*(5.*colorChain+(firstCardBonus+1.)*(3.5if colorChain else 2.)*(group[card[0]]==group[card[1]]==group[card[2]])*resist[card[0]]))(color[card[0]]==color[card[1]]==color[card[2]],.5*(color[card[0]]==1.5))))])(check.getCardGroup()))([self.servant[i]<6and j and self.houguInfo[self.orderChange[self.servant[i]]][0]and self.stage>=min(self.houguInfo[self.orderChange[self.servant[i]]][0],self.stageTotal)for i,j in enumerate(Check().isHouguReady())],check.isCardSealed(),check.getCardColor(),check.getCardResist()))
class Main:
    teamIndex=0
    friendPos=0
    def __init__(self,appleTotal=0,appleKind=0,battleFunc=lambda:Battle()()):
        self.appleTotal=appleTotal
        self.appleKind=appleKind
        self.battleFunc=battleFunc
        self.appleCount=0
        self.battleCount=0
    def __call__(self):
        while True:
            while True:
                if Check(.3,.3).isMainInterface():
                    control.checkTerminateLater()
                    base.press('8')
                    if Check(.7,.3).isApEmpty()and self.eatApple():return
                    self.chooseFriend()
                    while not Check().isBattleBegin():pass
                    if self.teamIndex and check.getTeamIndex()!=self.teamIndex:base.perform('\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79'[self.teamIndex-1]+' ',(1000,400))
                    base.perform(' 8M',(800,800,10000))
                    break
                elif check.isBattleContinue():
                    try:control.checkTerminateLater()
                    except ScriptTerminate:
                        base.press('F')
                        raise
                    base.press('K')
                    if Check(.7,.3).isApEmpty()and self.eatApple():return
                    self.chooseFriend()
                    control.sleep(6)
                    break
                elif check.isAddFriend():base.press('X')
                elif check.isSpecialDrop():
                    control.checkSpecialDrop()
                    logger.warning('Special drop')
                    check.save('specialdrop_%Y-%m-%d_%H.%M.%S.jpg')
                    base.press('\x67')
                base.press(' ')
            self.battleCount+=1
            logger.info(f'Battle {self.battleCount}')
            if self.battleFunc():base.perform('        ',(200,200,200,200,200,200,200,200))
            else:
                control.checkDefeated()
                base.perform('BIK',(500,500,500))
    def eatApple(self):
        if self.appleCount==self.appleTotal:
            logger.info('Ap Empty')
            base.press('Z')
            return True
        self.appleCount+=1
        logger.info(f'Apple {self.appleCount}')
        base.perform('W4K8'[self.appleKind]+'L',(400,1200))
        return False
    def chooseFriend(self):
        refresh=False
        while not Check(.2).isChooseFriend():
            if check.isNoFriend():
                if refresh:control.sleep(10)
                base.perform('\xBAK',(500,1000))
                refresh=True
        if not friendImg.flush():return base.press('8')
        while True:
            timer=time.time()
            while True:
                for i in(i for i,j in friendImg.items()if check(j)):
                    Battle.skillInfo[self.friendPos],Battle.houguInfo[self.friendPos]=(lambda r:(lambda p:([[Battle.skillInfo[self.friendPos][i][j]if p[i*3+j]=='x'else int(p[i*3+j])for j in range(3)]for i in range(3)],[Battle.houguInfo[self.friendPos][i]if p[i+9]=='x'else int(p[i+9])for i in range(2)]))(r.group())if r else(Battle.skillInfo[self.friendPos],Battle.houguInfo[self.friendPos]))(re.search('[0-9x]{11}$',i))
                    return logger.info(f'Friend {i}')
                if check.isListEnd((1860,1064)):break
                base.swipe((800,900,800,300))
                Check(.4)
            if refresh:control.sleep(max(0,timer+10-time.time()))
            base.perform('\xBAK',(500,1000))
            refresh=True
            while not Check(.2).isChooseFriend():
                if check.isNoFriend():
                    control.sleep(10)
                    base.perform('\xBAK',(500,1000))
def userScript():
    # BX WCBA 极地用迦勒底制服
    while not Check(0,.2).isTurnBegin():pass
    #                                    A    D    F    2    G   H    2   J   2    K    L    2   Q   E   2     _   6   5    4
    base.perform('ADF2GH2J2KL2QE2 654',(3000,3000,350,3000,3000,350,3000,350,3000,3000,350,3000,300,350,3000,2400,350,350,10000))
    while not Check(0,.2).isBattleFinished():assert not check.isTurnBegin()
    return True
