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
from fgoConst import VERSION
__version__=VERSION
__author__='hgjazhgj'
import logging,numpy,re,time,threading
import fgoDevice
from itertools import permutations
from functools import wraps
from fgoDetect import Detect,XDetect
from fgoFuse import fuse
from fgoImageListener import ImageListener
from fgoMetadata import servantData
from fgoSchedule import ScriptStop,schedule
from fgoLogging import getLogger,logit
logger=getLogger('Kernel')

friendImg=ImageListener('fgoImage/friend/')
mailImg=ImageListener('fgoImage/mail/')
lock=threading.Lock()
def withLock(lock):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            with lock:return func(*args,**kwargs)
        return wrapper
    return decorator
def guardian():
    logger=logging.getLogger('Guardian')
    prev=None
    while True:
        if XDetect.cache is not prev and XDetect.cache.isNetworkError():
            logger.warning('Reconnecting')
            fgoDevice.device.press('K')
        prev=XDetect.cache
        time.sleep(3)
threading.Thread(target=guardian,daemon=True,name='Guardian').start()
class Farming:
    def __init__(self):
        self.logger=getLogger('Farming')
        self.stop=False
    def __call__(self):
        while not self.stop:
            time.sleep(120)
            if not fgoDevice.device.available:continue
            self.run()
    @withLock(lock)
    def run(self):
        ...
farming=Farming()
threading.Thread(target=farming,daemon=True,name='Farming').start()
def setup():
    raise NotImplementedError
    if not fgoDevice.device.isInGame():
        fgoDevice.device.launch()
        while not Detect(1).isGameLaunch():pass
        while not Detect(1).isGameAnnounce():fgoDevice.device.press('\xBB')
        fgoDevice.device.press('\x08')
    elif False:...
@withLock(lock)
def gacha():
    while fuse.value<30:
        if Detect().isGacha():fgoDevice.device.perform('MK',(600,2700))
        fgoDevice.device.press('\x08')
@withLock(lock)
def lottery():
    Detect().setupLottery()
    count=0
    while(count:=0 if Detect().isLotteryContinue()else count+1)<5:
        for _ in range(40):fgoDevice.device.press('2')
@withLock(lock)
def mail():
    assert mailImg.flush()
    Detect().setupMailDone()
    while True:
        while any((pos:=Detect.cache.findMail(i[1]))and(fgoDevice.device.touch(pos),True)[-1]for i in mailImg.items()):
            while not Detect().isMailDone():pass
        fgoDevice.device.swipe((400,600,400,200))
        if Detect().isMailListEnd():break
@withLock(lock)
def synthesis():
    while True:
        fgoDevice.device.perform('8',(1000,))
        for i,j in((i,j)for i in range(4)for j in range(7)):
            fgoDevice.device.touch((133+133*j,253+142*i))
            schedule.sleep(.1)
        if Detect().isSynthesisFinished():break
        fgoDevice.device.perform('  KK\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB',(800,300,300,1000,150,150,150,150,150,150,150,150,150,150,150,150,150,150,150))
        while not Detect().isSynthesisBegin():fgoDevice.device.press('\xBB')
@withLock(lock)
def gachaHistory():
    Detect().setupGachaHistory()
    while not Detect.cache.isGachaHistoryListEnd():
        fgoDevice.device.swipe((930,500,930,200))
        Detect().getGachaHistory()
    fgoDevice.device.swipe((930,500,930,200))
    Detect().getGachaHistory()
    gachaHistory.result={'type':'GachaHistory'}|dict(zip(('value','file'),Detect.saveGachaHistory()))
