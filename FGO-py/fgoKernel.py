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
from itertools import permutations
from threading import Thread
from fgoDetect import Detect
from fgoDevice import Device
from fgoFuse import fuse
from fgoImageListener import ImageListener
from fgoSchedule import ScriptStop,schedule
from fgoLogging import getLogger,logit
logger=getLogger('Kernel')

friendImg=ImageListener('fgoImage/friend/')
mailImg=ImageListener('fgoImage/mail/')
device=Device()
def guardian():
    prev=None
    while True:
        if Detect.cache is not prev and Detect.cache.isNetworkError():
            logger.warning('Reconnecting')
            device.press('K')
        prev=Detect.cache
        time.sleep(3)
Thread(target=guardian,daemon=True,name='Guardian').start()

def gacha():
    while fuse.value<30:
        if Detect().isGacha():device.perform('MK',(200,2700))
        device.press('\x08')
def jackpot():
    while fuse.value<50:
        if Detect().isNextLottery():device.perform('\xDCKJ',(600,2400,500))
        for _ in range(40):device.press('2')
def mail():
    if not mailImg.flush():return
    Detect().setupMailDone()
    while True:
        while any((pos:=Detect.cache.findMail(i[1]))and(device.touch(pos),True)[-1]for i in mailImg.items()):
            while not Detect().isMailDone():pass
        device.swipe((400,600,400,200))
        if Detect().isMailListEnd():break
def synthesis():
    while True:
        device.perform('8',(1000,))
        for i in range(4):
            for j in range(7):
                device.touch((200+200*j,380+210*i))
                schedule.sleep(.1)
        if Detect().isSynthesisFinished():break
        device.perform('  KK\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB',(800,300,300,1000,150,150,150,150,150,150,150,150,150,150,150,150,150,150,150))
        while not Detect().isSynthesisBegin():device.press('\xBB')
def bench(times=20,touch=True,screenshot=True):
    if not(touch or screenshot):touch=screenshot=True
    screenshotBench=[]
    for _ in range(times*screenshot):
        begin=time.time()
        device.screenshot()
        screenshotBench.append(time.time()-begin)
    touchBench=[]
    for _ in range(times*touch):
        begin=time.time()
        device.press('\xBB')
        touchBench.append(time.time()-begin)
    result=(sum(touchBench)-max(touchBench)-min(touchBench))*1000/(times-2)if touch else None,(sum(screenshotBench)-max(screenshotBench)-min(screenshotBench))*1000/(times-2)if screenshot else None
    logger.warning(f'Benchmark: {f"touch {result[0]:.2f}ms"if result[0]else""}{", "if all(result)else""}{f"screenshot {result[1]:.2f}ms"if result[1]else""}')
    return result
