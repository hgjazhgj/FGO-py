import os,time,cv2,numpy
from functools import reduce,wraps
from fgoControl import control
from fgoFuse import fuse
from fgoLogging import logMeta,getLogger
logger=getLogger('Check')
IMG=(lambda t:([setattr(t,i[:-4].upper(),cv2.imread(f'fgoImage/{i}'))for i in os.listdir('fgoImage')if i[-4:]=='.png'],t)[-1])(type('IMG',(),{}))
class Check(metaclass=logMeta(logger)):
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
    def __new__(cls,*args,**kwargs):
        cls.cache=super().__new__(cls)
        return cls.cache
    def __init__(self,forwardLagency=.1,backwardLagency=0):
        control.sleep(forwardLagency)
        self.im=self.device.screenshot()
        fuse.increase()
        control.sleep(backwardLagency)
    def _compare(self,img,rect=(0,0,1920,1080),threshold=.05):return threshold>cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],img,cv2.TM_SQDIFF_NORMED))[0]and fuse.reset(self)
    def _select(self,img,rect=(0,0,1920,1080),threshold=.2):return(lambda x:numpy.argmin(x)if threshold>min(x)else None)([cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],i,cv2.TM_SQDIFF_NORMED))[0]for i in img])
    def _ocr(self,rect):return reduce(lambda x,y:x*10+y[1],(lambda contours,hierarchy:sorted(((pos,loc[2][0]//20)for pos,loc in((clip[0],cv2.minMaxLoc(cv2.matchTemplate(IMG.OCR,numpy.array([[[255*(cv2.pointPolygonTest(contours[i],(clip[0]+x,clip[1]+y),False)>=0and(hierarchy[0][i][2]==-1or cv2.pointPolygonTest(contours[hierarchy[0][i][2]],(clip[0]+x,clip[1]+y),False)<0))]*3for x in range(clip[2])]for y in range(clip[3])],dtype=numpy.uint8),cv2.TM_SQDIFF_NORMED)))for i,clip in((i,cv2.boundingRect(contours[i]))for i in range(len(contours))if hierarchy[0][i][3]==-1)if 8<clip[2]<20<clip[3]<27)if loc[0]<.3),key=lambda x:x[0]))(*cv2.findContours(cv2.threshold(cv2.cvtColor(self.im[rect[1]:rect[3],rect[0]:rect[2]],cv2.COLOR_BGR2GRAY),150,255,cv2.THRESH_BINARY)[1],cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)),0)
    def save(self,file=''):cv2.imwrite(time.strftime(file if file else'%Y-%m-%d_%H.%M.%S.jpg'),self.im)
    def show(self):
        cv2.imshow('Check Screenshot - Press S to save',cv2.resize(self.im,(0,0),fx=.4,fy=.4))
        if cv2.waitKey()==ord('s'):self.save()
        cv2.destroyAllWindows()
    def find(self,img,rect=(0,0,1920,1080),threshold=.05):return(lambda loc:((rect[0]+loc[2][0]+(img.shape[1]>>1),rect[1]+loc[2][1]+(img.shape[0]>>1)),fuse.reset(self))[0]if loc[0]<threshold else None)(cv2.minMaxLoc(cv2.matchTemplate(self.im[rect[1]:rect[3],rect[0]:rect[2]],img,cv2.TM_SQDIFF_NORMED)))
    def isAddFriend(self):return self._compare(IMG.END,(243,863,745,982))
    def isApEmpty(self):return self._compare(IMG.APEMPTY,(906,897,1017,967))
    # modified (1673,959,1899,1069)
    def isBattleBegin(self):return self._compare(IMG.BATTLEBEGIN,(1639,951,1865,1061))
    def isBattleContinue(self):return self._compare(IMG.BATTLECONTINUE,(1072,805,1441,895))
    def isBattleDefeated(self):return self._compare(IMG.DEFEATED,(445,456,702,523))
    def isBattleFinished(self):return self._compare(IMG.BOUND,(112,250,454,313))or self._compare(IMG.BOUNDUP,(987,350,1468,594))
    def isChooseFriend(self):return self._compare(IMG.CHOOSEFRIEND,(1249,270,1387,650))
    def isCardSealed(self):return[any(self._compare(j,(43+386*i,667,350+386*i,845),.3)for j in(IMG.CHARASEALED,IMG.CARDSEALED))for i in range(5)]
    def isGacha(self):return self._compare(IMG.GACHA,(973,960,1312,1052))
    def isHouguReady(self,that=None):return(lambda that:[not any(that._compare(j,(470+346*i,258,773+346*i,387),.4)for j in(IMG.HOUGUSEALED,IMG.CHARASEALED,IMG.CARDSEALED))and(numpy.mean(self.im[1019:1026,217+478*i:235+478*i])>55or numpy.mean(that.im[1019:1026,217+478*i:235+478*i])>55)for i in range(3)])(Check(.15)if that is None else that)
    def isListEnd(self,pos):return any(self._compare(i,(pos[0]-30,pos[1]-20,pos[0]+30,pos[1]+1),.25)for i in(IMG.LISTEND,IMG.LISTNONE))
    # modified (1630,950,1919,1079)
    def isMainInterface(self):return self._compare(IMG.MENU,(1630,920,1919,1049))
    def isNextJackpot(self):return self._compare(IMG.JACKPOT,(1220,347,1318,389))
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
    # modified (1296,20,1342,56)
    @retryOnError()
    def getStage(self):return self._select((IMG.STAGE1,IMG.STAGE2,IMG.STAGE3),(1326,20,1372,56),.5)+1
    # modified (1325,20,1372,56),.5)
    @retryOnError()
    def getStageTotal(self):return self._select((IMG.STAGETOTAL1,IMG.STAGETOTAL2,IMG.STAGETOTAL3),(1350,20,1397,56),.5)+1
    def getTeamIndex(self):return cv2.minMaxLoc(cv2.matchTemplate(self.im[58:92,768:1152],IMG.TEAMINDEX,cv2.TM_SQDIFF_NORMED))[2][0]//37+1
    # def isEnemyDanger(self):raise NotImplementedError
    def getEnemyHPGauge(self):raise NotImplementedError
    def getEnemyNP(self):raise NotImplementedError
    def getCriticalRate(self):raise NotImplementedError
