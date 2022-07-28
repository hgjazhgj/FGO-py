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
import logging,re,time,numpy
import fgoDevice
from itertools import permutations
from threading import Thread
from fgoDetect import Detect
from fgoFuse import fuse
from fgoImageListener import ImageListener
from fgoMetadata import servantData
from fgoSchedule import ScriptStop,schedule
from fgoLogging import getLogger,logit
logger=getLogger('Kernel')

friendImg=ImageListener('fgoImage/friend/')
mailImg=ImageListener('fgoImage/mail/')
def guardian():
    prev=None
    while True:
        if Detect.cache is not prev and Detect.cache.isNetworkError():
            logger.warning('Reconnecting')
            fgoDevice.device.press('K')
        prev=Detect.cache
        time.sleep(3)
Thread(target=guardian,daemon=True,name='Guardian').start()

def gacha():
    while fuse.value<30:
        if Detect().isGacha():fgoDevice.device.perform('MK',(600,2700))
        fgoDevice.device.press('\x08')
def lottery():
    while fuse.value<50:
        if Detect().isNextLottery():fgoDevice.device.perform('\xDCKJ',(600,2400,500))
        for _ in range(40):fgoDevice.device.press('2')
def mail():
    if not mailImg.flush():return
    Detect().setupMailDone()
    while True:
        while any((pos:=Detect.cache.findMail(i[1]))and(fgoDevice.device.touch(pos),True)[-1]for i in mailImg.items()):
            while not Detect().isMailDone():pass
        fgoDevice.device.swipe((400,600,400,200))
        if Detect().isMailListEnd():break
