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
__version__='v6.1.0'
# 素に銀と鉄.礎に石と契約の大公.
import logging
# 降り立つ風には壁を.四方の門は閉じ,王冠より出で,王国に至る三叉路は循環せよ.
import os
# 満たせ.満たせ.満たせ.満たせ.満たせ.
import re
# 繰り返すつどに五度.ただ,満たされる刻を破却する.
import threading
# ――――告げる.
import time
# 汝の身は我が下に,我が命運は汝の剣に.
import cv2
# 聖杯の寄るべに従い,この意,この理に従うならば応えよ!
import numpy
# 誓いを此処に.
import win32con
# 我は常世総ての善と成る者,我は常世総ての悪を敷く者.
import win32file
# 汝三大の言霊を纏う七天,抑止の輪より来たれ,
from airtest.core.android.android import Android
# 天秤の守り手よ―――！
from airtest.core.android.constant import CAP_METHOD,ORI_METHOD,TOUCH_METHOD
(lambda logger:(logger.setLevel(logging.WARNING),logger)[-1])(logging.getLogger('airtest')).handlers[0].setFormatter(type('ColoredFormatter',(logging.Formatter,),{'__init__':lambda self,*args,**kwargs:logging.Formatter.__init__(self,*args,**kwargs),'format':lambda self,record:(setattr(record,'levelname','\033[{}m[{}]'.format({'WARNING':'33','INFO':'34','DEBUG':'37','CRITICAL':'35','ERROR':'31'}.get(record.levelname,'0'),record.levelname)),logging.Formatter.format(self,record))[-1]})('\033[32m[%(asctime)s]%(levelname)s\033[36m<%(name)s>\033[0m %(message)s','%H:%M:%S'))
(lambda logger:(logger.setLevel(logging.INFO),logger.addHandler((lambda handler:(handler.setFormatter(type('ColoredFormatter',(logging.Formatter,),{'__init__':lambda self,*args,**kwargs:logging.Formatter.__init__(self,*args,**kwargs),'format':lambda self,record:(setattr(record,'levelname','\033[{}m[{}]'.format({'WARNING':'33','INFO':'34','DEBUG':'37','CRITICAL':'35','ERROR':'31'}.get(record.levelname,'0'),record.levelname)),logging.Formatter.format(self,record))[-1]})('\033[32m[%(asctime)s]%(levelname)s\033[36m<%(name)s>\033[0m %(message)s','%H:%M:%S')),handler)[-1])(logging.StreamHandler()))))(logging.getLogger('fgo'))
logger=logging.getLogger('fgo.Func')
teamIndex=0
skillInfo=[[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]]]
houguInfo=[[1,1],[1,1],[1,1],[1,1],[1,1],[1,1]]
dangerPos=[0,0,1]
friendPos=4
masterSkill=[[0,0,0],[0,0,0],[0,0,0,0]]
IMG=(lambda t:([setattr(t,i[:-4].upper(),cv2.imread(f'fgoImage/{i}'))for i in os.listdir('fgoImage')if i.endswith('.png')],t)[-1])(type('IMG',(),{}))
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
            time.sleep(.1)
    def terminateLater(self,count=-1):self.__terminateLaterFlag=count
    def checkTerminateLater(self):
        if not self.__terminateLaterFlag:raise ScriptTerminate('Terminate Appointment Effected')
        self.__terminateLaterFlag-=1
    def sleep(self,x,part=.1):
        timer=time.time()+x-part
        while True:
            self.checkSuspend()
            self.checkTerminate()
            if time.time()>=timer:break
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
        self.log=[None]*self.logsize
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
        return self
    def reset(self):
        if self.__value>self.show:logger.debug(f'Fuse {self.__value}')
        self.__value=0
        if check is not self.log[(self.logptr-1)%self.logsize]:
            self.log[self.logptr]=check
            self.logptr=(self.logptr+1)%self.logsize
        return self
    def save(self):
        for i in(i for i in range(self.logsize)if self.log[(i+self.logptr)%self.logsize]):self.log[(i+self.logptr)%self.logsize].save(f'fuselog_%Y-%m-%d_%H.%M.%S_{i:02}.jpg')
        check.save('fuselog_%Y-%m-%d_%H.%M.%S.jpg')
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
            for i in range(len(self.msg)-1,-1,-1):
                if self.msg[i][1]!=file:continue
                if self.msg[i][0]==2:
                    self.msg[i][0]=3
                    return
                break
            self.msg.append([1,file])
        def onDeleted(file):
            for i in range(len(self.msg)-1,-1,-1):
                if self.msg[i][1]!=file:continue
                if self.msg[i][0]==1:
                    del self.msg[i]
                    return
                if self.msg[i][0]==3:
                    del self.msg[i]
                    break
                temp=self.msg[i-1][1]
                del self.msg[i-1:i+1]
                onDeleted(temp)
                return
            self.msg.append([2,file])
        def onUpdated(file):
            for i in range(len(self.msg)-1,-1,-1):
                if self.msg[i][1]!=file:continue
                if self.msg[i][0]==1or self.msg[i][0]==3:return
                if self.msg[i][0]==5:
                    temp=self.msg[i-1][1]
                    del self.msg[i-1:i+1]
                    onDeleted(temp)
                    onCreated(file)
                    return
                break
            self.msg.append([3,file])
        def onRenamedFrom(file):self.ren=file
        def onRenamedTo(file):
            for i in range(len(self.msg)-1,-1,-1):
                if self.msg[i][1]==file:break
                if self.msg[i][1]==self.ren:
                    if self.msg[i][0]==1:
                        del self.msg[i]
                        onCreated(file)
                        return
                    if self.msg[i][0]==3:
                        self.msg[i][0]=2
                        onCreated(file)
                        return
                    if self.msg[i][0]==5:
                        self.ren=self.msg[i-1][1]
                        del self.msg[i-1:i+1]
                        if self.ren==file:return
                    break
            self.msg+=[[4,self.ren],[5,file]]
        with self.lock:
            for i in x:{1:onCreated,2:onDeleted,3:onUpdated,4:onRenamedFrom,5:onRenamedTo}.get(i[0],lambda _:None)(i[1])
    def get(self):
        with self.lock:
            ans=self.msg
            self.msg=[]
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
friendImg=ImageListener('fgoImage/friend/')
mailFilterImg=ImageListener('fgoImage/mailfilter/')
class Base(Android):
    def __init__(self,serialno=None):
        self.lock=threading.Lock()
        if serialno is None:
            self.serialno=None
            return
        try:super().__init__(serialno,cap_method=CAP_METHOD.JAVACAP,ori_method=ORI_METHOD.ADB,touch_method=TOUCH_METHOD.MAXTOUCH)
        except:self.serialno=None
        else:
            self.render=[round(i)for i in self.get_render_resolution(True)]
            self.scale,self.border=(1080/self.render[3],(round(self.render[2]-self.render[3]*16/9)>>1,0))if self.render[2]*9>self.render[3]*16else(1920/self.render[2],(0,round(self.render[3]-self.render[2]*9/16)>>1))
            self.maxtouch.install_and_setup()
            self.key={c:[round(p[i]/self.scale+self.border[i]+self.render[i])for i in range(2)]for c,p in{
                '\x70':(790,74),'\x71':(828,74),'\x72':(866,74),'\x73':(903,74),'\x74':(940,74),'\x75':(978,74),'\x76':(1016,74),'\x77':(1053,74),'\x78':(1091,74),'\x79':(1128,74),# VK_F1..10
                '1':(277,640),'2':(598,640),'3':(974,640),'4':(1312,640),'5':(1651,640),'6':(646,304),'7':(976,304),'8':(1267,304),'0':(1819,367),
                'Q':(1800,475),'W':(1360,475),'E':(1493,475),'R':(1626,475),'T':(210,540),'Y':(510,540),'U':(810,540),'I':(1110,540),'O':(1410,540),'P':(1710,540),'\xDC':(1880,40),# \ VK_OEM_5
                'A':(109,860),'S':(244,860),'D':(385,860),'F':(582,860),'G':(724,860),'H':(861,860),'J':(1056,860),'K':(1201,860),'L':(1336,860),'\xBA':(1247,197),# ; VK_OEM_1
                'Z':(960,943),'X':(259,932),'B':(495,480),'N':(248,1041),'M':(1200,1000),
                ' ':(1846,1030),
                '\x64':(70,221),'\x65':(427,221),'\x66':(791,221),'\x67':(70,69),'\x68':(427,69),'\x69':(791,69),# VK-NUMPAD4..9
                }.items()}
    def touch(self,pos):
        with self.lock:super().touch([round(pos[i]/self.scale+self.border[i]+self.render[i])for i in range(2)])
    def swipe(self,rect):
        p1,p2=[numpy.array(self._touch_point_by_orientation([rect[i<<1|j]/self.scale+self.border[j]+self.render[j]for j in range(2)]))for i in range(2)]
        vd=p2-p1
        lvd=numpy.linalg.norm(vd)
        vd/=.2*self.scale*lvd
        vx=numpy.array([0.,0.])
        def send(method,pos):self.maxtouch.safe_send(' '.join((method,'0',*[str(i)for i in self.maxtouch.transform_xy(*pos)],'50\nc\n')))
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
            self.maxtouch.safe_send('u 0\nc\n')
            time.sleep(.02)
    def press(self,key):
        with self.lock:super().touch(self.key[key])
    def perform(self,pos,wait):[(self.press(i),control.sleep(j*.001))for i,j in zip(pos,wait)]
    def screenshot(self):return cv2.resize(super().snapshot()[self.render[1]+self.border[1]:self.render[1]+self.render[3]-self.border[1],self.render[0]+self.border[0]:self.render[0]+self.render[2]-self.border[0]],(1920,1080),interpolation=cv2.INTER_CUBIC)
