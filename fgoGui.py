from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox,QInputDialog
from PyQt5.QtCore import Qt,pyqtSignal
from airtest.core.android.adb import ADB
import os,sys,cv2,threading,configparser,logging,playsound,random

from ui.fgoMainWindow import Ui_fgoMainWindow
import fgoFunc

logger=logging.getLogger('fgoFunc.fgoGui')
logger.name='fgoGui'

class NewConfigParser(configparser.ConfigParser):
    def optionxform(self,optionstr):return optionstr
config=NewConfigParser()
config.read('fgoConfig.ini')

def choice(x):
    while True:
        random.shuffle(x)
        yield from x
soundName=choice(os.listdir('sound'))

class MyMainWindow(QMainWindow):
    signalFuncBegin=pyqtSignal()
    signalFuncEnd=pyqtSignal()
    def __init__(self,parent=None):
        super().__init__(parent)
        self.ui=Ui_fgoMainWindow()
        self.ui.setupUi(self)
        self.ui.CBX_PARTY.addItems(config.sections())
        self.ui.CBX_PARTY.setCurrentIndex(-1)
        self.loadParty('DEFAULT')
        self.serialno=fgoFunc.base.serialno
        self.IMG_FRIEND=fgoFunc.IMG_FRIEND
        self.signalFuncBegin.connect(self.funcBegin)
        self.signalFuncEnd.connect(self.funcEnd)
    def runFunc(self,func,*args,**kwargs):
        if self.serialno is None:
            QMessageBox.critical(self,'Error','无设备连接',QMessageBox.Ok)
            return
        self.applyAll()
        def f():
            try:
                self.signalFuncBegin.emit()
                func(*args,**kwargs)
            except Exception as e:logger.exception(e)
            finally:
                self.signalFuncEnd.emit()
                playsound.playsound('sound/'+next(soundName))
        threading.Thread(target=f).start()
    def funcBegin(self):
        self.ui.BTN_ONEBATTLE.setEnabled(False)
        self.ui.BTN_MAIN.setEnabled(False)
        self.ui.BTN_USER.setEnabled(False)
        self.ui.MENU_SCRIPT_GACHA.setEnabled(False)
        self.ui.BTN_PAUSE.setEnabled(True)
        self.ui.BTN_STOP.setEnabled(True)
    def funcEnd(self):
        self.ui.BTN_ONEBATTLE.setEnabled(True)
        self.ui.BTN_MAIN.setEnabled(True)
        self.ui.BTN_USER.setEnabled(True)
        self.ui.MENU_SCRIPT_GACHA.setEnabled(True)
        self.ui.BTN_PAUSE.setEnabled(False)
        self.ui.BTN_STOP.setEnabled(False)
    def loadParty(self,x):
        skillInfo=eval(config[x]['skillInfo'])
        houguInfo=eval(config[x]['houguInfo'])
        dangerPos=eval(config[x]['dangerPos'])
        for i,j,k in((i,j,k)for i in range(6)for j in range(3)for k in range(3)):eval('self.ui.TXT_SKILL_'+str(i)+'_'+str(j)+'_'+str(k)+'.setText("'+str(skillInfo[i][j][k])+'")')
        for i,j in((i,j)for i in range(6)for j in range(2)):eval('self.ui.TXT_HOUGU_'+str(i)+'_'+str(j)+'.setText("'+str(houguInfo[i][j])+'")')
        for i in range(3):eval('self.ui.TXT_DANGER_'+str(i)+'.setText("'+str(dangerPos[i])+'")')
        eval('self.ui.RBT_FRIEND_'+config[x]['friendPos']+'.setChecked(True)')
        masterSkill=eval(config[x]['masterSkill'])
        for i,j in((i,j)for i in range(3)for j in range(3)):eval('self.ui.TXT_MASTER_'+str(i)+'_'+str(j)+'.setText("'+str(masterSkill[i][j])+'")')
    def saveParty(self):
        config[self.ui.CBX_PARTY.currentText()]={
            'skillInfo':str([[[int((lambda self:eval('self.ui.TXT_SKILL_'+str(i)+'_'+str(j)+'_'+str(k)+'.text()'))(self))for k in range(3)]for j in range(3)]for i in range(6)]).replace(' ',''),
            'houguInfo':str([[int((lambda self:eval('self.ui.TXT_HOUGU_'+str(i)+'_'+str(j)+'.text()'))(self))for j in range(2)]for i in range(6)]).replace(' ',''),
            'dangerPos':str([int((lambda self:eval('self.ui.TXT_DANGER_'+str(i)+'.text()'))(self))for i in range(3)]).replace(' ',''),
            'friendPos':self.ui.BTG_FRIEND.checkedButton().objectName()[-1],
            'masterSkill':str([[int((lambda self:eval('self.ui.TXT_MASTER_'+str(i)+'_'+str(j)+'.text()'))(self))for j in range(3)]for i in range(3)]).replace(' ','')}
        with open('fgoConfig.ini','w')as f:config.write(f)
    def resetParty(self):self.loadParty('DEFAULT')
    def getDevice(self):
        text,ok=(lambda adbList:QInputDialog.getItem(self,'更改安卓设备','在下拉列表中选择一个设备',adbList,adbList.index(self.serialno)if self.serialno and self.serialno in adbList else 0))([i for i,j in ADB().devices()if j=='device'])
        if ok and text:self.serialno=text
    def adbConnect(self):
        text,ok=QInputDialog.getText(self,'连接远程设备','设备地址',text='localhost:5555')
        if ok and text:ADB(text)
    def refreshDevice(self):fgoFunc.base=fgoFunc.Base(fgoFunc.base.serialno)
    def checkCheck(self):fgoFunc.Check(0).show()
    def getFriend(self):self.IMG_FRIEND=[[file[:-4],cv2.imread('image/friend/'+file)]for file in os.listdir('image/friend')if file.endswith('.png')]
    def applyAll(self):
        fgoFunc.suspendFlag=False
        fgoFunc.terminateFlag=False
        fgoFunc.fuse.reset()
        fgoFunc.skillInfo=[[[int((lambda self:eval('self.ui.TXT_SKILL_'+str(i)+'_'+str(j)+'_'+str(k)+'.text()'))(self))for k in range(3)]for j in range(3)]for i in range(6)]
        fgoFunc.houguInfo=[[int((lambda self:eval('self.ui.TXT_HOUGU_'+str(i)+'_'+str(j)+'.text()'))(self))for j in range(2)]for i in range(6)]
        fgoFunc.dangerPos=[int((lambda self:eval('self.ui.TXT_DANGER_'+str(i)+'.text()'))(self))for i in range(3)]
        fgoFunc.friendPos=int(self.ui.BTG_FRIEND.checkedButton().objectName()[-1])
        fgoFunc.masterSkill=[[int((lambda self:eval('self.ui.TXT_MASTER_'+str(i)+'_'+str(j)+'.text()'))(self))for j in range(3)]for i in range(3)]
        if self.serialno!=fgoFunc.base.serialno:fgoFunc.base=fgoFunc.Base(self.serialno)
        fgoFunc.IMG_FRIEND=self.IMG_FRIEND
    def runOneBattle(self):self.runFunc(fgoFunc.oneBattle)
    def runUser(self):self.runFunc(fgoFunc.userScript)
    def runGacha(self):self.runFunc(fgoFunc.gacha)
    def runMain(self):
        text,ok=QInputDialog.getItem(self,'肝哪个','在下拉列表中选择战斗函数',['oneBattle','userScript'],0)
        if ok and text:self.runFunc(fgoFunc.main,self.ui.TXT_APPLE.value(),self.ui.CBX_APPLE.currentIndex(),eval('fgoFunc.'+text))
    def pause(self):fgoFunc.suspendFlag=not fgoFunc.suspendFlag
    def stop(self):fgoFunc.terminateFlag=True
    def openFolder(self):os.startfile(os.getcwd())
    def stayOnTop(self):
        self.setWindowFlags(self.windowFlags()^Qt.WindowStaysOnTopHint)
        self.show()
    def about(self):QMessageBox.about(self,'关于','作者:\thgjazhgj  \n项目地址:https://github.com/hgjazhgj/FGO-py  \n联系方式:huguangjing0411@geektip.cc  \n防呆不放蠢,大力出奇迹!')

if __name__=='__main__':
    app=QApplication(sys.argv)
    myWin=MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