def synthesis():
    while True:
        fgoDevice.device.perform('8',(1000,))
        for i in range(4):
            for j in range(7):
                fgoDevice.device.touch((133+133*j,253+140*i))
                schedule.sleep(.1)
        if Detect().isSynthesisFinished():break
        fgoDevice.device.perform('  KK\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB',(800,300,300,1000,150,150,150,150,150,150,150,150,150,150,150,150,150,150,150))
        while not Detect().isSynthesisBegin():fgoDevice.device.press('\xBB')
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
class Turn:
    def __init__(self):
        self.stage=0
        self.stageTurn=0
        self.servant=[]
        self.countDown=[[[0,0,0],[0,0,0],[0,0,0]],[0,0,0]]
    def __call__(self,turn):
        self.stage,self.stageTurn=[t:=Detect(.2).getStage(),1+self.stageTurn*(self.stage==t)]
        if turn==1:
            Detect.cache.setupServantDead()
            self.stageTotal=Detect.cache.getStageTotal()
            self.servant=[servantData.get(Detect.cache.getFieldServant(i),None)for i in range(3)]
        else:self.servant=[servantData.get(Detect.cache.getFieldServant(i),None)if Detect.cache.isServantDead(i)else self.servant[i]for i in range(3)]
        logger.info(f'Turn {turn} Stage {self.stage} StageTurn {self.stageTurn} {self.servant}')
        if self.stageTurn==1:fgoDevice.device.perform('\x67\x68\x69'[numpy.argmax([Detect.cache.getEnemyHp(i)for i in range(3)])]+'\xBB',(800,500))
        self.dispatchSkill()
        fgoDevice.device.perform(' ',(2100,))
        fgoDevice.device.perform(self.selectCard(),(300,300,2300,1300,6000))
    def dispatchSkill(self):
        self.countDown=[[[max(0,j-1)for j in i]for i in self.countDown[0]],[max(0,i-1)for i in self.countDown[1]]]
        while skill:=[(0,i,j)for i in range(3)for j in range(3)if 0==self.countDown[0][i][j]and self.servant[i]and self.servant[i][5][j][0]and Detect.cache.isSkillReady(i,j)]: # +[(1,i)for i in range(3)if self.countDown[1][i]==0]:
            for i in skill:
                if i[0]==0:
                    if (p:=self.servant[i[1]][5][i[2]])[0]==1:
                        self.castServantSkill(i[1],i[2],i[1])
                        continue
                    elif p[0]==2:
                        np=[Detect.cache.getFieldServantNp(i)if self.servant[i]else 100 for i in range(3)]
                        if p[0]==0:
                            if any(i<100 for i in np):
                                self.castServantSkill(i[1],i[2],0)
                                continue
                        elif p[1]==1:
                            target=numpy.argmin(np)
                            if np[target]<100:
                                self.castServantSkill(i[1],i[2],target)
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
                                self.castServantSkill(i[1],i[2],i[1])
                                continue
                        else:
                            self.castServantSkill(i[1],i[2],0)
                            continue
                    elif p[0]==3:
                        np=[Detect.cache.getFieldServantNp(i)if self.servant[i]else 0 for i in range(3)]
                        if p[1]in{0,3,4}:
                            if any(i>=100 for i in np):
                                self.castServantSkill(i[1],i[2],0)
                                continue
                        elif p[1]==1:
                            target=numpy.argmax(np)
                            if np[target]>=100:
                                self.castServantSkill(i[1],i[2],target)
                                continue
                        elif p[1]==2:
                            np[i[1]]=0
                            if any(i>=100 for i in np):
                                self.castServantSkill(i[1],i[2],0)
                                continue
                        elif p[1]==5:
                            if np[i[1]]>=100:
                                self.castServantSkill(i[1],i[2],i[1])
                                continue
                        else:
                            self.castServantSkill(i[1],i[2],0)
                            continue
                    elif p[0]in{4,5,6}:
                        self.castServantSkill(i[1],i[2],0)
                        continue
                    elif p[0]==7:
                        hp=[Detect.cache.getFieldServantHp(i)if self.servant[i]else 999999 for i in range(3)]
                        if p[1]==0:
                            if any(i<4000 for i in hp):
                                self.castServantSkill(i[1],i[2],0)
                                continue
                        elif p[1]==1:
                            target=numpy.argmin(hp)
                            if hp[target]<4000:
                                self.castServantSkill(i[1],i[2],target)
                                continue
                        elif p[1]==2:
                            hp[i[1]]=999999
                            if any(i<4000 for i in hp):
                                self.castServantSkill(i[1],i[2],0)
                                continue
                        elif p[1]in{3,4}:
                            self.castServantSkill(i[1],i[2],0)
                            continue
                        elif p[1]==5:
                            if hp[i[1]]<4000:
                                self.castServantSkill(i[1],i[2],i[1])
                                continue
                        else:
                            self.castServantSkill(i[1],i[2],0)
                            continue
                    elif p[0]==8:
                        if any(self.servant[i]and(lambda x:x[1]and x[0]==x[1])(Detect.cache.getEnemyNp(i))for i in range(3)):
                            self.castServantSkill(i[1],i[2],i[1])
                            continue
                    elif p[0]==9:
                        if any(self.servant[i]and((lambda x:x[1]and x[0]==x[1])(Detect.cache.getEnemyNp(i))or Detect.cache.getFieldServantHp(i)<2500)for i in range(3)):
                            self.castServantSkill(i[1],i[2],i[1])
                            continue
                    self.countDown[0][i[1]][i[2]]=1
                else:...
    @logit(logger,logging.INFO)
    def selectCard(self):return''.join((lambda color,sealed,hougu,resist,critical:
            ['678'[i]for i in range(3)if hougu[i]]
            +['12345'[i]for i in sorted(range(5),key=(lambda x:-color[x]*resist[x]*(not sealed[x])*(1+critical[x])))]
            if any(hougu)else
            (lambda group:
                ['12345'[i]for i in(lambda choice:choice+tuple({0,1,2,3,4}-set(choice)))(
                    max(permutations(range(5),3),key=lambda card:(lambda colorChain,firstCardBonus:sum((firstCardBonus+[1.,1.2,1.4][i]*color[j])*(1+critical[j])*resist[j]*(not sealed[j])for i,j in enumerate(card))+(not any(sealed[i]for i in card))*(4.8*colorChain+(firstCardBonus+1.)*(3 if colorChain else 1.8)*(len({group[i]for i in card})==1)*resist[card[0]]))(len({color[i]for i in card})==1,.3*(color[card[0]]==1.1)))
                )])(Detect.cache.getCardGroup())
            )([[1,.8,1.1][i]for i in Detect().getCardColor()],Detect.cache.isCardSealed(),Detect.cache.isHouguReady(),[[1,1.7,.6][i]for i in Detect.cache.getCardResist()],[i/10 for i in Detect.cache.getCardCriticalRate()]))
    def castServantSkill(self,pos,skill,target):
        fgoDevice.device.press(('ASD','FGH','JKL')[pos][skill])
        if Detect(.7).isSkillNone():
            logger.warning(f'Skill {pos} {skill} None')
            self.countDown[0][pos][skill]=999
            fgoDevice.device.press('\x08')
        elif Detect.cache.isSkillCastFailed():
            logger.warning(f'Skill {pos} {skill} Cast Failed')
            self.countDown[0][pos][skill]=1
            fgoDevice.device.press('J')
        elif t:=Detect.cache.getSkillTargetCount():fgoDevice.device.perform(['3333','2244','3234'][t-1][f-5 if(f:=self.servant[pos][5][skill][1])in{6,7,8}else target],(300,))
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
        while True:
            if Detect(0,.3).isTurnBegin():
                self.turn+=1
                self.turnProc(self.turn)
            elif Detect.cache.isSpecialDropSuspended():
                schedule.checkKizunaReisou()
                logger.warning('Kizuna Reisou')
                Detect.cache.save('fgoLog/SpecialDrop')
                fgoDevice.device.press('\x67')
            elif not self.rainbowBox and Detect.cache.isSpecialDropRainbowBox():self.rainbowBox=True
            elif Detect.cache.isBattleFinished():
                logger.info('Battle Finished')
                if self.rainbowBox:
                    schedule.checkSpecialDrop()
                    logger.warning('Special Drop')
                    Detect.cache.save('fgoLog/SpecialDrop')
                return self.turn
            elif Detect.cache.isBattleDefeated():
                logger.warning('Battle Defeated')
                schedule.checkDefeated()
                return 0
            fgoDevice.device.perform('\xBB\x08',(100,100))