base=Base()
check=None
class Check:
    def __init__(self,forwordLagency=.01,backwordLagency=0):
        control.sleep(forwordLagency)
        self.im=base.screenshot()
        global check
        check=self
        fuse.increase()
        control.sleep(backwordLagency)
    def compare(self,img,rect=(0,0,1920,1080),threshold=.05):return threshold>cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],img,cv2.TM_SQDIFF_NORMED))[0]and fuse.reset()
    def select(self,img,rect=(0,0,1920,1080),threshold=.4):return(lambda x:numpy.argmin(x)if not logger.debug(f'Select from {x}')and threshold>min(x)else None)([cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],i,cv2.TM_SQDIFF_NORMED))[0]for i in img])
    def tap(self,img,rect=(0,0,1920,1080),threshold=.05):return(lambda loc:loc[0]<threshold and(base.touch((rect[0]+loc[2][0]+(img.shape[1]>>1),rect[1]+loc[2][1]+(img.shape[0]>>1))),fuse.reset())[1])(cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],img,cv2.TM_SQDIFF_NORMED)))
    def save(self,name=''):
        cv2.imwrite(time.strftime(name if name else'%Y-%m-%d_%H.%M.%S.jpg',time.localtime()),self.im)
        return self
    def show(self):
        cv2.imshow('Check Screenshot - Press S to save',cv2.resize(self.im,(0,0),fx=.4,fy=.4))
        if cv2.waitKey()==ord('s'):self.save()
        cv2.destroyAllWindows()
        return self
    def isAddFriend(self):return self.compare(IMG.END,(243,863,745,982))
    def isApEmpty(self):return self.compare(IMG.APEMPTY,(906,897,1017,967))
    def isBattleBegin(self):return self.compare(IMG.BATTLEBEGIN,(1673,959,1899,1069))
    def isBattleContinue(self):return self.compare(IMG.BATTLECONTINUE,(1072,805,1441,895))
    def isBattleDefeated(self):return self.compare(IMG.DEFEATED,(445,456,702,523))
    def isBattleFinished(self):return self.compare(IMG.BOUND,(112,250,454,313))or self.compare(IMG.BOUNDUP,(987,350,1468,594))
    def isChooseFriend(self):return self.compare(IMG.CHOOSEFRIEND,(1249,324,1387,382))
    def isGacha(self):return self.compare(IMG.GACHA,(973,960,1312,1052))
    def isHouguReady(self):return[not any(self.compare(j,(470+346*i,258,768+346*i,387),.4)for j in(IMG.HOUGUSEALED,IMG.CARDSEALED))and(numpy.mean(self.im[1019:1026,217+478*i:235+478*i])>55or numpy.mean(Check(.2).im[1019:1026,217+478*i:235+478*i])>55)for i in range(3)]
    def isListEnd(self,pos):return any(self.compare(i,(pos[0]-30,pos[1]-20,pos[0]+30,pos[1]+1),.25)for i in(IMG.LISTEND,IMG.LISTNONE))
    def isMainInterface(self):return self.compare(IMG.MENU,(1630,950,1919,1079))
    def isNextJackpot(self):return self.compare(IMG.JACKPOT,(1556,336,1859,397))
    def isNoFriend(self):return self.compare(IMG.NOFRIEND,(369,545,1552,797),.1)
    def isSkillReady(self):return[[not self.compare(IMG.STILL,(54+476*i+132*j,897,83+480*i+141*j,927),.1)for j in range(3)]for i in range(3)]
    def isSpecialDrop(self):return self.compare(IMG.CLOSE,(8,18,102,102))
    def isTurnBegin(self):return self.compare(IMG.ATTACK,(1567,932,1835,1064))
    def getABQ(self):return[-1if self.compare(IMG.CARDSEALED,(43+386*i,667,345+386*i,845),.3)else self.select((IMG.QUICK,IMG.ARTS,IMG.BUSTER),(120+386*i,811,196+386*i,866))for i in range(5)]
    def getTeamIndex(self):return cv2.minMaxLoc(cv2.matchTemplate(self.im[58:92,768:1152],IMG.TEAMINDEX,cv2.TM_SQDIFF_NORMED))[2][0]//37+1
    def getPortrait(self):return[self.im[640:740,195+480*i:296+480*i]for i in range(3)]
    def retryOnError(interval=.1,err=TypeError):
        def wrapper(func):
            from functools import wraps
            @wraps(func)
            def wrap(self,*args,**kwargs):
                try:
                    if(ans:=func(self,*args,**kwargs))is not None:return ans
                except err:pass
                logger.warning(f'Retry {func.__qualname__}({",".join(repr(i)for i in args)}{","if kwargs else""}{",".join((i+"="+repr(j))for i,j in kwargs.items())})')
                return wrap(Check(interval),*args,**kwargs)
            return wrap
        return wrapper
    @retryOnError()
    def getStage(self):return self.select((IMG.STAGE1,IMG.STAGE2,IMG.STAGE3),(1296,20,1342,56))+1
    @retryOnError()
    def getStageTotal(self):return self.select((IMG.STAGETOTAL1,IMG.STAGETOTAL2,IMG.STAGETOTAL3),(1325,20,1372,56))+1
