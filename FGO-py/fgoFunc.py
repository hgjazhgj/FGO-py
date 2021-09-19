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
__version__='v7.3.0'
import logging,re,time,cv2,numpy
from itertools import permutations
from fgoAndroid import Android
from fgoCheck import Check
from fgoControl import control,ScriptTerminate
from fgoFuse import fuse
from fgoImageListener import ImageListener
from fgoLogging import getLogger,logit
logger=getLogger('Func')
friendImg=ImageListener('fgoImage/friend/')
mailFilterImg=ImageListener('fgoImage/mailFilter/')
dropFilterImg=ImageListener('fgoImage/dropFilter/')
class Device(Android):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        Check.device=self
device=Device()

def gacha():
    while fuse.value<30:
        if Check().isGacha():device.perform('MK',(200,2700))
        device.press('\xDC')
def jackpot():
    while fuse.value<50:
        if Check().isNextJackpot():device.perform('0KJ',(600,2400,500))
        for _ in range(40):device.press('2')
def mailFiltering():
    if not mailFilterImg.flush():return
    while not Check(1).isListEnd((1406,1018)):
        if not any((lambda pos:pos and(device.touch(pos),True)[-1])(Check.cache.find(i[1],threshold=.016))for i in mailFilterImg.items()):device.swipe((400,900,400,300))
