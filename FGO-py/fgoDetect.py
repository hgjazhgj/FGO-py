import os,time,cv2,numpy,tqdm
from functools import reduce,wraps
from fgoSchedule import schedule
from fgoFuse import fuse
from fgoLogging import getLogger,logMeta,logit
from fgoMetadata import servantData,servantImg
logger=getLogger('Detect')

IMG=type('IMG',(),{i[:-4].upper():(lambda x:(x[...,:3],x[...,3]))(cv2.imread(f'fgoImage/{i}',cv2.IMREAD_UNCHANGED))for i in os.listdir('fgoImage')if i.endswith('.png')})
for i in range(3):setattr(IMG,f'CHARGE{i}_SMALL',[cv2.resize(i,(0,0),fx=.77,fy=.77,interpolation=cv2.INTER_CUBIC)for i in getattr(IMG,f'CHARGE{i}')])
CLASS={100:[(lambda x:(x[...,:3],x[...,3]))(cv2.imread(f'fgoImage/class/{i}{j}.png',cv2.IMREAD_UNCHANGED))for i in['shielder','saber','archer','lancer','rider','caster','assassin','berserker','ruler','avenger','alterego','mooncancer','foreigner','pretender']for j in range(3)]}
for scale in [75,93,125]:CLASS[scale]=[[cv2.resize(j,(0,0),fx=scale/100,fy=scale/100,interpolation=cv2.INTER_CUBIC)for j in i]for i in CLASS[100]]
MATERIAL=[(i[:-4],cv2.imread(f'fgoImage/material/{i}'))for i in os.listdir('fgoImage/material')if i.endswith('.png')]
def coroutine(func):
    @wraps(func)
    def primer(*args,**kwargs):
        gen=func(*args,**kwargs)
        next(gen)
        return gen
    return primer
def validateIterable(iterable,validator):
    if hasattr(iterable,'__iter__'):return all(validateIterable(i,validator)for i in iterable)
    return validator(iterable)
def notNone(func):
    @wraps(func)
    def wrap(*args,**kwargs):
        assert validateIterable(ans:=func(*args,**kwargs),lambda x:x is not None)
        return ans
    return wrap
