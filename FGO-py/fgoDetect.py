import os,time,cv2,numpy,re,tqdm
from functools import reduce,wraps
from fgoConst import PACKAGE_TO_REGION
from fgoFuse import fuse
from fgoLogging import getLogger,logMeta
from fgoMetadata import servantData,servantImg,classImg,materialImg,chapterImg,mapImg,questImg
from fgoOcr import Ocr
from fgoSchedule import schedule
logger=getLogger('Detect')

IMG=type('IMG',(),{i[:-4].upper():(lambda x:(x[...,:3],x[...,3]))(cv2.imread(f'fgoImage/{i}',cv2.IMREAD_UNCHANGED))for i in os.listdir('fgoImage')if i.endswith('.png')})
for i in range(3):setattr(IMG,f'CHARGE{i}_SMALL',[cv2.resize(i,(0,0),fx=.77,fy=.77,interpolation=cv2.INTER_CUBIC)for i in getattr(IMG,f'CHARGE{i}')])
IMG.LISTBARINV=[i[::-1]for i in IMG.LISTBAR]
IMG_CN=type('IMG_CN',(IMG,),{i[:-4].upper():(lambda x:(x[...,:3],x[...,3]))(cv2.imread(f'fgoImage/cn/{i}',cv2.IMREAD_UNCHANGED))for i in os.listdir('fgoImage/cn')if i.endswith('.png')})
IMG_JP=type('IMG_JP',(IMG,),{i[:-4].upper():(lambda x:(x[...,:3],x[...,3]))(cv2.imread(f'fgoImage/jp/{i}',cv2.IMREAD_UNCHANGED))for i in os.listdir('fgoImage/jp')if i.endswith('.png')})
IMG_NA=type('IMG_NA',(IMG,),{i[:-4].upper():(lambda x:(x[...,:3],x[...,3]))(cv2.imread(f'fgoImage/na/{i}',cv2.IMREAD_UNCHANGED))for i in os.listdir('fgoImage/na')if i.endswith('.png')})
IMG_TW=type('IMG_TW',(IMG,),{i[:-4].upper():(lambda x:(x[...,:3],x[...,3]))(cv2.imread(f'fgoImage/tw/{i}',cv2.IMREAD_UNCHANGED))for i in os.listdir('fgoImage/tw')if i.endswith('.png')})
CLASS={100:classImg[1]}|{scale:[[cv2.resize(j,(0,0),fx=scale/100,fy=scale/100,interpolation=cv2.INTER_CUBIC)for j in i]for i in classImg[1]]for scale in(75,93,125)}
OCR=type('OCR',(),{i:Ocr(i)for i in tqdm.tqdm(['EN','ZHS','JA','ZHT'],leave=False)})
def coroutine(func):
    @wraps(func)
    def primer(*args,**kwargs):
        gen=func(*args,**kwargs)
        next(gen)
        return gen
    return primer
def validate(validator=lambda x:x):
    def wrapper(func):
        @wraps(func)
        def wrap(*args,**kwargs):
            assert validator(ans:=func(*args,**kwargs))
            return ans
        return wrap
    return wrapper