@withLock(lock)
def bench(times=20,touch=True,screenshot=True):
    if not(touch or screenshot):touch=screenshot=True
    screenshotBench=[]
    for _ in range(times*screenshot):
        begin=time.time()
        fgoDevice.device.screenshot()
        screenshotBench.append(time.time()-begin)
    touchBench=[]
    for _ in range(times*touch):
        begin=time.time()
        fgoDevice.device.press('\xBB')
        touchBench.append(time.time()-begin)
    result=(sum(touchBench)-max(touchBench)-min(touchBench))*1000/(times-2)if touch else None,(sum(screenshotBench)-max(screenshotBench)-min(screenshotBench))*1000/(times-2)if screenshot else None
    logger.warning(f'Benchmark: {f"touch {result[0]:.2f}ms"if result[0]else""}{", "if all(result)else""}{f"screenshot {result[1]:.2f}ms"if result[1]else""}')
    return result
class ClassicTurn:
    skillInfo=[[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]]]
    houguInfo=[[1,7],[1,7],[1,7],[1,7],[1,7],[1,7]]
    masterSkill=[[0,0,0,7],[0,0,0,7],[0,0,0,0,7]]
    def __init__(self):
        ClassicTurn.friendInfo=[[[-1,-1,-1,-1],[-1,-1,-1,-1],[-1,-1,-1,-1]],[-1,-1]]
        self.stage=0
        self.stageTurn=0
        self.servant=[0,1,2]
        self.orderChange=[0,1,2,3,4,5]
        self.countDown=[[[0,0,0],[0,0,0],[0,0,0]],[0,0,0]]
    def __call__(self,turn):
        self.stage,self.stageTurn=[t:=Detect(.2).getStage(),1+self.stageTurn*(self.stage==t)]
        self.friend=[Detect.cache.isServantFriend(i)for i in range(3)]
        if turn==1:
            Detect.cache.setupServantDead(self.friend)
            self.stageTotal=Detect.cache.getStageTotal()
            self.servant=[6 if self.servant[i]>=6 or Detect.cache.getFieldServantClassRank(i)is None else self.servant[i]for i in range(3)]
        else:
            for i in(i for i in range(3)if self.servant[i]<6 and Detect.cache.isServantDead(i,self.friend[i])):
                self.servant[i]=max(self.servant)+1
                self.countDown[0][i]=[0,0,0]
        logger.info(f'Turn {turn} Stage {self.stage} StageTurn {self.stageTurn} {self.servant}')
        if self.stageTurn==1:Detect.cache.setupEnemyGird()
        self.dispatchSkill()
        fgoDevice.device.perform(' ',(2100,))
        fgoDevice.device.perform(self.selectCard(),(300,300,2300,1300,6000))
    def dispatchSkill(self):
        self.countDown=[[[max(0,j-1)for j in i]for i in self.countDown[0]],[max(0,i-1)for i in self.countDown[1]]]
        while(s:=[(self.getSkillInfo(i,j,3),0,(i,j))for i in range(3)if self.servant[i]<6 for j in range(3)if self.countDown[0][i][j]==0 and(t:=self.getSkillInfo(i,j,0))and min(t,self.stageTotal)<<8|self.getSkillInfo(i,j,1)<=self.stage<<8|self.stageTurn and Detect.cache.isSkillReady(i,j)]+[(self.masterSkill[i][-1],1,(i,))for i in range(3)if self.countDown[1][i]==0 and self.masterSkill[i][0]and min(self.masterSkill[i][0],self.stageTotal)<<8|self.masterSkill[i][1]<=self.stage<<8|self.stageTurn]):
            _,cast,arg=min(s,key=lambda x:x[0])
            [self.castServantSkill,self.castMasterSkill][cast](*arg)
            fgoDevice.device.perform('\x08',(1800,))
            while not Detect().isTurnBegin():pass
            Detect(.5)
    @logit(logger,logging.INFO)
    def selectCard(self):return''.join((lambda hougu,sealed,color,resist,critical:(fgoDevice.device.perform('\x67\x68\x69\x64\x65\x66'[numpy.argmax([Detect.cache.getEnemyHp(i)for i in range(6)])],(500,))if any(hougu)or self.stageTurn==1 else 0,['678'[i]for i in sorted((i for i in range(3)if hougu[i]),key=lambda x:self.getHouguInfo(x,1))]+['12345'[i]for i in sorted(range(5),key=(lambda x:-color[x]*resist[x]*(not sealed[x])*(1+critical[x])))]if any(hougu)else(lambda group:['12345'[i]for i in(lambda choice:choice+tuple({0,1,2,3,4}-set(choice)))(logger.debug('cardRank'+','.join(('  'if i%5 else'\n')+f'({j}, {k:5.2f})'for i,(j,k)in enumerate(sorted([(card,(lambda colorChain,firstCardBonus:sum((firstCardBonus+[1.,1.2,1.4][i]*color[j])*(1+critical[j])*resist[j]*(not sealed[j])for i,j in enumerate(card))+(not any(sealed[i]for i in card))*(4.8*colorChain+(firstCardBonus+1.)*(3 if colorChain else 1.8)*(len({group[i]for i in card})==1)*resist[card[0]]))(len({color[i]for i in card})==1,.3*(color[card[0]]==1.1)))for card in permutations(range(5),3)],key=lambda x:-x[1]))))or max(permutations(range(5),3),key=lambda card:(lambda colorChain,firstCardBonus:sum((firstCardBonus+[1.,1.2,1.4][i]*color[j])*(1+critical[j])*resist[j]*(not sealed[j])for i,j in enumerate(card))+(not any(sealed[i]for i in card))*(4.8*colorChain+(firstCardBonus+1.)*(3 if colorChain else 1.8)*(len({group[i]for i in card})==1)*resist[card[0]]))(len({color[i]for i in card})==1,.3*(color[card[0]]==1.1))))])(Detect.cache.getCardGroup()))[1])([self.servant[i]<6 and j and(t:=self.getHouguInfo(i,0))and self.stage>=min(t,self.stageTotal)for i,j in enumerate(Detect().isHouguReady())],Detect.cache.isCardSealed(),[[.8,1.,1.1][i]for i in Detect.cache.getCardColor()],[[1.,1.7,.6][i]for i in Detect.cache.getCardResist()],[i/10 for i in Detect.cache.getCardCriticalRate()]))
    def getSkillInfo(self,pos,skill,arg):return self.friendInfo[0][skill][arg]if self.friend[pos]and self.friendInfo[0][skill][arg]>=0 else self.skillInfo[self.orderChange[self.servant[pos]]][skill][arg]
    def getHouguInfo(self,pos,arg):return self.friendInfo[1][arg]if self.friend[pos]and self.friendInfo[1][arg]>=0 else self.houguInfo[self.orderChange[self.servant[pos]]][arg]
    def castServantSkill(self,pos,skill):
        fgoDevice.device.press(('ASD','FGH','JKL')[pos][skill])
        if Detect(.7).isSkillNone():
            logger.warning(f'Skill {pos} {skill} Disabled')
            self.countDown[0][pos][skill]=999
            fgoDevice.device.press('\x08')
        elif Detect(.7).isSkillCastFailed():
            self.countDown[pos][skill]=1
            fgoDevice.device.press('J')
        elif t:=Detect.cache.getSkillTargetCount():fgoDevice.device.perform(['3333','2244','3234'][t-1][self.getSkillInfo(pos,skill,2)],(300,))
    def castMasterSkill(self,skill):
        self.countDown[1][skill]=15
        fgoDevice.device.perform('Q'+'WER'[skill],(300,300))
        if self.masterSkill[skill][2]:
            if skill==2 and self.masterSkill[2][3]:
                if self.masterSkill[2][2]-1 not in self.servant or self.masterSkill[2][3]-1 in self.servant:return fgoDevice.device.perform('\xBB',(300,))
                p=self.servant.index(self.masterSkill[2][2]-1)
                fgoDevice.device.perform(('TYUIOP'[p],'TYUIOP'[self.masterSkill[2][3]-max(self.servant)+1],'Z'),(300,300,2600))
                self.orderChange[self.masterSkill[2][2]-1],self.orderChange[self.masterSkill[2][3]-1]=self.orderChange[self.masterSkill[2][3]-1],self.orderChange[self.masterSkill[2][2]-1]
                fgoDevice.device.perform('\x08',(2300,))
                while not Detect().isTurnBegin():pass
                self.friend=[Detect(.5).isServantFriend(0),Detect.cache.isServantFriend(1),Detect.cache.isServantFriend(2)]
                Detect.cache.setupServantDead(self.friend)
            elif t:=Detect(.5).getSkillTargetCount():fgoDevice.device.perform(['3333','2244','3234'][t-1][self.masterSkill[skill][2]],(300,))