class XDetect(metaclass=logMeta(logger)):
    # The accuracy of each API here is designed to be 100% at 1280x720 resolution, if you find any mismatches, please submit an issue, with a screenshot saved via Detect.cache.save() or fuse.save().
    cache=None
    screenshot=None
    enemyGird=0
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
        XDetect.cache=self
    def _crop(self,rect):
        # cv2.imwrite(time.strftime(f'fgoTemp/Crop_%Y-%m-%d_%H.%M.%S_{rect}.png',time.localtime(self.time)),self.im[rect[1]+2:rect[3]-2,rect[0]+2:rect[2]-2],[cv2.IMWRITE_PNG_COMPRESSION,9])
        return self.im[rect[1]:rect[3],rect[0]:rect[2]]
    # @logit(logger)
    def _loc(self,img,rect=(0,0,1280,720)):return cv2.minMaxLoc(cv2.matchTemplate(self._crop(rect),img[0],cv2.TM_SQDIFF_NORMED,mask=img[1]))
    def _compare(self,img,rect=(0,0,1280,720),threshold=.05):return threshold>self._loc(img,rect)[0]
    def _select(self,img,rect=(0,0,1280,720),threshold=.2):return(lambda x:numpy.argmin(x)if threshold>min(x)else None)([self._loc(i,rect)[0]for i in img])
    def _find(self,img,rect=(0,0,1280,720),threshold=.05):return(lambda loc:(rect[0]+loc[2][0]+(img[0].shape[1]>>1),rect[1]+loc[2][1]+(img[0].shape[0]>>1))if loc[0]<threshold else None)(self._loc(img,rect))
    def _ocr(self,rect,scale=1.):return reduce(lambda x,y:x*10+y[1],(lambda contours,hierarchy:sorted(((pos,loc[2][0]//20)for pos,loc in((clip[0],cv2.minMaxLoc(cv2.matchTemplate(IMG.OCR[0],numpy.array([[[255*(cv2.pointPolygonTest(contours[i],(clip[0]+x,clip[1]+y),False)>=0 and(hierarchy[0][i][2]==-1 or cv2.pointPolygonTest(contours[hierarchy[0][i][2]],(clip[0]+x,clip[1]+y),False)<0))]*3 for x in range(clip[2])]for y in range(clip[3])],dtype=numpy.uint8),cv2.TM_SQDIFF_NORMED)))for i,clip in((i,cv2.boundingRect(contours[i]))for i in range(len(contours))if hierarchy[0][i][3]==-1)if 8<clip[2]<20<clip[3]<27)if loc[0]<.3),key=lambda x:x[0]))(*cv2.findContours(cv2.threshold(cv2.resize(cv2.cvtColor(self._crop(rect),cv2.COLOR_BGR2GRAY),(0,0),fx=1.5/scale,fy=1.5/scale,interpolation=cv2.INTER_CUBIC),150,255,cv2.THRESH_BINARY)[1],cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)),0)
    def _count(self,img,rect=(0,0,1280,720),threshold=.1):return cv2.connectedComponents((cv2.matchTemplate(self._crop(rect),img[0],cv2.TM_SQDIFF_NORMED,mask=img[1])<threshold).astype(numpy.uint8))[0]-1
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
    def _isListEnd(self,pos):return(lambda x:.1<x[0]or pos[1]<x[2][1]+30)(self._loc(IMG.LISTBAR,(pos[0]-19,0,pos[0]+19,720)))
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
        XDetect.enemyGird=2 if any(self._select(CLASS[75],(110+200*i,1,173+200*i,48))is not None for i in range(3))else 1 if False else 0
        return XDetect.enemyGird
    def setupGachaHistory(self):XDetect._gachaHistory=cv2.threshold(cv2.cvtColor(self._crop((147,157,1105,547)),cv2.COLOR_BGR2GRAY),128,255,cv2.THRESH_BINARY)[1]
    def setupLottery(self):XDetect._watchLottery=self._asyncImageChange((960,4,1010,32))
    def setupMailDone(self):XDetect._watchMailDone=self._asyncImageChange((202,104,252,124))
    def setupServantDead(self,friend=None):
        XDetect._watchServantPortrait=[self._asyncImageChange((130+318*i,426,197+318*i,494))for i in range(3)]
        XDetect._watchServantFriend=[self._asyncValueChange(self.isServantFriend(i)if friend is None else friend[i])for i in range(3)]
    def isAddFriend(self):return self._compare(IMG.END,(162,575,497,655))
    def isApEmpty(self):return self._compare(IMG.APEMPTY,(604,598,678,645))
    def isBattleBegin(self):return self._compare(IMG.BATTLEBEGIN,(1092,634,1244,708))
    def isBattleContinue(self):return self._compare(IMG.BATTLECONTINUE,(764,546,916,586))
    def isBattleDefeated(self):return self._compare(IMG.DEFEATED,(603,100,690,176))
    def isBattleFinished(self):return self._compare(IMG.DROPITEM,(110,30,264,76))
    def isChooseFriend(self):return self._compare(IMG.CHOOSEFRIEND,(832,180,925,434))
    def isCardSealed(self):return[any(self._compare(j,(28+257*i,444,234+257*i,564),.3)for j in(IMG.CHARASEALED,IMG.CARDSEALED))for i in range(5)]
    def isFriendListEnd(self):return self._isListEnd((1255,709))
    def isGacha(self):return self._compare(IMG.GACHA,(648,640,875,702))
    def isGachaHistoryListEnd(self):return self._isListEnd((1142,552))
    def isHouguReady(self,that=None):return(lambda that:[not any(that._compare(j,(313+231*i,172,515+231*i,258),.52)for j in(IMG.HOUGUSEALED,IMG.CHARASEALED,IMG.CARDSEALED))and(numpy.mean(self._crop((144+319*i,679,156+319*i,684)))>55 or numpy.mean(that._crop((144+319*i,679,156+319*i,684)))>55)for i in range(3)])((time.sleep(.15),type(self)())[1]if that is None else that)
    def isLotteryContinue(self):return self._watchLottery.send(self)
    def isMailDone(self):return self._watchMailDone.send(self)
    def isMainInterface(self):return self._compare(IMG.MENU,(1086,613,1280,700))
    def isMailListEnd(self):return self._isListEnd((937,679))
    def isNetworkError(self):return self._compare(IMG.NETWORKERROR,(798,544,879,584))
    def isNoFriend(self):return self._compare(IMG.NOFRIEND,(245,362,274,392),.15)
    def isServantDead(self,pos,friend=None):return any((self._watchServantPortrait[pos].send(self),self._watchServantFriend[pos].send(self.isServantFriend(pos)if friend is None else friend)))
    def isServantFriend(self,pos):return self._compare(IMG.SUPPORT,(194+318*pos,388,284+318*pos,418))
    def isSkillCastFailed(self):return self._compare(IMG.SKILLERROR,(595,539,684,586))
    def isSkillNone(self):return self._compare(IMG.CROSS,(1070,45,1105,79))or self._compare(IMG.CROSS,(1093,164,1126,196))
    def isSkillReady(self,i,j):return not self._compare(IMG.STILL,(35+318*i+88*j,598,55+318*i+88*j,618),.2)
    def isSpecialDropRainbowBox(self):return self._compare(IMG.RAINBOW,(957,2,990,40),.1)
    def isSpecialDropSuspended(self):return self._compare(IMG.CLOSE,(8,11,68,68))
    def isSynthesisBegin(self):return self._compare(IMG.SYNTHESIS,(16,12,150,73))
    def isSynthesisFinished(self):return self._compare(IMG.DECIDEDISABLED,(1096,645,1207,702))
    def isTurnBegin(self):return self._compare(IMG.ATTACK,(1064,621,1224,710))
    @retryOnError()
    def getCardColor(self):return[+self._select((IMG.ARTS,IMG.QUICK,IMG.BUSTER),(80+257*i,537,131+257*i,581))for i in range(5)]
    def getCardCriticalRate(self):return[(lambda x:0 if x is None else x+1)(self._select((IMG.CRITICAL1,IMG.CRITICAL2,IMG.CRITICAL3,IMG.CRITICAL4,IMG.CRITICAL5,IMG.CRITICAL6,IMG.CRITICAL7,IMG.CRITICAL8,IMG.CRITICAL9,IMG.CRITICAL0),(76+257*i,350,113+257*i,405),.06))for i in range(5)]
    def getCardGroup(self): # When your servant and the support one has the same command card portrait, getCardGroup will see them as in the same group, which is not true and hard to fix, because the support tag on a command card might be covered when there are many buff icons. This problem causes selectCard to not provide the best solve
        universe={0,1,2,3,4}
        result=[-1]*5
        index=0
        while universe:
            group=(lambda item:{item}|{i for i in universe if self._loc((self._crop((113+257*i,460,144+257*i,472)),None),(106+257*item,440,150+257*item,492))[0]<.025})(universe.pop())
            for i in group:result[i]=index
            index+=1
            universe-=group
        return result
    def getCardResist(self):return[{0:1,1:2}.get(self._select((IMG.WEAK,IMG.RESIST),(175+257*i,353,205+257*i,420)),0)for i in range(5)]
    def getEnemyHp(self,pos):
        if self.enemyGird==0:return 0 if pos>2 else self._ocr((100+250*pos,40,222+250*pos,65))
        if self.enemyGird==2:return self._ocr((190+pos%3*200-pos//3*100,28+pos//3*99,287+pos%3*200-pos//3*100,53+pos//3*99),scale=.77)
    def getEnemyNp(self,pos):
        if self.enemyGird==0:return(0,0)if pos>2 else(lambda count:(lambda c2:(c2,c2)if c2 else(lambda c0,c1:(c1,c0+c1))(count(IMG.CHARGE0),count(IMG.CHARGE1),))(count(IMG.CHARGE2)))(lambda img:self._count(img,(160+250*pos,67,250+250*pos,88)))
        if self.enemyGird==2:return(lambda count:(lambda c2:(c2,c2)if c2 else(lambda c0,c1:(c1,c0+c1))(count(IMG.CHARGE0_SMALL),count(IMG.CHARGE1_SMALL),))(count(IMG.CHARGE2_SMALL)))(lambda img:self._count(img,(231+pos%3*200-pos//3*100,49+pos//3*99,311+pos%3*200-pos//3*100,72+pos//3*99)))
    def getFieldServant(self,pos):return(lambda img,cls:min((numpy.min(cv2.matchTemplate(img,i[...,:3],cv2.TM_SQDIFF_NORMED,mask=i[...,3])),no)for no,(_,portrait,_)in servantImg.items()if servantData[no][0]==cls[0]for i in portrait)[1]if cls else 0)(self._crop((120+318*pos,421,207+318*pos,490)),self.getFieldServantClassRank(pos))
    def getFieldServantClassRank(self,pos):return(lambda x:x if x is None else divmod(x,3))(self._select(CLASS[125],(13+318*pos,618,117+318*pos,702)))
    def getFieldServantHp(self,pos):return self._ocr((200+318*pos,620,293+318*pos,644))
    def getFieldServantNp(self,pos):return self._ocr((220+318*pos,655,274+318*pos,680))
    def getGachaHistory(self):XDetect._gachaHistory=numpy.vstack((XDetect._gachaHistory,(lambda img:img[cv2.minMaxLoc(cv2.matchTemplate(img,XDetect._gachaHistory[-80:],cv2.TM_SQDIFF_NORMED))[2][1]+80:])(cv2.threshold(cv2.cvtColor(self._crop((147,157,1105,547)),cv2.COLOR_BGR2GRAY),128,255,cv2.THRESH_BINARY)[1])))
    @classmethod
    def getGachaHistoryCount(cls):return cls.__new__(cls).inject(XDetect._gachaHistory)._count((IMG.GACHAHISTORY[0][...,0],IMG.GACHAHISTORY[1]),(28,0,60,XDetect._gachaHistory.shape[0]),.7)
    def getMaterial(self):return(lambda x:{MATERIAL[i][0]:x.count(i)for i in set(x)-{None}})([self._select(((i[1],None)for i in MATERIAL),(168+i%7*137,104+i//7*142,258+i%7*137,196+i//7*142),.02)for i in range(1,21)])
    def getSkillTargetCount(self):return(lambda x:numpy.bincount(numpy.diff(x))[1]+x[0])(cv2.dilate(numpy.max(cv2.threshold(numpy.max(self._crop((306,320,973,547)),axis=2),57,1,cv2.THRESH_BINARY)[1],axis=0).reshape(1,-1),numpy.ones((1,66),numpy.uint8)).ravel())if self._compare(IMG.CROSS,(1083,139,1113,166))else 0
    @retryOnError()
    def getStage(self):return self._select((IMG.STAGE1,IMG.STAGE2,IMG.STAGE3),(884,13,902,38),.5)+1
    @retryOnError()
    def getStageTotal(self):return self._select((IMG.STAGE1,IMG.STAGE2,IMG.STAGE3),(912,13,932,38),.5)+1
    def getTeamIndex(self):return self._loc(IMG.TEAMINDEX,(512,34,768,62))[2][0]//25
    # getTeam* series except getTeamIndex APIs are not used now
    def getTeamServantCard(self):return[reduce(lambda x,y:x<<1|y,(numpy.argmax(self.im[526,150+200*i+15*(i>2)+21*j])==0 for j in range(3)))for i in range(6)]
    def getTeamServantClassRank(self):return[(lambda x:x if x is None else divmod(x,3))(self._select(CLASS[100],(30+200*i+15*(i>2),133,115+200*i+15*(i>2),203)))for i in range(6)]
    def findFriend(self,img):return self._find(img,(13,166,1233,720))
    def findLastExec(self):return self._find(IMG.LASTEXEC,(200,160,1280,560))
    def findMail(self,img):return self._find(img,(73,166,920,720),threshold=.016)
    @classmethod
    def saveGachaHistory(cls):return(lambda c:(lambda img:(c,cls.__new__(cls).inject(img).save(f'GachaHistory({c})',(0,0,*img.shape[::-1]))))(numpy.vstack((cv2.putText(numpy.zeros((36,XDetect._gachaHistory.shape[1]),numpy.uint8),f'GachaHistory({c}) generated by FGO-py',(8,26),cv2.FONT_HERSHEY_DUPLEX,0.85,255,2,cv2.LINE_4),XDetect._gachaHistory[:numpy.flatnonzero(numpy.max(XDetect._gachaHistory,axis=1))[-1]+2]))))(cls.getGachaHistoryCount())
    def isGameAnnounce(self):raise NotImplementedError
    def isGameLaunch(self):raise NotImplementedError
    def isInCampaign(self):raise NotImplementedError
    def getCardServant(self,choices):raise NotImplementedError
    def getEnemyHpGauge(self):raise NotImplementedError
    def getTeamMaster(self):raise NotImplementedError
    def getTeamServant(self):raise NotImplementedError
    def getTeamServantAtk(self):raise NotImplementedError
    def getTeamServantCost(self):raise NotImplementedError
    def getTeamServantHouguLv(self):raise NotImplementedError
    def getTeamServantRank(self):raise NotImplementedError
    def getTeamServantSkillLv(self):raise NotImplementedError
    def findFarm(self):raise NotImplementedError
class Detect(XDetect,metaclass=logMeta(logger)):
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