class Turn:
    skillInfo=[[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]]]
    houguInfo=[[1,7],[1,7],[1,7],[1,7],[1,7],[1,7]]
    masterSkill=[[0,0,0,7],[0,0,0,7],[0,0,0,0,7]]
    def __init__(self):
        Turn.friendInfo=[[[-1,-1,-1,-1],[-1,-1,-1,-1],[-1,-1,-1,-1]],[-1,-1]]
        self.stage=0
        self.stageTurn=0
        self.servant=[0,1,2]
        self.team=[None]*6
        self.orderChange=[0,1,2,3,4,5]
        self.countDown=[[[0,0,0],[0,0,0],[0,0,0]],[0,0,0]]
    def __call__(self,turn):
        self.stage,self.stageTurn=[t:=Detect(.2).getStage(),1+self.stageTurn*(self.stage==t)]
        self.friend=Detect.cache.isServantFriend()
        if turn==1:
            Detect.cache.setupServantDead(self.friend)
            self.stageTotal=Detect.cache.getStageTotal()
        else:self.servant=(lambda m,p:[m+p.index(i)+1 if i in p else self.servant[i]for i in range(3)])(max(self.servant),(lambda dead:[i for i in range(3)if self.servant[i]<6 and dead[i]])(Detect.cache.isServantDead(self.friend)))
        logger.info(f'Turn {turn} Stage {self.stage} StageTurn {self.stageTurn} {self.servant}')
        Detect.cache.getFieldServantHp(),Detect.cache.getFieldServantNp(),Detect.cache.getEnemyNp()
        if self.stageTurn==1:device.perform('\x67\x68\x69'[numpy.argmax(Detect.cache.getEnemyHp())]+'\xBB',(800,500))
        self.countDown=[[[max(0,j-1)for j in i]for i in self.countDown[0]],[max(0,i-1)for i in self.countDown[1]]]
        self.dispatchSkill()
        device.perform(' ',(2100,))
        device.perform(self.selectCard(),(300,300,2300,1300,6000))
    def dispatchSkill(self):
        while(s:=(lambda skill:[(self.getSkillInfo(i,j,3),0,(i,j))for i in range(3)if self.servant[i]<6 for j in range(3)if skill[i][j]and(t:=self.getSkillInfo(i,j,0))and min(t,self.stageTotal)<<8|self.getSkillInfo(i,j,1)<=self.stage<<8|self.stageTurn])(Detect.cache.isSkillReady())+[(self.masterSkill[i][-1],1,(i,))for i in range(3)if self.countDown[1][i]==0 and min(self.masterSkill[i][0],self.stageTotal)<<8|self.masterSkill[i][1]<=self.stage<<8|self.stageTurn]):
            _,cast,arg=min(s,key=lambda x:x[0])
            [self.castServantSkill,self.castMasterSkill][cast](*arg)
            device.perform('\x08',(1800,))
            while not Detect().isTurnBegin():pass
            Detect(.5)
    @logit(logger,logging.INFO)
    def selectCard(self):return''.join((lambda hougu,sealed,color,resist,critical:['678'[i]for i in sorted((i for i in range(3)if hougu[i]),key=lambda x:self.getHouguInfo(x,1))]+['12345'[i]for i in sorted(range(5),key=(lambda x:-color[x]*resist[x]*(not sealed[x])*(1+critical[x])))]if any(hougu)else(lambda group:['12345'[i]for i in(lambda choice:choice+tuple({0,1,2,3,4}-set(choice)))(logger.debug('cardRank'+','.join(('  'if i%5 else'\n')+f'({j}, {k:5.2f})'for i,(j,k)in enumerate(sorted([(card,(lambda colorChain,firstCardBonus:sum((firstCardBonus+[1.,1.2,1.4][i]*color[j])*(1+critical[j])*resist[j]*(not sealed[j])for i,j in enumerate(card))+(not any(sealed[i]for i in card))*(4.8*colorChain+(firstCardBonus+1.)*(3 if colorChain else 1.8)*(len({group[i]for i in card})==1)*resist[card[0]]))(len({color[i]for i in card})==1,.3*(color[card[0]]==1.1)))for card in permutations(range(5),3)],key=lambda x:-x[1]))))or max(permutations(range(5),3),key=lambda card:(lambda colorChain,firstCardBonus:sum((firstCardBonus+[1.,1.2,1.4][i]*color[j])*(1+critical[j])*resist[j]*(not sealed[j])for i,j in enumerate(card))+(not any(sealed[i]for i in card))*(4.8*colorChain+(firstCardBonus+1.)*(3 if colorChain else 1.8)*(len({group[i]for i in card})==1)*resist[card[0]]))(len({color[i]for i in card})==1,.3*(color[card[0]]==1.1))))])(Detect.cache.getCardGroup()))([self.servant[i]<6 and j and(t:=self.getHouguInfo(i,0))and self.stage>=min(t,self.stageTotal)for i,j in enumerate(Detect().isHouguReady())],Detect.cache.isCardSealed(),Detect.cache.getCardColor(),Detect.cache.getCardResist(),Detect.cache.getCriticalRate()))
    def getSkillInfo(self,pos,skill,arg):return self.friendInfo[0][skill][arg]if self.friend[pos]and self.friendInfo[0][skill][arg]>=0 else self.skillInfo[self.orderChange[self.servant[pos]]][skill][arg]
    def getHouguInfo(self,pos,arg):return self.friendInfo[1][arg]if self.friend[pos]and self.friendInfo[1][arg]>=0 else self.houguInfo[self.orderChange[self.servant[pos]]][arg]
    def castServantSkill(self,pos,skill):
        device.press(('ASD','FGH','JKL')[pos][skill])
        if Detect(.7).isSkillCastFailed():
            self.countDown[pos][skill]=1
            return device.press('J')
        if t:=Detect.cache.getSkillTargetCount():device.perform(['3333','2244','3234'][t-1][self.getSkillInfo(pos,skill,2)],(300,))
    def castMasterSkill(self,skill):
        self.countDown[1][skill]=15
        device.perform('Q'+'WER'[skill],(300,300))
        if self.masterSkill[skill][2]:
            if skill==2 and self.masterSkill[2][3]:
                if self.masterSkill[2][2]-1 not in self.servant or self.masterSkill[2][3]-1 in self.servant:return device.perform('\xBB',(300,))
                p=self.servant.index(self.masterSkill[2][2]-1)
                device.perform(('TYUIOP'[p],'TYUIOP'[self.masterSkill[2][3]-max(self.servant)+1],'Z'),(300,300,2600))
                self.orderChange[self.masterSkill[2][2]-1],self.orderChange[self.masterSkill[2][3]-1]=self.orderChange[self.masterSkill[2][3]-1],self.orderChange[self.masterSkill[2][2]-1]
                device.perform('\x08',(2300,))
                while not Detect().isTurnBegin():pass
                self.friend=Detect(.5).isServantFriend()
                Detect.cache.setupServantDead(self.friend)
            elif t:=Detect(.5).getSkillTargetCount():device.perform(['3333','2244','3234'][t-1][self.masterSkill[skill][2]],(300,))
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
                device.press('\x67')
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
            device.perform('\xBB\x08',(100,100))
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
                    device.press('8')
                    if Detect(.7,.3).isApEmpty()and not self.eatApple():return
                    self.chooseFriend()
                    while not Detect(0,.3).isBattleBegin():pass
                    if self.teamIndex and Detect.cache.getTeamIndex()+1!=self.teamIndex:device.perform('\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79'[self.teamIndex-1]+' ',(1000,1500))
                    self.battleProc.turnProc.teamClass=Detect().getTeamServantClass()
                    self.battleProc.turnProc.teamCard=Detect.cache.getTeamServantCard()
                    device.perform(' M',(800,10000))
                    break
                elif Detect.cache.isBattleContinue():
                    device.press('L')
                    if Detect(.7,.3).isApEmpty()and not self.eatApple():return
                    self.chooseFriend()
                    schedule.sleep(6)
                    break
                elif Detect.cache.isTurnBegin():break
                elif Detect.cache.isAddFriend():device.perform('X',(300,))
                elif Detect.cache.isSpecialDropSuspended():device.perform('\x67',(300,))
                device.press('\xBB')
            self.battleCount+=1
            logger.info(f'Battle {self.battleCount}')
            if self.battleProc():device.perform('      ',(200,200,200,200,200,200))
            else:device.perform('CIK',(500,500,500))
            schedule.checkStopLater()
    @logit(logger,logging.INFO)
    def eatApple(self):
        if self.appleCount==self.appleTotal:return device.press('Z')
        self.appleCount+=1
        device.perform('W4K8'[self.appleKind]+'L',(400,1200))
        return self.appleCount
    @logit(logger,logging.INFO)
    def chooseFriend(self):
        refresh=False
        while not Detect(0,.3).isChooseFriend():
            if Detect.cache.isNoFriend():
                if refresh:schedule.sleep(10)
                device.perform('\xBAK',(500,1000))
                refresh=True
        if not friendImg.flush():return device.press('8')
        while True:
            timer=time.time()
            while True:
                for i in(i for i,j in friendImg.items()if(lambda pos:pos and(device.touch(pos),True)[-1])(Detect.cache.findFriend(j))):
                    Turn.friendInfo=(lambda r:(lambda p:([[[-1 if p[i*4+j]=='X'else int(p[i*4+j],16)for j in range(4)]for i in range(3)],[-1 if p[i+12]=='X'else int(p[i+12],16)for i in range(2)]]))(r.group())if r else[[[-1,-1,-1,-1],[-1,-1,-1,-1],[-1,-1,-1,-1]],[-1,-1]])(re.match('([0-9X]{3}[0-9A-FX]){3}[0-9X][0-9A-FX]$',i.replace('-','')[-14:].upper()))
                    return i
                if Detect.cache.isFriendListEnd():break
                device.swipe((400,600,400,200))
                Detect(.4)
            if refresh:schedule.sleep(max(0,timer+10-time.time()))
            device.perform('\xBAK',(500,1000))
            refresh=True
            while not Detect(.2).isChooseFriend():
                if Detect.cache.isNoFriend():
                    schedule.sleep(10)
                    device.perform('\xBAK',(500,1000))
class UserScript:
    def __call__(self):return Battle(Xjbd)()
class Xjbd(Turn):
    def dispatchSkill(self):
        ...