class Turn:
    def __init__(self):
        self.stage=0
        self.stageTurn=0
        self.countDown=[[[0,0,0],[0,0,0],[0,0,0]],[0,0,0]]
    def __call__(self,turn):
        self.stage,self.stageTurn=[t:=Detect(.2).getStage(),1+self.stageTurn*(self.stage==t)]
        if turn==1:
            Detect.cache.setupServantDead()
            self.stageTotal=Detect.cache.getStageTotal()
            self.servant=[(lambda x:(x,)+servantData.get(x,()))(Detect.cache.getFieldServant(i))for i in range(3)]
        else:
            for i in(i for i in range(3)if Detect.cache.isServantDead(i)):
                self.servant[i]=(lambda x:(x,)+servantData.get(x,()))(Detect.cache.getFieldServant(i))
                self.countDown[0][i]=[0,0,0]
        logger.info(f'Turn {turn} Stage {self.stage} StageTurn {self.stageTurn} {[i[0]for i in self.servant]}')
        if self.stageTurn==1:Detect.cache.setupEnemyGird()
        self.dispatchSkill()
        self.enemy=[Detect.cache.getEnemyHp(i)for i in range(6)]
        fgoDevice.device.perform(' ',(2100,))
        fgoDevice.device.perform(self.selectCard(),(300,300,2300,1300,6000))
    def dispatchSkill(self):
        self.countDown=[[[max(0,j-1)for j in i]for i in self.countDown[0]],[max(0,i-1)for i in self.countDown[1]]]
        while skill:=[(0,i,j)for i in range(3)for j in range(3)if 0==self.countDown[0][i][j]and self.servant[i][0]and self.servant[i][6][j][0]and Detect.cache.isSkillReady(i,j)]: # +[(1,i)for i in range(3)if self.countDown[1][i]==0]:
            for i in skill:
                if i[0]==0:
                    if (p:=self.servant[i[1]][6][i[2]])[0]==1:
                        self.castServantSkill(i[1],i[2],i[1]+1)
                        continue
                    elif p[0]==2:
                        np=[Detect.cache.getFieldServantNp(i)if self.servant[i][0]else 100 for i in range(3)]
                        if p[1]==0:
                            if any(i<100 for i in np):
                                self.castServantSkill(i[1],i[2],0)
                                continue
                        elif p[1]==1:
                            np[i[1]]=100
                            target=numpy.argmin(np)
                            if np[target]<100:
                                self.castServantSkill(i[1],i[2],target+1)
                                continue
                        elif p[1]==2:
                            np[i[1]]=100
                            if any(i<100 for i in np):
                                self.castServantSkill(i[1],i[2],0)
                                continue
                        elif p[1]in{3,4}:
                            if self.stageTurn>1:
                                self.castServantSkill(i[1],i[2],0)
                                continue
                        elif p[1]==5:
                            if np[i[1]]<100:
                                self.castServantSkill(i[1],i[2],i[1]+1)
                                continue
                        else:
                            self.castServantSkill(i[1],i[2],0)
                            continue
                    elif p[0]==3:
                        np=[Detect.cache.getFieldServantNp(i)if self.servant[i][0]else 0 for i in range(3)]
                        if p[1]in{0,3,4}:
                            if any(i>=100 for i in np):
                                self.castServantSkill(i[1],i[2],0)
                                continue
                        elif p[1]==1:
                            target=numpy.argmax(np)
                            if np[target]>=100:
                                self.castServantSkill(i[1],i[2],target+1)
                                continue
                        elif p[1]==2:
                            np[i[1]]=0
                            if any(i>=100 for i in np):
                                self.castServantSkill(i[1],i[2],0)
                                continue
                        elif p[1]==5:
                            if np[i[1]]>=100:
                                self.castServantSkill(i[1],i[2],i[1]+1)
                                continue
                        else:
                            self.castServantSkill(i[1],i[2],0)
                            continue
                    elif p[0]in{4,5,6}:
                        self.castServantSkill(i[1],i[2],0)
                        continue
                    elif p[0]==7:
                        hp=[Detect.cache.getFieldServantHp(i)if self.servant[i][0]else 999999 for i in range(3)]
                        if p[1]==0:
                            if any(i<6600 for i in hp):
                                self.castServantSkill(i[1],i[2],0)
                                continue
                        elif p[1]==1:
                            target=numpy.argmin(hp)
                            if hp[target]<6600:
                                self.castServantSkill(i[1],i[2],target+1)
                                continue
                        elif p[1]==2:
                            hp[i[1]]=999999
                            if any(i<6600 for i in hp):
                                self.castServantSkill(i[1],i[2],0)
                                continue
                        elif p[1]in{3,4}:
                            self.castServantSkill(i[1],i[2],0)
                            continue
                        elif p[1]==5:
                            if hp[i[1]]<6600:
                                self.castServantSkill(i[1],i[2],i[1]+1)
                                continue
                        else:
                            self.castServantSkill(i[1],i[2],0)
                            continue
                    elif p[0]==8:
                        if any((lambda x:x[1]and x[0]==x[1])(Detect.cache.getEnemyNp(i))for i in range(6)):
                            self.castServantSkill(i[1],i[2],i[1]+1)
                            continue
                    elif p[0]==9:
                        if any((lambda x:x[1]and x[0]==x[1])(Detect.cache.getEnemyNp(i))for i in range(6))or Detect.cache.getFieldServantHp(i[1])<3300:
                            self.castServantSkill(i[1],i[2],i[1]+1)
                            continue
                    self.countDown[0][i[1]][i[2]]=1
                else:...
    @logit(logger,logging.INFO)
    def selectCard(self):
        color,sealed,hougu,resist,critical=[[1,.8,1.1][i]for i in Detect().getCardColor()],Detect.cache.isCardSealed(),Detect.cache.isHouguReady(),[[1,1.7,.6][i]for i in Detect.cache.getCardResist()],[i/10 for i in Detect.cache.getCardCriticalRate()]
        houguTargeted,houguArea,houguSupport=[[j for j in range(3)if hougu[j]and self.servant[j][0]and self.servant[j][5][0]==i]for i in range(3)]
        houguArea=houguArea if self.stage==self.stageTotal or sum(i>0 for i in self.enemy)>1 and sum(self.enemy)>12000 else[]
        houguTargeted=houguTargeted if self.stage==self.stageTotal or max(self.enemy)>23000+8000*len(houguArea)else[]
        if self.stageTurn==1 or houguTargeted:fgoDevice.device.perform('\x67\x68\x69\x64\x65\x66'[numpy.argmax(self.enemy)],(500,))
        return''.join((lambda hougu:['678'[i]for i in hougu]+['12345'[i]for i in sorted(range(5),key=(lambda x:-color[x]*resist[x]*(not sealed[x])*(1+critical[x])))]if hougu else(lambda group:['12345'[i]for i in(lambda choice:choice+tuple({0,1,2,3,4}-set(choice)))(max(permutations(range(5),3),key=lambda card:(lambda colorChain,firstCardBonus:sum((firstCardBonus+[1.,1.2,1.4][i]*color[j])*(1+critical[j])*resist[j]*(not sealed[j])for i,j in enumerate(card))+(not any(sealed[i]for i in card))*(4.8*colorChain+(firstCardBonus+1.)*(3 if colorChain else 1.8)*(len({group[i]for i in card})==1)*resist[card[0]]))(len({color[i]for i in card})==1,.3*(color[card[0]]==1.1))))])(Detect.cache.getCardGroup()))(houguSupport+houguArea+houguTargeted))
    def castServantSkill(self,pos,skill,target):
        fgoDevice.device.press(('ASD','FGH','JKL')[pos][skill])
        if Detect(.7).isSkillNone():
            logger.warning(f'Skill {pos} {skill} Disabled')
            self.countDown[0][pos][skill]=999
            fgoDevice.device.press('\x08')
        elif Detect.cache.isSkillCastFailed():
            logger.warning(f'Skill {pos} {skill} Cast Failed')
            self.countDown[0][pos][skill]=1
            fgoDevice.device.press('J')
        elif t:=Detect.cache.getSkillTargetCount():fgoDevice.device.perform(['3333','2244','3234'][t-1][f-5 if(f:=self.servant[pos][6][skill][1])in{6,7,8}else target],(300,))
        fgoDevice.device.press('\x08')
        while not Detect().isTurnBegin():pass
        Detect(.5)
    def castMasterSkill(self,skill,target):
        self.countDown[1][skill]=15
        fgoDevice.device.perform('Q'+'WER'[skill],(300,300))
        if t:=Detect(.4).getSkillTargetCount():fgoDevice.device.perform(['3333','2244','3234'][t-1][target],(300,))
        while not Detect().isTurnBegin():pass
        Detect(.5)
