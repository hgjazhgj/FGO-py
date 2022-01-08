import os,time,cv2,numpy
from functools import reduce,wraps
from fgoControl import control
from fgoFuse import fuse
from fgoLogging import getLogger,logMeta
logger=getLogger('Check')
IMG=type('IMG',(),{i[:-4].upper():cv2.imread(f'fgoImage/{i}')for i in os.listdir('fgoImage')if i[-4:]=='.png'})
class Check(metaclass=logMeta(logger)):
    # The accuracy of each API here is designed to be 100% at 1920x1080 resolution, if you find any mismatches, please submit an issue, with a screenshot saved via Check.cache.save() or fuse.save().
    cache=None
    device=None
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
    def startIter(iter):
        @wraps(iter)
        def wrapper(self,*args,**kwargs):
            ans=iter(self,*args,**kwargs)
            next(ans)
            return ans
        return wrapper
    def __init__(self,forwardLagency=.1,backwardLagency=0,blockFuse=False):
        control.sleep(forwardLagency)
        self.im=self.device.screenshot()
        self.time=time.time()
        Check.cache=self
        if not blockFuse:fuse.increase()
        control.sleep(backwardLagency)
    def _clip(self,rect):return self.im[rect[1]:rect[3],rect[0]:rect[2]]
    def _loc(self,img,rect=(0,0,1920,1080)):return cv2.minMaxLoc(cv2.matchTemplate(self._clip(rect),img,cv2.TM_SQDIFF_NORMED,mask=numpy.max(img,axis=2)>>1))
    def _compare(self,img,rect=(0,0,1920,1080),threshold=.05,blockFuse=False):return threshold>self._loc(img,rect)[0]and(blockFuse or fuse.reset(self))
    def _select(self,img,rect=(0,0,1920,1080),threshold=.2):return(lambda x:numpy.argmin(x)if threshold>min(x)else None)([self._loc(i,rect)[0]for i in img])
    def _ocr(self,rect):return reduce(lambda x,y:x*10+y[1],(lambda contours,hierarchy:sorted(((pos,loc[2][0]//20)for pos,loc in((clip[0],cv2.minMaxLoc(cv2.matchTemplate(IMG.OCR,numpy.array([[[255*(cv2.pointPolygonTest(contours[i],(clip[0]+x,clip[1]+y),False)>=0and(hierarchy[0][i][2]==-1or cv2.pointPolygonTest(contours[hierarchy[0][i][2]],(clip[0]+x,clip[1]+y),False)<0))]*3for x in range(clip[2])]for y in range(clip[3])],dtype=numpy.uint8),cv2.TM_SQDIFF_NORMED)))for i,clip in((i,cv2.boundingRect(contours[i]))for i in range(len(contours))if hierarchy[0][i][3]==-1)if 8<clip[2]<20<clip[3]<27)if loc[0]<.3),key=lambda x:x[0]))(*cv2.findContours(cv2.threshold(cv2.cvtColor(self._clip(rect),cv2.COLOR_BGR2GRAY),150,255,cv2.THRESH_BINARY)[1],cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)),0)
    @startIter
    def _iterMatch(self,rect,threshold=.05):
        img=self._clip(rect)
        check=yield None
        while True:
            tmp=check._clip(rect)
            check=yield threshold<cv2.matchTemplate(img,tmp,cv2.TM_SQDIFF_NORMED)[0][0]and fuse.reset(check)
            img=tmp
    @startIter
    def _iterChange(self,init):
        a=[init,(yield None)]
        p=0
        while True:
            a[p]=yield a[0]!=a[1]
            p^=1
    def _isListEnd(self,pos):return not self._compare(IMG.LISTBAR,(pos[0]-20,pos[1]-17,pos[0]+20,pos[1]+4),.25)
    def save(self,name='Capture'):cv2.imwrite(time.strftime(f'{name}_%Y-%m-%d_%H.%M.%S.png',time.localtime(self.time)),self.im)
    def show(self):
        cv2.imshow('Check Screenshot - Press S to save',cv2.resize(self.im,(0,0),fx=.4,fy=.4))
        if cv2.waitKey()==ord('s'):self.save()
        cv2.destroyAllWindows()
    def find(self,img,rect=(0,0,1920,1080),threshold=.02):return(lambda loc:((rect[0]+loc[2][0]+(img.shape[1]>>1),rect[1]+loc[2][1]+(img.shape[0]>>1)),fuse.reset(self))[0]if loc[0]<threshold else None)(self._loc(img,rect))
    def setupMailDone(self):Check._iterMailDone=self._iterMatch((303,156,378,186))
    def setupServantDead(self,friend=None):
        Check._iterServantFace=[self._iterMatch((195+480*i,640,296+480*i,740))for i in range(3)]
        Check._iterServantFriend=[self._iterChange(i)for i in(self.isServantFriend()if friend is None else friend)]
    def isAddFriend(self):return self._compare(IMG.END,(243,863,745,982))
    def isApEmpty(self):return self._compare(IMG.APEMPTY,(906,897,1017,967))
    def isBattleBegin(self):return self._compare(IMG.BATTLEBEGIN,(1639,951,1865,1061))
    def isBattleContinue(self):return self._compare(IMG.BATTLECONTINUE,(860,256,1060,308))
    def isBattleDefeated(self):return self._compare(IMG.DEFEATED,(905,151,1034,263))
    def isBattleFinished(self):return self._compare(IMG.DROPITEM,(165,46,396,113))
    def isChooseFriend(self):return self._compare(IMG.CHOOSEFRIEND,(1249,270,1387,650))
    def isCardSealed(self):return[any(self._compare(j,(43+386*i,667,350+386*i,845),.3)for j in(IMG.CHARASEALED,IMG.CARDSEALED))for i in range(5)]
    def isFriendListEnd(self):return self._isListEnd((1882,1064))
    def isGacha(self):return self._compare(IMG.GACHA,(973,960,1312,1052))
    def isHouguReady(self,that=None):return(lambda that:[not any(that._compare(j,(470+346*i,258,773+346*i,387),.4)for j in(IMG.HOUGUSEALED,IMG.CHARASEALED,IMG.CARDSEALED))and(numpy.mean(self.im[1019:1026,217+478*i:235+478*i])>55or numpy.mean(that.im[1019:1026,217+478*i:235+478*i])>55)for i in range(3)])(Check(.15)if that is None else that)
    def isMailDone(self):return self._iterMailDone.send(self)
    def isMainInterface(self):return self._compare(IMG.MENU,(1630,920,1919,1049))
    def isMailListEnd(self):return self._isListEnd((1406,1018))
    def isNetworkError(self):return self._compare(IMG.NETWORKERROR,(816,392,1085,518),blockFuse=True)
    def isNextJackpot(self):return self._compare(IMG.JACKPOT,(1245,347,1318,389))
    def isNoFriend(self):return self._compare(IMG.NOFRIEND,(369,545,411,587),.1)
    def isServantDead(self,friend=None):return[any((self._iterServantFace[i].send(self),self._iterServantFriend[i].send(j)))for i,j in enumerate(self.isServantFriend()if friend is None else friend)]
    def isServantFriend(self):return[self._compare(IMG.SUPPORT,(292+480*i,582,425+480*i,626))for i in range(3)]
    def isSkillReady(self):return[[not self._compare(IMG.STILL,(54+476*i+132*j,897,83+480*i+141*j,927),.1)for j in range(3)]for i in range(3)]
    def isSpecialDropRainbowBox(self):return self._compare(IMG.RAINBOW,(1436,3,1484,59))
    def isSpecialDropSuspended(self):return self._compare(IMG.CLOSE,(12,17,107,102))
    def isTurnBegin(self):return self._compare(IMG.ATTACK,(1567,932,1835,1064))
    def getCardColor(self):return[[.8,1.,1.1][self._select((IMG.QUICK,IMG.ARTS,IMG.BUSTER),(120+386*i,806,196+386*i,871))]for i in range(5)]
    def getCardGroup(self): # When your servant and the support one has the same command card portrait, getCardGroup will see them as in the same group, which is not true and hard to fix, because the support tag on a command card might be covered when there are many buff icons. This problem causes selectCard to not provide the best solve
        universe={0,1,2,3,4}
        result=[-1]*5
        index=0
        while universe:
            group=(lambda item:{item}|{i for i in universe if self._loc(self._clip((170+386*i,690,215+386*i,707)),(160+386*item,660,225+386*item,737))[0]<.025})(universe.pop())
            for i in group:result[i]=index
            index+=1
            universe-=group
        return result
    def getCardResist(self):return[{0:1.7,1:.6}.get(self._select((IMG.WEAK,IMG.RESIST),(263+386*i,530,307+386*i,630)),1.)for i in range(5)]
    def getCriticalRate(self):return[(lambda x:0.if x is None else(x+1)/10)(self._select((IMG.CRITICAL1,IMG.CRITICAL2,IMG.CRITICAL3,IMG.CRITICAL4,IMG.CRITICAL5,IMG.CRITICAL6,IMG.CRITICAL7,IMG.CRITICAL8,IMG.CRITICAL9,IMG.CRITICAL0),(114+386*i,526,169+386*i,607),.06))for i in range(5)]
    def getEnemyHP(self):return[self._ocr((150+375*i,61,332+375*i,97))for i in range(3)]
    def getHP(self):return[self._ocr((300+476*i,930,439+476*i,965))for i in range(3)]
    def getNP(self):return[self._ocr((330+476*i,983,411+476*i,1020))for i in range(3)]
    @retryOnError()
    def getStage(self):return self._select((IMG.STAGE1,IMG.STAGE2,IMG.STAGE3),(1326,20,1352,56),.5)+1
    @retryOnError()
    def getStageTotal(self):return self._select((IMG.STAGE1,IMG.STAGE2,IMG.STAGE3),(1369,20,1397,56),.5)+1
    def getTeamIndex(self):return self._loc(IMG.TEAMINDEX,(768,52,1152,92))[2][0]//37
    def getEnemyHPGauge(self):raise NotImplementedError
    def getEnemyNP(self):raise NotImplementedError