class XDetectBase(metaclass=logMeta(logger)):
    # The accuracy of each API here is designed to be 100% at 1280x720 resolution, if you find any mismatches, please submit an issue, with a screenshot saved via Detect.cache.save() or fuse.save().
    screenshot=None
    enemyGird=0
    tmpl=IMG
    ocr=OCR.EN
    def retryOnError(err=(TypeError,ValueError,IndexError,AssertionError)):
        def wrapper(func):
            @wraps(func)
            def wrap(self,*args,**kwargs):
                try:return func(self,*args,**kwargs)
                except err:pass
                logger.warning(f'Retry {getattr(func,"__qualname__",func)}({",".join(repr(i)for i in args)}{","if kwargs else""}{",".join("%s=%r"%i for i in kwargs.items())})')
                return wrap(type(self)(),*args,**kwargs)
            return wrap
        return wrapper
    def __init__(self):
        self.im=self.screenshot()
        self.time=time.time()
    def _crop(self,rect):return self.im[rect[1]:rect[3],rect[0]:rect[2]]
    def _loc(self,img,rect=(0,0,1280,720)):return cv2.minMaxLoc(cv2.matchTemplate(self._crop(rect),img[0],cv2.TM_SQDIFF_NORMED,mask=img[1]))
    def _compare(self,img,rect=(0,0,1280,720),threshold=.05):return threshold>self._loc(img,rect)[0]
    def _select(self,img,rect=(0,0,1280,720),threshold=.2):return(lambda x:numpy.argmin(x)if threshold>min(x)else None)([self._loc(i,rect)[0]for i in img])
    def _find(self,img,rect=(0,0,1280,720),threshold=.05):return(lambda loc:(rect[0]+loc[2][0]+(img[0].shape[1]>>1),rect[1]+loc[2][1]+(img[0].shape[0]>>1))if loc[0]<threshold else None)(self._loc(img,rect))
    def _ocrInt(self,rect):return OCR.EN.ocrInt(self._crop(rect))
    def _ocrText(self,rect):raise NotImplementedError
    def _count(self,img,rect=(0,0,1280,720),threshold=.1):return cv2.connectedComponents((cv2.matchTemplate(self._crop(rect),img[0],cv2.TM_SQDIFF_NORMED,mask=img[1])<threshold).astype(numpy.uint8))[0]-1
    @staticmethod
    def _stack(origin,increment,critic):return numpy.vstack((origin,increment[cv2.minMaxLoc(cv2.matchTemplate(increment,origin[-critic:],cv2.TM_SQDIFF_NORMED))[2][1]+critic:]))
    @coroutine
    def _asyncImageChange(self,rect,threshold=.05):
        img=self._crop(rect)
        detect=yield None
        while True:
            tmp=detect._crop(rect)
            detect=yield threshold<cv2.matchTemplate(img,tmp,cv2.TM_SQDIFF_NORMED)[0][0]
            img=tmp
    @coroutine
    def _asyncValueChange(self,init):
        a=[init,(yield None)]
        p=0
        while True:
            a[p]=yield a[0]!=a[1]
            p^=1
    def _isListBegin(self,pos):return(lambda x:x[0]>.1 or pos[1]>x[2][1]-5)(self._loc(self.tmpl.LISTBARINV,(pos[0]-19,0,pos[0]+19,720)))
    def _isListEnd(self,pos):return(lambda x:x[0]>.1 or pos[1]<x[2][1]+30)(self._loc(self.tmpl.LISTBAR,(pos[0]-19,0,pos[0]+19,720)))
    def inject(self,img):
        self.im=img
        self.time=time.time()
        return self
    def save(self,name='Screenshot',rect=(0,0,1280,720),appendTime=True):return cv2.imwrite(name:=time.strftime(f'{name}{f"_%Y-%m-%d_%H.%M.%S.{round(self.time*1000)%1000:03}"if appendTime else""}.png',time.localtime(self.time)),self._crop(rect),[cv2.IMWRITE_PNG_COMPRESSION,9])and name
    def show(self):
        cv2.imshow('Screenshot - Press S to save',cv2.resize(self.im,(0,0),fx=.6,fy=.6))
        if cv2.waitKey()==ord('s'):self.save()
        cv2.destroyAllWindows()
    def setupEnemyGird(self):
        XDetectBase.enemyGird=2 if any(self._select(CLASS[75],(110+200*i,1,173+200*i,48))is not None for i in range(3))else 1 if False else 0
        return XDetectBase.enemyGird
    def setupLottery(self):XDetectBase._watchLottery=self._asyncImageChange((983,4,1037,34))
    def setupMailDone(self):XDetectBase._watchMailDone=self._asyncImageChange((202,104,252,124))
    def setupServantDead(self,friend=None):
        XDetectBase._watchServantPortrait=[self._asyncImageChange((130+318*i,426,197+318*i,494))for i in range(3)]
        XDetectBase._watchServantFriend=[self._asyncValueChange(self.isServantFriend(i)if friend is None else friend[i])for i in range(3)]
    def setupSummonHistory(self):XDetectBase._summonHistory=cv2.threshold(cv2.cvtColor(self._crop((147,157,1105,547)),cv2.COLOR_BGR2GRAY),128,255,cv2.THRESH_BINARY)[1]
    def setupWeeklyMission(self):XDetectBase._weeklyMission=self._crop((603,250,1092,710))
    def isAddFriend(self):return self._compare(self.tmpl.ADDFRIEND,(161,574,499,656))
    def isApEmpty(self):return self._compare(self.tmpl.APEMPTY,(522,582,758,652))
    def isBattleContinue(self):return self._compare(self.tmpl.BATTLECONTINUE,(704,530,976,601))
    def isBattleDefeated(self):return self._compare(self.tmpl.DEFEATED,(603,100,690,176))
    def isBattleFinished(self):return self._compare(self.tmpl.DROPITEM,(110,30,264,76))
    def isBattleFormation(self):return self._compare(self.tmpl.BATTLEBEGIN,(1070,632,1270,710))
    def isChooseFriend(self):return any(self._compare(i,(1189,190,1210,243))for i in(self.tmpl.CHOOSEFRIEND,self.tmpl.CHOOSEFRIENDEX))
    def isCardSealed(self):return[self._compare(self.tmpl.CHARASEALED,(76+257*i,479,225+257*i,533),.3)or any(self._compare(j,(44+257*i,492,68+257*i,528),.14)for j in(self.tmpl.CARDSEALEDARTS,self.tmpl.CARDSEALEDQUICK,self.tmpl.CARDSEALEDBUSTER))for i in range(5)]
    def isFpContinue(self):return self._compare(self.tmpl.FPCONTINUE,(646,639,883,707))
    def isFpSummon(self):return self._compare(self.tmpl.FPSUMMON,(643,20,812,67))
    def isFriendListEnd(self):return self._isListEnd((1255,709))
    def isHouguReady(self,that=None):return(lambda that:[not any(that._compare(j,(313+231*i,172,515+231*i,258),.52)for j in(self.tmpl.HOUGUSEALED,self.tmpl.CHARASEALED))and(numpy.mean(self._crop((144+319*i,679,156+319*i,684)))>55 or numpy.mean(that._crop((144+319*i,679,156+319*i,684)))>55)for i in range(3)])((time.sleep(.15),type(self)())[1]if that is None else that)
    def isLotteryContinue(self):return self._watchLottery.send(self)
    def isMailDone(self):return self._watchMailDone.send(self)
    def isMainInterface(self):return self._compare(self.tmpl.MENU,(1104,613,1267,676))
    def isMailListEnd(self):return self._isListEnd((937,679))
    def isNetworkError(self):return self._compare(self.tmpl.NETWORKERROR,(703,529,974,597))
    def isNoFriend(self):return self._compare(self.tmpl.NOFRIEND,(245,362,274,392))
    def isQuestFreeContains(self,chapter):return self._compare((questImg[chapter],None),(1075,115,1111,575))
    def isQuestFreeFirst(self,chapter):return self._compare((questImg[chapter],None),(1075,115,1111,270))
    def isQuestListBegin(self):return self._isListBegin((1258,95))
    def isServantDead(self,pos,friend=None):return any((self._watchServantPortrait[pos].send(self),self._watchServantFriend[pos].send(self.isServantFriend(pos)if friend is None else friend)))
    def isServantFriend(self,pos):return self._compare(self.tmpl.SUPPORT,(187+318*pos,394,225+318*pos,412))
    def isSkillCastFailed(self):return self._compare(self.tmpl.SKILLERROR,(504,528,776,597))
    def isSkillNone(self):return self._compare(self.tmpl.CROSS,(1070,45,1105,79))or self._compare(self.tmpl.CROSS,(1093,164,1126,196))
    def isSkillReady(self,i,j):return not self._compare(self.tmpl.STILL,(35+318*i+88*j,598,55+318*i+88*j,618),.2)
    def isSpecialDropRainbowBox(self):return self._compare(self.tmpl.RAINBOW,(957,2,990,40),.1)
    def isSpecialDropSuspended(self):return self._compare(self.tmpl.CLOSE,(6,14,28,68))
    def isSummonHistoryListEnd(self):return self._isListEnd((1142,552))
    def isSynthesisBegin(self):return self._compare(self.tmpl.SYNTHESIS,(16,12,112,73))
    def isSynthesisFinished(self):return self._compare(self.tmpl.DECIDEDISABLED,(1035,625,1275,711))
    def isTerminal(self):return numpy.mean(self._crop((111,571,162,610)))<100
    def isTurnBegin(self):return self._compare(self.tmpl.ATTACK,(1155,635,1210,682))
    def isWeeklyMission(self):return numpy.min(cv2.matchTemplate(servantImg[1][1][3][0],cv2.resize(self._crop((296,117,421,210)),(0,0),fx=.555,fy=.555,interpolation=cv2.INTER_CUBIC),cv2.TM_SQDIFF_NORMED))<.1
    def isWeeklyMissionListEnd(self):return self._isListEnd((1261,614))
    @retryOnError()
    def getCardColor(self):return[+self._select((self.tmpl.ARTS,self.tmpl.QUICK,self.tmpl.BUSTER),(80+257*i,537,131+257*i,581))for i in range(5)]
    def getCardCriticalRate(self):return[(lambda x:0 if x is None else x+1)(self._select((self.tmpl.CRITICAL1,self.tmpl.CRITICAL2,self.tmpl.CRITICAL3,self.tmpl.CRITICAL4,self.tmpl.CRITICAL5,self.tmpl.CRITICAL6,self.tmpl.CRITICAL7,self.tmpl.CRITICAL8,self.tmpl.CRITICAL9,self.tmpl.CRITICAL0),(76+257*i,350,113+257*i,405),.06))for i in range(5)]
    def getCardGroup(self):
        universe={0,1,2,3,4}
        result=[-1]*5
        index=0
        while universe:
            group=(lambda item:{item}|{i for i in universe if self._loc((self._crop((113+257*i,460,144+257*i,472)),None),(106+257*item,440,150+257*item,492))[0]<.025})(universe.pop())
            for i in group:result[i]=index
            index+=1
            universe-=group
        return result
    def getCardResist(self):return[{0:1,1:2}.get(self._select((self.tmpl.WEAK,self.tmpl.RESIST),(180+257*i,318,226+257*i,417)if i<5 else(-695+232*i,54,-649+232*i,117)),0)for i in range(8)]
    def getCardServant(self,hint):return(lambda target:[(lambda img:min((numpy.min(cv2.matchTemplate(img,i[0],cv2.TM_SQDIFF_NORMED,mask=i[1])),no)for no,card in target for i in card)[1])(self._crop((76+257*i,431,184+257*i,498)))for i in range(5)])([(i,servantImg[i][0])for i in hint])
    def getEnemyHp(self,pos):
        if self.enemyGird==0:return 0 if pos>2 else self._ocrInt((100+250*pos,40,222+250*pos,65))
        if self.enemyGird==2:return self._ocrInt((190+pos%3*200-pos//3*100,28+pos//3*99,287+pos%3*200-pos//3*100,53+pos//3*99))
    def getEnemyNp(self,pos):
        if self.enemyGird==0:return(0,0)if pos>2 else(lambda count:(lambda c2:(c2,c2)if c2 else(lambda c0,c1:(c1,c0+c1))(count(self.tmpl.CHARGE0),count(self.tmpl.CHARGE1),))(count(self.tmpl.CHARGE2)))(lambda img:self._count(img,(160+250*pos,67,250+250*pos,88)))
        if self.enemyGird==2:return(lambda count:(lambda c2:(c2,c2)if c2 else(lambda c0,c1:(c1,c0+c1))(count(self.tmpl.CHARGE0_SMALL),count(self.tmpl.CHARGE1_SMALL),))(count(self.tmpl.CHARGE2_SMALL)))(lambda img:self._count(img,(231+pos%3*200-pos//3*100,49+pos//3*99,311+pos%3*200-pos//3*100,72+pos//3*99)))
    def getFieldServant(self,pos):return(lambda img,cls:min((numpy.min(cv2.matchTemplate(img,i[0],cv2.TM_SQDIFF_NORMED,mask=i[1])),no)for no,(_,portrait,_)in servantImg.items()if servantData[no][0]==cls[0]for i in portrait)[1]if cls else 0)(self._crop((120+318*pos,421,207+318*pos,490)),self.getFieldServantClassRank(pos))
    def getFieldServantClassRank(self,pos):return(lambda x:x if x is None else classImg[0][x])(self._select(CLASS[125],(13+318*pos,618,117+318*pos,702)))
    def getFieldServantHp(self,pos):return self._ocrInt((200+317*pos,620,293+317*pos,644))
    def getFieldServantNp(self,pos):return self._ocrInt((220+317*pos,655,271+317*pos,680))
    def getMaterial(self):return(lambda x:{materialImg[i][0]:x.count(i)for i in set(x)-{None}})([self._select(((i[1],None)for i in materialImg),(176+i%7*137,110+i//7*142,253+i%7*137,187+i//7*142),.02)for i in range(1,21)])
    def getSkillTargetCount(self):return(lambda x:numpy.bincount(numpy.diff(x))[1]+x[0])(cv2.dilate(numpy.max(cv2.threshold(numpy.max(self._crop((306,320,973,547)),axis=2),67,1,cv2.THRESH_BINARY)[1],axis=0).reshape(1,-1),numpy.ones((1,66),numpy.uint8)).ravel())if self._compare(self.tmpl.CROSS,(1083,139,1113,166))else 0
    @retryOnError()
    @validate()
    def getStage(self):return self._ocrInt((884,14,902,37))
    @retryOnError()
    @validate()
    def getStageTotal(self):return self._ocrInt((912,13,932,38))
    def getSummonHistory(self):XDetectBase._summonHistory=self._stack(XDetectBase._summonHistory,cv2.threshold(cv2.cvtColor(self._crop((147,157,1105,547)),cv2.COLOR_BGR2GRAY),128,255,cv2.THRESH_BINARY)[1],80)
    @classmethod
    def getSummonHistoryCount(cls):return cls.__new__(cls).inject(XDetectBase._summonHistory)._count((cls.tmpl.SUMMONHISTORY[0][...,0],cls.tmpl.SUMMONHISTORY[1]),(28,0,60,XDetectBase._summonHistory.shape[0]),.7)
    def getTeamIndex(self):return self._loc(self.tmpl.TEAMINDEX,(512,34,768,62))[2][0]//25
    # getTeam* series except getTeamIndex APIs are not used now
    def getTeamServantCard(self):return[reduce(lambda x,y:x<<1|y,(numpy.argmax(self.im[526,150+200*i+15*(i>2)+21*j])==0 for j in range(3)))for i in range(6)]
    def getTeamServantClassRank(self):return[(lambda x:x if x is None else classImg[0][x])(self._select(CLASS[100],(30+200*i+15*(i>2),133,115+200*i+15*(i>2),203)))for i in range(6)]
    def getWeeklyMission(self):XDetectBase._weeklyMission=self._stack(XDetectBase._weeklyMission,self._crop((603,250,1092,710)),157)
    def findChapter(self,chapter):return self._find((chapterImg[chapter],None),(640,90,1230,600),.016)
    def findFriend(self,img):return self._find(img,(13,166,1233,720),.04)
    def findMail(self,img):return self._find(img,(73,166,920,720),.016)
    def findMapCamera(self,chapter):return numpy.array(cv2.minMaxLoc(cv2.matchTemplate(mapImg[chapter],cv2.resize(self._crop((200,200,1080,520)),(0,0),fx=.3,fy=.3,interpolation=cv2.INTER_CUBIC),cv2.TM_SQDIFF_NORMED))[2])/.3+(440,160)
    @classmethod
    def saveSummonHistory(cls):return(lambda c:(lambda img:(c,cls.__new__(cls).inject(img).save(f'SummonHistory({c})',(0,0,*img.shape[::-1]))))(numpy.vstack((cv2.putText(numpy.zeros((36,XDetectBase._summonHistory.shape[1]),numpy.uint8),f'SummonHistory({c}) generated by FGO-py',(8,26),cv2.FONT_HERSHEY_DUPLEX,0.85,255,2,cv2.LINE_4),XDetectBase._summonHistory[:numpy.flatnonzero(numpy.max(XDetectBase._summonHistory,axis=1))[-1]+2]))))(cls.getSummonHistoryCount())
    def isGameAnnounce(self):raise NotImplementedError
    def isGameLaunch(self):raise NotImplementedError
    def isInCampaign(self):raise NotImplementedError
    def getEnemyHpGauge(self):raise NotImplementedError
    def getTeamMaster(self):raise NotImplementedError
    def getTeamServant(self):raise NotImplementedError
    def getTeamServantAtk(self):raise NotImplementedError
    def getTeamServantCost(self):raise NotImplementedError
    def getTeamServantHouguLv(self):raise NotImplementedError
    def getTeamServantRank(self):raise NotImplementedError
    def getTeamServantSkillLv(self):raise NotImplementedError
class XDetectCN(XDetectBase):
    tmpl=IMG_CN
    ocr=OCR.ZHS
    @classmethod
    def saveWeeklyMission(cls):
        result=[]
        mission=''
        for i in(i for i in cls.ocr.ocrArea(cls._weeklyMission)if'完成'not in i and'进行'not in i and'获得'not in i and'举办'not in i):
            if mission and i[0].isdigit():
                if'『'in mission and(count:=(lambda x:int(x[1])-int(x[0]))(i.split('/')if'/'in i else(i[:len(i)>>1],i[len(i)+1>>1:]))):result.append((re.findall('『(.*?)』',mission),'从者'not in mission,count))
                mission=''
            else:mission+=i
        return result
class XDetectJP(XDetectBase):
    tmpl=IMG_JP
    ocr=OCR.JA
    def isBattleContinue(self):return self._compare(self.tmpl.BATTLECONTINUE,(704,547,976,618))
    def getTeamIndex(self):return self._loc(self.tmpl.TEAMINDEX,(452,34,828,62))[2][0]//25
class XDetectNA(XDetectBase):
    tmpl=IMG_NA
    ocr=OCR.EN
    def isHouguReady(self,that=None):return(lambda that:[not any(that._compare(j,(313+231*i,194,515+231*i,270),.52)for j in(self.tmpl.HOUGUSEALED,self.tmpl.CHARASEALED))and(numpy.mean(self._crop((144+319*i,679,156+319*i,684)))>55 or numpy.mean(that._crop((144+319*i,679,156+319*i,684)))>55)for i in range(3)])((time.sleep(.15),type(self)())[1]if that is None else that)
    def isSkillReady(self,i,j):return not self._compare(self.tmpl.STILL,(41+318*i+88*j,607,74+318*i+88*j,614),.6)
class XDetectTW(XDetectBase):
    tmpl=IMG_TW
    ocr=OCR.ZHT
    def isHouguReady(self,that=None):return(lambda that:[not any(that._compare(j,(313+231*i,194,515+231*i,270),.52)for j in(self.tmpl.HOUGUSEALED,self.tmpl.CHARASEALED))and(numpy.mean(self._crop((144+319*i,679,156+319*i,684)))>55 or numpy.mean(that._crop((144+319*i,679,156+319*i,684)))>55)for i in range(3)])((time.sleep(.15),type(self)())[1]if that is None else that)
class DetectBase(XDetectBase):
    def __init__(self,anteLatency=.1,postLatency=0):
        schedule.sleep(anteLatency)
        super().__init__()
        fuse.increase()
        schedule.sleep(postLatency)
    def _compare(self,*args,**kwargs):return super()._compare(*args,**kwargs)and fuse.reset(self)
    def _find(self,*args,**kwargs):
        if(t:=super()._find(*args,**kwargs))is not None:fuse.reset(self)
        return t
    @coroutine
    def _asyncImageChange(self,*args,**kwargs):
        inner=super()._asyncImageChange(*args,**kwargs)
        p=yield None
        while True:
            if t:=inner.send(p):fuse.reset(self)
            p=yield t
class DetectCN(DetectBase,XDetectCN):pass # mro: DetectCN->DetectBase->XDetectCN->XDetectBase->object
class DetectJP(DetectBase,XDetectJP):pass
class DetectNA(DetectBase,XDetectNA):pass
class DetectTW(DetectBase,XDetectTW):pass
class XDetect:
    provider={'CN':XDetectCN,'JP':XDetectJP,'NA':XDetectNA,'TW':XDetectTW}
    region=''
    cache=None
    def __new__(cls,*args,**kwargs):
        if cls.region:cls.cache=cls.provider[cls.region](*args,**kwargs)
        else:cls.cache=XDetectBase(*args,**kwargs)
        return cls.cache
class Detect(XDetect):provider={'CN':DetectCN,'JP':DetectJP,'NA':DetectNA,'TW':DetectTW}
def setup(device):
    XDetectBase.screenshot=device.screenshot
    if not hasattr(device,'package'):return
    XDetect.region=PACKAGE_TO_REGION.get(device.package,'CN')
    logger.warning(f'Package: {device.package}, Region: {XDetect.region}')