class Main:
    teamIndex=0
    def __init__(self,appleTotal=0,appleKind=0,battleClass=Battle):
        self.appleTotal=appleTotal
        self.appleKind=appleKind
        self.battleClass=battleClass
        self.appleCount=0
        self.battleCount=0
    def __call__(self):
        while True:
            self.battleProc=self.battleClass()
            while True:
                if Detect(.3,.3).isMainInterface():
                    fgoDevice.device.press('8')
                    if Detect(.7,.3).isApEmpty()and not self.eatApple():return
                    self.chooseFriend()
                    while not Detect(0,.3).isBattleBegin():pass
                    if self.teamIndex and Detect.cache.getTeamIndex()+1!=self.teamIndex:fgoDevice.device.perform('\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79'[self.teamIndex-1]+' ',(1000,1500))
                    fgoDevice.device.perform(' M',(800,10000))
                    break
                elif Detect.cache.isBattleContinue():
                    fgoDevice.device.press('L')
                    if Detect(.7,.3).isApEmpty()and not self.eatApple():return
                    self.chooseFriend()
                    schedule.sleep(6)
                    break
                elif Detect.cache.isTurnBegin():break
                elif Detect.cache.isAddFriend():fgoDevice.device.perform('X',(300,))
                elif Detect.cache.isSpecialDropSuspended():fgoDevice.device.perform('\x67',(300,))
                fgoDevice.device.press('\xBB')
            self.battleCount+=1
            logger.info(f'Battle {self.battleCount}')
            if self.battleProc():fgoDevice.device.perform('      ',(200,200,200,200,200,200))
            else:fgoDevice.device.perform('CIK',(500,500,500))
            schedule.checkStopLater()
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
                    Turn.friendInfo=(lambda r:(lambda p:([[[-1 if p[i*4+j]=='X'else int(p[i*4+j],16)for j in range(4)]for i in range(3)],[-1 if p[i+12]=='X'else int(p[i+12],16)for i in range(2)]]))(r.group())if r else[[[-1,-1,-1,-1],[-1,-1,-1,-1],[-1,-1,-1,-1]],[-1,-1]])(re.match('([0-9X]{3}[0-9A-FX]){3}[0-9X][0-9A-FX]$',i.replace('-','')[-14:].upper()))
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