def gacha():
    while fuse.value<30:
        if Check(.1).isGacha():base.perform('MK',(200,2700))
        base.press('\xDC')
def jackpot():
    while fuse.value<70:
        if Check().isNextJackpot():base.perform('0JJ',(600,1800,0))
        for _ in range(40):base.press('2')
def mailFiltering():
    mailFilterImg.flush()
    while not Check(1).isListEnd((1406,1079)):
        if not any(check.tap(i[1],threshold=.016)for i in mailFilterImg.items()):base.swipe((400,900,400,300))
def battle():
    turn,stage,stageTurn,servant=0,0,0,[0,1,2]
    while True:
        if Check(0,.1).isTurnBegin():
            turn+=1
            stage,stageTurn=(lambda x:[x,stageTurn+1if stage==x else 1])(Check(.5).getStage())
            skill,newPortrait=check.isSkillReady(),check.getPortrait()
            if turn==1:stageTotal=check.getStageTotal()
            else:servant=(lambda m,p:[m+p.index(i)+1if i in p else servant[i]for i in range(3)])(max(servant),[i for i in range(3)if servant[i]<6and cv2.matchTemplate(newPortrait[i],portrait[i],cv2.TM_SQDIFF_NORMED)[0][0]>.04])
            if stageTurn==1and dangerPos[stage-1]:base.perform('\x69\x68\x67\x66\x65\x64'[dangerPos[stage-1]-1]+'\xDC',(250,500))
            portrait=newPortrait
            logger.info(f'{turn} {stage} {stageTurn} {servant}')
            for i,j in((i,j)for i in range(3)if servant[i]<6for j in range(3)if skill[i][j]and skillInfo[servant[i]][j][0]and min(skillInfo[servant[i]][j][0],stageTotal)<<8|skillInfo[servant[i]][j][1]<=stage<<8|stageTurn):
                base.perform(('ASD','FGH','JKL')[i][j],(300,))
                if skillInfo[servant[i]][j][2]:base.perform('234'[skillInfo[servant[i]][j][2]-1],(300,))
                control.sleep(2.3)
                while not Check().isTurnBegin():pass
            for i in(i for i in range(3)if stage==min(masterSkill[i][0],stageTotal)and stageTurn==masterSkill[i][1]):
                base.perform('Q'+'WER'[i],(300,300))
                if masterSkill[i][2]:base.perform('234'[masterSkill[i][2]-1],(300,))
                control.sleep(2.3)
                while not Check().isTurnBegin():pass
            base.perform(' ',(2350,))
            base.perform((lambda c,h:['678'[i]for i in sorted((i for i in range(3)if h[i]),key=lambda x:-houguInfo[servant[x]][1])]+['12345'[i]for i in sorted(range(5),key=(lambda x:-c[x])if any(h)else(lambda x:-3if c[x]!=-1and c.count(c[x])>=3else-c[x]))])(Check().getABQ(),[servant[i]<6and j and houguInfo[servant[i]][0]and stage>=min(houguInfo[servant[i]][0],stageTotal)for i,j in zip(range(3),check.isHouguReady())]),(270,270,2270,1270,6000))
        elif check.isBattleFinished():
            logger.info('Battle Finished')
            return True
        elif check.isBattleDefeated():
            control.checkDefeated()
            logger.warning('Battle Defeated')
            return False