class Battle:
    def __init__(self,turnClass=Turn):
        self.turn=0
        self.turnProc=turnClass()
        self.rainbowBox=False
    def __call__(self):
        self.start=time.time()
        self.material={}
        while True:
            if Detect(0,.3).isTurnBegin():
                self.turn+=1
                self.turnProc(self.turn)
            elif Detect.cache.isSpecialDropSuspended():
                schedule.checkKizunaReisou()
                logger.warning('Kizuna Reisou')
                Detect.cache.save('fgoLog/SpecialDrop')
                fgoDevice.device.press('\x1B')
            elif not self.rainbowBox and Detect.cache.isSpecialDropRainbowBox():self.rainbowBox=True
            elif Detect.cache.isBattleFinished():
                logger.info('Battle Finished')
                self.material=Detect(.4).getMaterial()
                if self.rainbowBox:
                    schedule.checkSpecialDrop()
                    logger.warning('Special Drop')
                    Detect.cache.save('fgoLog/SpecialDrop')
                return True
            elif Detect.cache.isBattleDefeated():
                logger.warning('Battle Defeated')
                schedule.checkDefeated()
                return False
            fgoDevice.device.perform('\xBB\x08',(100,100))
    @property
    def result(self):
        return{
            'type':'Battle',
            'turn':self.turn,
            'time':time.time()-self.start,
            'material':self.material,
        }