class Battle:
    skillInfo=[[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,0]]]
    houguInfo=[[1,1],[1,1],[1,1],[1,1],[1,1],[1,1]]
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
                skill,newPortrait=Check.cache.isSkillReady(),Check.cache.getPortrait()
                Check.cache.getHP(),Check.cache.getNP()
                if self.turn==1:self.stageTotal=Check.cache.getStageTotal()
                else:self.servant=(lambda m,p:[m+p.index(i)+1if i in p else self.servant[i]for i in range(3)])(max(self.servant),[i for i in range(3)if self.servant[i]<6and cv2.matchTemplate(newPortrait[i],portrait[i],cv2.TM_SQDIFF_NORMED)[0][0]>.04])
                if self.stageTurn==1:device.perform('\x67\x68\x69'[numpy.argmax(Check.cache.getEnemyHP())]+'\xDC',(250,500))
                portrait=newPortrait
                logger.info(f'Turn {self.turn} Stage {self.stage} StageTurn {self.stageTurn} {self.servant}')
                for i,j in((i,j)for i in range(3)if self.servant[i]<6for j in range(3)if skill[i][j]and self.skillInfo[self.orderChange[self.servant[i]]][j][0]and min(self.skillInfo[self.orderChange[self.servant[i]]][j][0],self.stageTotal)<<8|self.skillInfo[self.orderChange[self.servant[i]]][j][1]<=self.stage<<8|self.stageTurn):
                    device.perform(('ASD','FGH','JKL')[i][j],(300,))
                    if self.skillInfo[self.orderChange[self.servant[i]]][j][2]:device.perform('234'[self.skillInfo[self.orderChange[self.servant[i]]][j][2]-1],(300,))
                    control.sleep(2.3)
                    while not Check().isTurnBegin():pass
                for i in(i for i in range(3)if self.stage==min(self.masterSkill[i][0],self.stageTotal)and self.stageTurn==self.masterSkill[i][1]):
                    device.perform('Q'+'WER'[i],(300,300))
                    if self.masterSkill[i][2]:
                        if i==2and self.masterSkill[2][3]:
                            if self.masterSkill[2][2]-1not in self.servant or self.masterSkill[2][3]-1in self.servant:
                                device.perform('\xDC',(300,))
                                continue
                            device.perform(('TYUIOP'[self.servant.index(self.masterSkill[2][2]-1)],'TYUIOP'[self.masterSkill[2][3]-max(self.servant)+1],'Z'),(300,300,2600))
                            self.orderChange[self.masterSkill[2][2]-1],self.orderChange[self.masterSkill[2][3]-1]=self.orderChange[self.masterSkill[2][3]-1],self.orderChange[self.masterSkill[2][2]-1]
                            control.sleep(2.3)
                            while not Check().isTurnBegin():pass
                            portrait=Check(.5).getPortrait()
                            for j in(j for j in range(3)if self.skillInfo[self.masterSkill[2][3]-1][j][0]and min(self.skillInfo[self.masterSkill[2][3]-1][j][0],self.stageTotal)<<8|self.skillInfo[self.masterSkill[2][3]-1][j][1]<=self.stage<<8|self.stageTurn):
                                device.perform(('ASD','FGH','JKL')[self.servant.index(self.masterSkill[2][2]-1)][j],(300,))
                                if self.skillInfo[self.masterSkill[2][3]-1][j][2]:device.perform('234'[self.skillInfo[self.masterSkill[2][3]-1][j][2]-1],(300,))
                                control.sleep(2.3)
                                while not Check().isTurnBegin():pass
                            continue
                        device.perform('234'[self.masterSkill[i][2]-1],(300,))
                    control.sleep(2.3)
                    while not Check().isTurnBegin():pass
                device.perform(' ',(2100,))
                device.perform(self.selectCard(),(270,270,2270,1270,6000))
            elif Check.cache.isBattleFinished():
                logger.info('Battle Finished')
                for i in(i for i,j in dropFilterImg.items()if Check.cache.find(j)):
                    control.checkSpecialDrop()
                    logger.warning(f'Special drop {i}')
                    Check.cache.save('fgoLogs/SpecialDrop')
                    break
                return True
            elif Check.cache.isBattleDefeated():
                logger.warning('Battle Defeated')
                return False
            device.press('\xDC')
    @logit(logger,logging.INFO)
    def selectCard(self):return''.join((lambda hougu,sealed,color,resist:['678'[i]for i in sorted((i for i in range(3)if hougu[i]),key=lambda x:-self.houguInfo[self.orderChange[self.servant[x]]][1])]+['12345'[i]for i in sorted(range(5),key=(lambda x:-color[x]*resist[x]*(not sealed[x])))]if any(hougu)else(lambda group:['12345'[i]for i in(lambda choice:choice+tuple({0,1,2,3,4}-set(choice)))(logger.debug('cardRank'+','.join(('  'if i%5else'\n')+f'({j}, {k:5.2f})'for i,(j,k)in enumerate(sorted([(card,(lambda colorChain,firstCardBonus:sum((firstCardBonus+[1.,1.2,1.4][i]*color[j])*resist[j]*(not sealed[j])for i,j in enumerate(card))+(not(sealed[card[0]]or sealed[card[1]]or sealed[card[2]]))*(4.8*colorChain+(firstCardBonus+1.)*(3.5if colorChain else 2.)*(group[card[0]]==group[card[1]]==group[card[2]])*resist[card[0]]))(color[card[0]]==color[card[1]]==color[card[2]],.5*(color[card[0]]==1.5)))for card in permutations(range(5),3)],key=lambda x:-x[1]))))or max(permutations(range(5),3),key=lambda card:(lambda colorChain,firstCardBonus:sum((firstCardBonus+[1.,1.2,1.4][i]*color[j])*resist[j]*(not sealed[j])for i,j in enumerate(card))+(not(sealed[card[0]]or sealed[card[1]]or sealed[card[2]]))*(5.*colorChain+(firstCardBonus+1.)*(3.5if colorChain else 2.)*(group[card[0]]==group[card[1]]==group[card[2]])*resist[card[0]]))(color[card[0]]==color[card[1]]==color[card[2]],.5*(color[card[0]]==1.5))))])(Check.cache.getCardGroup()))([self.servant[i]<6and j and self.houguInfo[self.orderChange[self.servant[i]]][0]and self.stage>=min(self.houguInfo[self.orderChange[self.servant[i]]][0],self.stageTotal)for i,j in enumerate(Check().isHouguReady())],Check.cache.isCardSealed(),Check.cache.getCardColor(),Check.cache.getCardResist()))
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
                    device.press('8')
                    if Check(.7,.3).isApEmpty()and not self.eatApple():return
                    self.chooseFriend()
                    while not Check().isBattleBegin():pass
                    if self.teamIndex and Check.cache.getTeamIndex()!=self.teamIndex:device.perform('\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79'[self.teamIndex-1]+' ',(1000,400))
                    device.perform(' 8M',(800,800,10000))
                    break
                elif Check.cache.isBattleContinue():
                    try:control.checkTerminateLater()
                    except ScriptTerminate:
                        device.press('F')
                        raise
                    device.press('K')
                    if Check(.7,.3).isApEmpty()and not self.eatApple():return
                    self.chooseFriend()
                    control.sleep(6)
                    break
                elif Check.cache.isAddFriend():device.press('X')
                elif Check.cache.isSpecialDrop():
                    control.checkSpecialDrop()
                    logger.warning('Special drop')
                    Check.cache.save('fgoLogs/SpecialDrop')
                    device.press('\x67')
                device.press(' ')
            self.battleCount+=1
            logger.info(f'Battle {self.battleCount}')
            if not self.battleFunc():
                control.checkDefeated()
                device.perform('BIK',(500,500,500))
    @logit(logger,logging.INFO)
    def eatApple(self):
        if self.appleCount==self.appleTotal:return device.press('Z')
        self.appleCount+=1
        device.perform('W4K8'[self.appleKind]+'L',(400,1200))
        return self.appleCount
    @logit(logger,logging.INFO)
    def chooseFriend(self):
        refresh=False
        while not Check(.2).isChooseFriend():
            if Check.cache.isNoFriend():
                if refresh:control.sleep(10)
                device.perform('\xBAK',(500,1000))
                refresh=True
        if not friendImg.flush():return device.press('8')
        while True:
            timer=time.time()
            while True:
                for i in(i for i,j in friendImg.items()if(lambda pos:pos and(device.touch(pos),True)[-1])(Check.cache.find(j))):
                    Battle.skillInfo[self.friendPos],Battle.houguInfo[self.friendPos]=(lambda r:(lambda p:([[Battle.skillInfo[self.friendPos][i][j]if p[i*3+j]=='x'else int(p[i*3+j])for j in range(3)]for i in range(3)],[Battle.houguInfo[self.friendPos][i]if p[i+9]=='x'else int(p[i+9])for i in range(2)]))(r.group())if r else(Battle.skillInfo[self.friendPos],Battle.houguInfo[self.friendPos]))(re.search('[0-9x]{11}$',i))
                    return i
                if Check.cache.isListEnd((1882,1064)):break
                device.swipe((800,900,800,300))
                Check(.4)
            if refresh:control.sleep(max(0,timer+10-time.time()))
            device.perform('\xBAK',(500,1000))
            refresh=True
            while not Check(.2).isChooseFriend():
                if Check.cache.isNoFriend():
                    control.sleep(10)
                    device.perform('\xBAK',(500,1000))
def userScript():
    # BX WCBA 极地用迦勒底制服
    while not Check(0,.2).isTurnBegin():pass
    #                                    A    D    F    2    G   H    2   J   2    K    L    2   Q   E   2     _   6   5    4
    device.perform('ADF2GH2J2KL2QE2 654',(3000,3000,350,3000,3000,350,3000,350,3000,3000,350,3000,300,350,3000,2400,350,350,10000))
    while not Check(0,.2).isBattleFinished():assert not Check.cache.isTurnBegin()
    return True