def main(appleTotal=0,appleKind=0,battleFunc=battle):
    def eatApple():
        if Check(.7,.3).isApEmpty():
            nonlocal appleCount,appleTotal
            if appleCount==appleTotal:
                logger.info('Ap Empty')
                base.press('Z')
                return True
            else:
                appleCount+=1
                logger.info(f'Apple {appleCount}')
                base.perform('W4K8'[appleKind]+'L',(400,1200))
                return False
    def chooseFriend():
        refresh=False
        while not Check(.2).isChooseFriend():
            if check.isNoFriend():
                if refresh:control.sleep(10)
                base.perform('\xBAJ',(500,1000))
                refresh=True
        friendImg.flush()
        if not friendImg:
            time.sleep(.2)
            return base.press('8')
        while True:
            timer=time.time()
            while True:
                for i in(i[0]for i in friendImg.items()if check.tap(i[1])):
                    skillInfo[friendPos],houguInfo[friendPos]=(lambda r:(lambda p:([[skillInfo[friendPos][i][j]if p[i*3+j]=='x'else int(p[i*3+j])for j in range(3)]for i in range(3)],[houguInfo[friendPos][i]if p[i+9]=='x'else int(p[i+9])for i in range(2)]))(r.group())if r else(skillInfo[friendPos],houguInfo[friendPos]))(re.search('[0-9x]{11}$',i))
                    return logger.info(f'Friend {i}')
                if check.isListEnd((1860,1064)):break
                base.swipe((800,900,800,300))
                Check(.3)
            if refresh:control.sleep(max(0,timer+10-time.time()))
            base.perform('\xBAJ',(500,1000))
            refresh=True
            while not Check(.2).isChooseFriend():
                if check.isNoFriend():
                    control.sleep(10)
                    base.perform('\xBAJ',(500,1000))
    appleCount,battleCount=0,0
    while True:
        while True:
            if Check(.3,.3).isMainInterface():
                control.checkTerminateLater()
                base.press('8')
                if eatApple():return
                chooseFriend()
                while not Check(.1).isBattleBegin():pass
                if teamIndex and check.getTeamIndex()!=teamIndex:base.perform('\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79'[teamIndex-1]+' ',(1000,400))
                base.perform(' 8M',(800,800,10000))
                break
            elif check.isBattleContinue():
                try:control.checkTerminateLater()
                except ScriptTerminate as e:
                    base.press('F')
                    raise e
                base.press('K')
                if eatApple():return
                chooseFriend()
                break
            elif check.isAddFriend():base.press('X')
            elif check.isSpecialDrop():
                control.checkSpecialDrop()
                logger.warning('Special drop')
                check.save('specialdrop_%Y-%m-%d_%H.%M.%S.jpg')
                base.press('\x67')
            base.press(' ')
        battleCount+=1
        logger.info(f'Battle {battleCount}')
        base.perform('        ',(200,200,200,200,200,200,200,200))if battleFunc()else base.perform('BIJ',(500,500,500))
def userScript():
    # BX WCBA 极地用迦勒底制服
    while not Check(0,.2).isTurnBegin():pass
    #                                    A    D    F    2    G   H    2   J   2    K    L    2   Q   E   2     _   6   5    4
    base.perform('ADF2GH2J2KL2QE2 654',(3000,3000,350,3000,3000,350,3000,350,3000,3000,350,3000,300,350,3000,2400,350,350,10000))
    while not Check(0,.2).isBattleFinished():assert not check.isTurnBegin()
    return True
