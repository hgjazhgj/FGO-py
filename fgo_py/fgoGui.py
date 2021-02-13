import configparser,logging,os,sys,threading
from airtest.core.android.adb import ADB
from PyQt5.QtCore import QRegExp,Qt,pyqtSignal
from PyQt5.QtGui import QIntValidator,QRegExpValidator
from PyQt5.QtWidgets import QApplication,QInputDialog,QMainWindow,QMessageBox

import fgoFunc
from fgoMainWindow import Ui_fgoMainWindow

logger=logging.getLogger('fgo.Gui')

config=type('NewConfigParser',(configparser.ConfigParser,),{'optionxform':lambda self,optionstr:optionstr})()
config.read('fgoConfig.ini')

class MyMainWindow(QMainWindow):
    signalFuncBegin=pyqtSignal()
    signalFuncEnd=pyqtSignal()
    def __init__(self,parent=None):
        super().__init__(parent)
        self.ui=Ui_fgoMainWindow()
        self.ui.setupUi(self)
        self.ui.CBX_PARTY.addItems(config.sections())
        self.ui.CBX_PARTY.setCurrentIndex(-1)
        self.ui.TXT_PARTY.setValidator(QRegExpValidator(QRegExp('10|[0-9]'),self))
        self.loadParty('DEFAULT')
        self.getDevice()
        self.thread=threading.Thread()
        self.signalFuncBegin.connect(self.funcBegin)
        self.signalFuncEnd.connect(self.funcEnd)
    def keyPressEvent(self,key):
        if self.ui.MENU_CONTROL_MAPKEY.isChecked()and not key.modifiers()&~Qt.KeypadModifier:
            try:fgoFunc.base.press(chr(key.nativeVirtualKey()))
            except KeyError:pass
    def closeEvent(self,event):
        if self.thread.is_alive()and QMessageBox.warning(self,'关闭','战斗正在进行,确认关闭?',QMessageBox.Yes|QMessageBox.No)!=QMessageBox.Yes:
            event.ignore()
            return
        fgoFunc.terminateFlag=True
        if not self.thread._started:self.thread.join()
        event.accept()
    def runFunc(self,func,*args,**kwargs):
        if not fgoFunc.base.serialno:return QMessageBox.critical(self,'错误','未连接设备')
        def f():
            try:
                fgoFunc.suspendFlag=False
                fgoFunc.terminateFlag=False
                fgoFunc.tobeTerminatedFlag=-1
                fgoFunc.fuse.reset()
                self.signalFuncBegin.emit()
                self.applyAll()
                func(*args,**kwargs)
            except Exception as e:logger.exception(e)
            finally:
                self.signalFuncEnd.emit()
                QApplication.beep()
        self.thread=threading.Thread(target=f,name='BattleFunc')
        self.thread.start()
    def funcBegin(self):
        self.ui.BTN_ONEBATTLE.setEnabled(False)
        self.ui.BTN_MAIN.setEnabled(False)
        self.ui.BTN_USER.setEnabled(False)
        self.ui.BTN_PAUSE.setEnabled(True)
        self.ui.BTN_PAUSE.setChecked(False)
        self.ui.BTN_STOP.setEnabled(True)
        self.ui.BTN_STOPLATER.setEnabled(True)
        self.ui.MENU_SCRIPT.setEnabled(False)
    def funcEnd(self):
        self.ui.BTN_ONEBATTLE.setEnabled(True)
        self.ui.BTN_MAIN.setEnabled(True)
        self.ui.BTN_USER.setEnabled(True)
        self.ui.BTN_PAUSE.setEnabled(False)
        self.ui.BTN_STOP.setEnabled(False)
        self.ui.BTN_STOPLATER.setChecked(False)
        self.ui.BTN_STOPLATER.setEnabled(False)
        self.ui.MENU_SCRIPT.setEnabled(True)
    def loadParty(self,x):
        self.ui.TXT_PARTY.setText(config[x]['partyIndex'])
        skillInfo=eval(config[x]['skillInfo'])
        for i,j,k in((i,j,k)for i in range(6)for j in range(3)for k in range(3)):eval(f'self.ui.TXT_SKILL_{i}_{j}_{k}.setText("{skillInfo[i][j][k]}")')
        houguInfo=eval(config[x]['houguInfo'])
        for i,j in((i,j)for i in range(6)for j in range(2)):eval(f'self.ui.TXT_HOUGU_{i}_{j}.setText("{houguInfo[i][j]}")')
        dangerPos=eval(config[x]['dangerPos'])
        for i in range(3):eval(f'self.ui.TXT_DANGER_{i}.setText("{dangerPos[i]}")')
        eval(f'self.ui.RBT_FRIEND_{config[x]["friendPos"]}.setChecked(True)')
        masterSkill=eval(config[x]['masterSkill'])
        for i,j in((i,j)for i in range(3)for j in range(4if i==2else 3)):eval(f'self.ui.TXT_MASTER_{i}_{j}.setText("{masterSkill[i][j]}")')
    def saveParty(self):
        if not self.ui.CBX_PARTY.currentText():return
        config[self.ui.CBX_PARTY.currentText()]={
            'partyIndex':self.ui.TXT_PARTY.text(),
            'skillInfo':str([[[int((lambda self:eval(f'self.ui.TXT_SKILL_{i}_{j}_{k}.text()'))(self))for k in range(3)]for j in range(3)]for i in range(6)]).replace(' ',''),
            'houguInfo':str([[int((lambda self:eval(f'self.ui.TXT_HOUGU_{i}_{j}.text()'))(self))for j in range(2)]for i in range(6)]).replace(' ',''),
            'dangerPos':str([int((lambda self:eval(f'self.ui.TXT_DANGER_{i}.text()'))(self))for i in range(3)]).replace(' ',''),
            'friendPos':self.ui.BTG_FRIEND.checkedButton().objectName()[-1],
            'masterSkill':str([[int((lambda self:eval(f'self.ui.TXT_MASTER_{i}_{j}.text()'))(self))for j in range(4if i==2else 3)]for i in range(3)]).replace(' ','')}
        with open('fgoConfig.ini','w')as f:config.write(f)
    def resetParty(self):self.loadParty('DEFAULT')
    def getDevice(self):
        text,ok=(lambda adbList:QInputDialog.getItem(self,'选取设备','在下拉列表中选择一个设备',adbList,adbList.index(fgoFunc.base.serialno)if fgoFunc.base.serialno and fgoFunc.base.serialno in adbList else 0,True,Qt.WindowStaysOnTopHint))([i for i,j in ADB().devices()if j=='device'])
        if ok and text and text!=fgoFunc.base.serialno:fgoFunc.base=fgoFunc.Base(text)
    def adbConnect(self):
        text,ok=QInputDialog.getText(self,'连接设备','远程设备地址',text='localhost:5555')
        if ok and text:ADB(text)
    def refreshDevice(self):fgoFunc.base=fgoFunc.Base(fgoFunc.base.serialno)
    def checkCheck(self):fgoFunc.Check().show()if fgoFunc.base.serialno else QMessageBox.critical(self,'错误','未连接设备')
    def applyAll(self):
        fgoFunc.partyIndex=int(self.ui.TXT_PARTY.text())
        fgoFunc.skillInfo=[[[int((lambda self:eval(f'self.ui.TXT_SKILL_{i}_{j}_{k}.text()'))(self))for k in range(3)]for j in range(3)]for i in range(6)]
        fgoFunc.houguInfo=[[int((lambda self:eval(f'self.ui.TXT_HOUGU_{i}_{j}.text()'))(self))for j in range(2)]for i in range(6)]
        fgoFunc.dangerPos=[int((lambda self:eval(f'self.ui.TXT_DANGER_{i}.text()'))(self))for i in range(3)]
        fgoFunc.friendPos=int(self.ui.BTG_FRIEND.checkedButton().objectName()[-1])
        fgoFunc.masterSkill=[[int((lambda self:eval(f'self.ui.TXT_MASTER_{i}_{j}.text()'))(self))for j in range(4if i==2else 3)]for i in range(3)]
    def runOneBattle(self):self.runFunc(fgoFunc.battle)
    def runUser(self):self.runFunc(fgoFunc.userScript)
    def runGacha(self):self.runFunc(fgoFunc.gacha)
    def runJackpot(self):self.runFunc(fgoFunc.jackpot)
    def runMailFiltering(self):self.runFunc(fgoFunc.mailFiltering)
    def runMain(self):
        text,ok=QInputDialog.getItem(self,'肝哪个','在下拉列表中选择战斗函数',['battle','userScript'])
        if ok and text:self.runFunc(fgoFunc.main,self.ui.TXT_APPLE.value(),self.ui.CBX_APPLE.currentIndex(),eval('fgoFunc.'+text))
    def pause(self):fgoFunc.suspendFlag=not fgoFunc.suspendFlag
    def stop(self):fgoFunc.terminateFlag=True
    def stopLater(self,x):
        if x:
            text,ok=QInputDialog.getInt(self,'输入','剩余的战斗数量',0,0,1919810,1)
            if ok:fgoFunc.tobeTerminatedFlag=text
            else:self.ui.BTN_STOPLATER.setChecked(False)
        else:fgoFunc.tobeTerminatedFlag=-1
    def explorerHere(self):os.startfile('.')
    def pwsHere(self):os.system('start PowerShell -NoLogo')
    def stayOnTop(self):
        self.setWindowFlags(self.windowFlags()^Qt.WindowStaysOnTopHint)
        self.show()
    def mapKey(self,x):
        if x and not fgoFunc.base.serialno:
            self.ui.MENU_CONTROL_MAPKEY.setChecked(False)
            return QMessageBox.critical(self,'错误','未连接设备')
    def exec(self):
        s=QApplication.clipboard().text()
        if QMessageBox.information(self,'exec',s,QMessageBox.Ok|QMessageBox.Cancel)!=QMessageBox.Ok:return
        try:exec(s)
        except BaseException as e:logger.exception(e)
    def about(self):QMessageBox.about(self,'关于','''
<h2>FGO全自动脚本</h2>
<table border="0">
  <tr>
    <td>当前版本</td>
    <td>v4.9.9</td>
  </tr>
  <tr>
    <td>作者</td>
    <td>hgjazhgj</td>
  </tr>
  <tr>
    <td>项目地址</td>
    <td><a href="https://github.com/hgjazhgj/FGO-py">https://github.com/hgjazhgj/FGO-py</a></td>
  </tr>
  <tr>
    <td>电子邮箱</td>
    <td><a href="mailto:huguangjing0411@geektip.cc">huguangjing0411@geektip.cc</a></td>
  </tr>
</table>
<!-- 都看到这里了真的不考虑给点钱吗... -->
这是我的支付宝收款码,请给我打钱,一分钱也行<br/>
<img src="data:image/bmp;base64,Qk2yAAAAAAAAAD4AAAAoAAAAHQAAAB0AAAABAAEAAAAAAHQAAAB0EgAAdBIAAAAAAAAAAAAA6KAAAP///wABYWKofU/CKEV/Zt
BFXEMwRbiQUH2a5yABj+Uo/zf3AKDtsBjeNa7YcUYb2MrQ04jEa/Ioh7TO6BR150Djjo3ATKgPmGLjdfDleznImz0gcA19mxD/rx/4AVVUAH2zpfBFCgUQRSgtEEVjdRB9
/R3wATtkAA==" height="290" width="290"/><br/>
这是我的微信收款码,请给我打钱,一分钱也行<br/>
<img src="data:;base64,Qk2yAAAAAAAAAD4AAAAoAAAAHQAAAB0AAAABAAEAAAAAAHQAAAB0EgAAdBIAAAAAAAAAAAAAOKsiAP///wABNLhYfVLBqEUYG0
hFcn7gRS8QAH2Pd2ABQiVY/x1nMFWzcFhidNUwaXr3GEp1khDJzDfAuqx06ChC9hhPvmIQMJX3SCZ13ehlXB9IVtJQUAQreqj/jv/4AVVUAH0iFfBFuxUQRRAlEEX2fRB9
Wl3wAdBsAA" height="290" width="290"/>
''')

if __name__=='__main__':
    app=QApplication(sys.argv)
    myWin=MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