class Main:
    teamIndex=0
    def __init__(self,appleTotal=0,appleKind=0,battleClass=Battle):
        self.appleTotal=appleTotal
        self.appleKind=appleKind
        self.battleClass=battleClass
        self.appleCount=0
        self.battleCount=0
    @withLock(lock)
    def __call__(self):
        self.start=time.time()
        self.material={}
        self.battleTurn=0
        self.battleTime=0
        self.defeated=0
        while True:
            self.battleProc=self.battleClass()
            while True:
                if Detect(.3,.3).isMainInterface():
                    fgoDevice.device.press('8')
                    if Detect(.7,.3).isApEmpty()and not self.eatApple():return
                    self.chooseFriend()
                    while not Detect(0,.3).isBattleBegin():pass
                    if self.teamIndex and Detect.cache.getTeamIndex()+1!=self.teamIndex:fgoDevice.device.perform('\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79'[self.teamIndex-1]+' ',(1000,1500))
                    fgoDevice.device.perform(' M ',(2000,2000,13000))
                    break
                elif Detect.cache.isBattleContinue():
                    fgoDevice.device.press('L')
                    if Detect(.7,.3).isApEmpty()and not self.eatApple():return
                    self.chooseFriend()
                    schedule.sleep(6)
                    break
                elif Detect.cache.isTurnBegin():break
                elif Detect.cache.isAddFriend():fgoDevice.device.perform('X',(300,))
                elif Detect.cache.isSpecialDropSuspended():fgoDevice.device.perform('\x1B',(300,))
                fgoDevice.device.press('\xBB')
            self.battleCount+=1
            logger.info(f'Battle {self.battleCount}')
            if self.battleProc():
                battleResult=self.battleProc.result
                self.battleTurn+=battleResult['turn']
                self.battleTime+=battleResult['time']
                self.material={i:self.material.get(i,0)+battleResult['material'].get(i,0)for i in self.material|battleResult['material']}
                fgoDevice.device.perform(' '*10,(400,)*10)
            else:
                self.defeated+=1
                fgoDevice.device.perform('CIK',(500,500,500))
            schedule.checkStopLater()
    @property
    def result(self):
        return{
            'type':'Main',
            'time':time.time()-self.start,
            'battle':self.battleCount,
            'defeated':self.defeated,
            'turnPerBattle':self.battleTurn/(self.battleCount-self.defeated)if self.battleCount-self.defeated else 0,
            'timePerBattle':self.battleTime/(self.battleCount-self.defeated)if self.battleCount-self.defeated else 0,
            'material':self.material
        }
    @logit(logger,logging.INFO)
    def eatApple(self):
        if self.appleCount==self.appleTotal:return fgoDevice.device.press('Z')
        self.appleCount+=1
        fgoDevice.device.perform('W4K8'[self.appleKind]+'L',(600,1200))
        # for i in set('W4K')-{'W4K8'[self.appleKind]}:
        #     if not Detect().isApEmpty():break
        #     fgoDevice.device.perform(i+'L',(600,1200))
        # else:raise ScriptStop('No Apples')
        return self.appleCount
    @logit(logger,logging.INFO)
    def chooseFriend(self):
        refresh=False
        while not Detect(0,.3).isChooseFriend():
            if Detect.cache.isNoFriend():
                if refresh:schedule.sleep(10)
                fgoDevice.device.perform('\xBAK',(500,1000))
                refresh=True
        if not friendImg.flush():return fgoDevice.device.press('8')
        while True:
            timer=time.time()
            while True:
                for i in(i for i,j in friendImg.items()if(lambda pos:pos and(fgoDevice.device.touch(pos),True)[-1])(Detect.cache.findFriend(j))):
                    ClassicTurn.friendInfo=(lambda r:(lambda p:
                        [
                            [[-1 if p[i*4+j]=='X'else int(p[i*4+j],16)for j in range(4)]for i in range(3)],
                            [-1 if p[i+12]=='X'else int(p[i+12],16)for i in range(2)]
                        ]
                    )(r.group())if r else[[[-1,-1,-1,-1],[-1,-1,-1,-1],[-1,-1,-1,-1]],[-1,-1]])(re.match('([0-9X]{3}[0-9A-FX]){3}[0-9X][0-9A-FX]$',i.replace('-','')[-14:].upper()))
                    return i
                if Detect.cache.isFriendListEnd():break
                fgoDevice.device.swipe((400,600,400,200))
                Detect(.4)
            if refresh:schedule.sleep(max(0,timer+10-time.time()))
            fgoDevice.device.perform('\xBAK',(500,1000))
            refresh=True
            while not Detect(.2).isChooseFriend():
                if Detect.cache.isNoFriend():
                    schedule.sleep(10)
                    fgoDevice.device.perform('\xBAK',(500,1000))
