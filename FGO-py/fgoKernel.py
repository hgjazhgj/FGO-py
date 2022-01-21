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
from fgoAndroid import Android
from fgoConnectHelper import convert
from fgoDetect import Detect
from fgoFuse import fuse
from fgoImageListener import ImageListener
from fgoLogging import getLogger,logit
from fgoSchedule import ScriptTerminate,schedule
from fgoWsa import Wsa

logger=getLogger('Core')
friendImg=ImageListener('fgoImage/friend/')
mailImg=ImageListener('fgoImage/mail/')
class Device(Android):
    def __new__(cls,name=None,*args,**kwargs):
        result=Wsa()if name and name.lower()=='wsa'else super().__new__(cls)
        Detect.device=result
        return result
    def __init__(self,name=None,*args,**kwargs):
        name=convert(name)
        super().__init__(name,*args,**kwargs)
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
        device.press('\xBB')
def jackpot():
    while fuse.value<50:
        if Detect().isNextJackpot():device.perform('\xDCKJ',(600,2400,500))
        for _ in range(40):device.press('2')
def mail():
    if not mailImg.flush():return
    Detect().setupMailDone()
    while True:
        while any((pos:=Detect.cache.findMail(i[1]))and(device.touch(pos),True)[-1]for i in mailImg.items()):
            while not Detect().isMailDone():pass
        device.swipe((400,900,400,300))
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
class Battle:
    skillInfo=[[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]]]
    houguInfo=[[1,7],[1,7],[1,7],[1,7],[1,7],[1,7]]
    masterSkill=[[0,0,0,7],[0,0,0,7],[0,0,0,0,7]]
    def __init__(self):
        Battle.friendInfo=[[[-1,-1,-1,-1],[-1,-1,-1,-1],[-1,-1,-1,-1]],[-1,-1]]
        self.turn=0
        self.stage=0
        self.stageTurn=0
        self.servant=[0,1,2]
        self.orderChange=[0,1,2,3,4,5]
        self.masterSkillReady=[True,True,True]
        self.rainbowBox=False
    def __call__(self):
        while True:
            if Detect(0,.3).isTurnBegin():
                self.turn+=1
                self.stage,self.stageTurn=[t:=Detect(.2).getStage(),1+self.stageTurn*(self.stage==t)]
                self.friend=Detect.cache.isServantFriend()
                Detect.cache.getHP(),Detect.cache.getNP()
                if self.turn==1:
                    Detect.cache.setupServantDead(self.friend)
                    self.stageTotal=Detect.cache.getStageTotal()
                else:self.servant=(lambda m,p:[m+p.index(i)+1 if i in p else self.servant[i]for i in range(3)])(max(self.servant),(lambda dead:[i for i in range(3)if self.servant[i]<6 and dead[i]])(Detect.cache.isServantDead(self.friend)))
                logger.info(f'Turn {self.turn} Stage {self.stage} StageTurn {self.stageTurn} {self.servant}')
                if self.stageTurn==1:device.perform('\x67\x68\x69'[numpy.argmax(Detect.cache.getEnemyHP())]+'\xBB',(800,500))
                while(s:=(lambda skill:[(self.getSkillInfo(i,j,3),0,(i,j))for i in range(3)if self.servant[i]<6 for j in range(3)if skill[i][j]and(t:=self.getSkillInfo(i,j,0))and min(t,self.stageTotal)<<8|self.getSkillInfo(i,j,1)<=self.stage<<8|self.stageTurn])(Detect.cache.isSkillReady())+[(self.masterSkill[i][-1],1,i)for i in range(3)if self.masterSkillReady[i]and self.stage==min(self.masterSkill[i][0],self.stageTotal)and self.stageTurn==self.masterSkill[i][1]]):
                    _,cast,arg=min(s,key=lambda x:x[0])
                    if cast==0:
                        device.perform(('ASD','FGH','JKL')[arg[0]][arg[1]],(300,))
                        if t:=self.getSkillInfo(*arg,2):device.perform('234'[t-1],(300,))
                    elif cast==1:
                        self.masterSkillReady[arg]=False
                        device.perform('Q'+'WER'[arg],(300,300))
                        if self.masterSkill[arg][2]:
                            if arg==2 and self.masterSkill[2][3]:
                                if self.masterSkill[2][2]-1 not in self.servant or self.masterSkill[2][3]-1 in self.servant:
                                    device.perform('\xBB',(300,))
                                    continue
                                p=self.servant.index(self.masterSkill[2][2]-1)
                                device.perform(('TYUIOP'[p],'TYUIOP'[self.masterSkill[2][3]-max(self.servant)+1],'Z'),(300,300,2600))
                                self.orderChange[self.masterSkill[2][2]-1],self.orderChange[self.masterSkill[2][3]-1]=self.orderChange[self.masterSkill[2][3]-1],self.orderChange[self.masterSkill[2][2]-1]
                                device.perform('\x08',(2300,))
                                while not Detect().isTurnBegin():pass
                                self.friend=Detect(.5).isServantFriend()
                                Detect.cache.setupServantDead(self.friend)
                                continue
                            device.perform('234'[self.masterSkill[arg][2]-1],(300,))
                    device.perform('\x08',(2300,))
                    while not Detect().isTurnBegin():pass
                    Detect(.5)
                device.perform(' ',(2100,))
                device.perform(self.selectCard(),(300,300,2300,1300,6000))
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
                    logger.warning('Special drop')
                    Detect.cache.save('fgoLog/SpecialDrop')
                return self.turn
            elif Detect.cache.isBattleDefeated():
                logger.warning('Battle Defeated')
                schedule.checkDefeated()
                return 0
            device.perform('\xBB\x08',(100,100))
    @logit(logger,logging.INFO)
    def selectCard(self):return''.join((lambda hougu,sealed,color,resist,critical:['678'[i]for i in sorted((i for i in range(3)if hougu[i]),key=lambda x:self.getHouguInfo(x,1))]+['12345'[i]for i in sorted(range(5),key=(lambda x:-color[x]*resist[x]*(not sealed[x])*(1+critical[x])))]if any(hougu)else(lambda group:['12345'[i]for i in(lambda choice:choice+tuple({0,1,2,3,4}-set(choice)))(logger.debug('cardRank'+','.join(('  'if i%5 else'\n')+f'({j}, {k:5.2f})'for i,(j,k)in enumerate(sorted([(card,(lambda colorChain,firstCardBonus:sum((firstCardBonus+[1.,1.2,1.4][i]*color[j])*(1+critical[j])*resist[j]*(not sealed[j])for i,j in enumerate(card))+(not any(sealed[i]for i in card))*(4.8*colorChain+(firstCardBonus+1.)*(3 if colorChain else 1.8)*(len({group[i]for i in card})==1)*resist[card[0]]))(len({color[i]for i in card})==1,.3*(color[card[0]]==1.1)))for card in permutations(range(5),3)],key=lambda x:-x[1]))))or max(permutations(range(5),3),key=lambda card:(lambda colorChain,firstCardBonus:sum((firstCardBonus+[1.,1.2,1.4][i]*color[j])*(1+critical[j])*resist[j]*(not sealed[j])for i,j in enumerate(card))+(not any(sealed[i]for i in card))*(4.8*colorChain+(firstCardBonus+1.)*(3 if colorChain else 1.8)*(len({group[i]for i in card})==1)*resist[card[0]]))(len({color[i]for i in card})==1,.3*(color[card[0]]==1.1))))])(Detect.cache.getCardGroup()))([self.servant[i]<6 and j and(t:=self.getHouguInfo(i,0))and self.stage>=min(t,self.stageTotal)for i,j in enumerate(Detect().isHouguReady())],Detect.cache.isCardSealed(),Detect.cache.getCardColor(),Detect.cache.getCardResist(),Detect.cache.getCriticalRate()))
    def getSkillInfo(self,pos,skill,arg):return self.friendInfo[0][skill][arg]if self.friend[pos]and self.friendInfo[0][skill][arg]>=0 else self.skillInfo[self.orderChange[self.servant[pos]]][skill][arg]
    def getHouguInfo(self,pos,arg):return self.friendInfo[1][arg]if self.friend[pos]and self.friendInfo[1][arg]>=0 else self.houguInfo[self.orderChange[self.servant[pos]]][arg]
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
            self.battleFunc=self.battleClass()
            while True:
                if Detect(.3,.3).isMainInterface():
                    device.press('8')
                    if Detect(.7,.3).isApEmpty()and not self.eatApple():return
                    self.chooseFriend()
                    while not Detect().isBattleBegin():pass
                    if self.teamIndex and Detect.cache.getTeamIndex()+1!=self.teamIndex:device.perform('\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79'[self.teamIndex-1]+' ',(1000,400))
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
            if self.battleFunc():device.press(' ')
            else:device.perform('BIK',(500,500,500))
            schedule.checkTerminateLater()
    @logit(logger,logging.INFO)
    def eatApple(self):
        if self.appleCount==self.appleTotal:return device.press('Z')
        self.appleCount+=1
        device.perform('W4K8'[self.appleKind]+'L',(400,1200))
        return self.appleCount
    @logit(logger,logging.INFO)
    def chooseFriend(self):
        refresh=False
        while not Detect(.2).isChooseFriend():
            if Detect.cache.isNoFriend():
                if refresh:schedule.sleep(10)
                device.perform('\xBAK',(500,1000))
                refresh=True
        if not friendImg.flush():return device.press('8')
        while True:
            timer=time.time()
            while True:
                for i in(i for i,j in friendImg.items()if(lambda pos:pos and(device.touch(pos),True)[-1])(Detect.cache.findFriend(j))):
                    Battle.friendInfo=(lambda r:(lambda p:([[[-1 if p[i*4+j]=='X'else int(p[i*4+j],16)for j in range(4)]for i in range(3)],[-1 if p[i+12]=='X'else int(p[i+12],16)for i in range(2)]]))(r.group())if r else[[[-1,-1,-1,-1],[-1,-1,-1,-1],[-1,-1,-1,-1]],[-1,-1]])(re.match('([0-9X]{3}[0-9A-FX]){3}[0-9X][0-9A-FX]$',i.replace('-','')[-14:].upper()))
                    return i
                if Detect.cache.isFriendListEnd():break
                device.swipe((800,900,800,300))
                Detect(.4)
            if refresh:schedule.sleep(max(0,timer+10-time.time()))
            device.perform('\xBAK',(500,1000))
            refresh=True
            while not Detect(.2).isChooseFriend():
                if Detect.cache.isNoFriend():
                    schedule.sleep(10)
                    device.perform('\xBAK',(500,1000))
class UserScript:
    def __call__(self):
        while not Detect(0,.3).isTurnBegin():device.press('\xBB')
        # # BX WCBA 极地用迦勒底制服
        # #                                      A    D    F    2    G   H    2   J   2    K    L    2   Q   E   2     _   6   5    4
        # device.perform('ADF2GH2J2KL2QE2 654',(3000,3000,350,3000,3000,350,3000,350,3000,3000,350,3000,300,350,3000,2400,350,350,10000))
        # # Hikari Nobu      Kintoki wcba atorasu
        # #                                   Q   E    2    A    F    2    G   H    2   J    2    K   L    2    _   6   5    4
        # device.perform('QE2AF2GH2J2KL2 654',(300,350,3000,3000,350,3000,3000,350,3000,350,3000,3000,350,3000,2400,350,350,10000))
        device.perform('QE2',(300,350,3000))
        return Battle()()
