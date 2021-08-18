import configparser,logging,os,sys,threading
from PyQt6.QtCore import QRegularExpression,Qt,pyqtSignal
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QApplication,QInputDialog,QMainWindow,QMessageBox

import fgoFunc
from fgoMainWindow import Ui_fgoMainWindow

logger=logging.getLogger('fgo.Gui')

config=type('NewConfigParser',(configparser.ConfigParser,),{'optionxform':lambda self,optionstr:optionstr})()
config.read('fgoTeamup.ini')

class MyMainWindow(QMainWindow):
    signalFuncBegin=pyqtSignal()
    signalFuncEnd=pyqtSignal()
    def __init__(self,parent=None):
        super().__init__(parent)
        self.ui=Ui_fgoMainWindow()
        self.ui.setupUi(self)
        self.ui.CBX_TEAM.addItems(config.sections())
        self.ui.CBX_TEAM.setCurrentIndex(-1)
        self.ui.TXT_TEAM.setValidator(QRegularExpressionValidator(QRegularExpression('10|[0-9]'),self))
        self.loadTeam('DEFAULT')
        self.getDevice()
        self.thread=threading.Thread()
        self.signalFuncBegin.connect(self.funcBegin)
        self.signalFuncEnd.connect(self.funcEnd)
    def keyPressEvent(self,key):
        if self.ui.MENU_CONTROL_MAPKEY.isChecked()and not key.modifiers()&~Qt.KeyboardModifier.KeypadModifier:
            try:fgoFunc.base.press(chr(key.nativeVirtualKey()))
            except KeyError:pass
            except Exception as e:logger.critical(e)
    def closeEvent(self,event):
        if self.thread.is_alive()and QMessageBox.warning(self,'关闭','战斗正在进行,确认关闭?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes:return event.ignore()
        fgoFunc.control.terminate()
        if not self.thread._started:self.thread.join()
        event.accept()
    def isDeviceAvaliable(self):
        if not fgoFunc.base.avaliable:
            self.ui.LBL_DEVICE.clear()
            return False
        return True
    def runFunc(self,func,*args,**kwargs):
        if not self.isDeviceAvaliable():return QMessageBox.critical(self,'错误','未连接设备')
        def f():
            try:
                self.signalFuncBegin.emit()
                self.applyAll()
                func(*args,**kwargs)
            except fgoFunc.ScriptTerminate as e:logger.critical(e)
            except BaseException as e:logger.exception(e)
            finally:
                self.signalFuncEnd.emit()
                fgoFunc.control.reset()
                fgoFunc.fuse.reset()
                QApplication.beep() # print('\a',end='')
        self.thread=threading.Thread(target=f,name=f'{getattr(func,"__qualname__",getattr(type(func),"__qualname__",repr(func)))}({",".join(repr(i)for i in args)}{","if kwargs else""}{",".join("%s=%r"%i for i in kwargs.items())})')
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
        self.ui.TXT_APPLE.setValue(0)
    def loadTeam(self,teamName):
        self.ui.TXT_TEAM.setText(config[teamName]['teamIndex'])
        getattr(self.ui,f'RBT_FRIEND_{config[teamName]["friendPos"]}').setChecked(True)
        (lambda skillInfo:[getattr(self.ui,f'TXT_SKILL_{i}_{j}_{k}').setText(str(skillInfo[i][j][k]))for i in range(6)for j in range(3)for k in range(3)])(eval(config[teamName]['skillInfo']))
        (lambda houguInfo:[getattr(self.ui,f'TXT_HOUGU_{i}_{j}').setText(str(houguInfo[i][j]))for i in range(6)for j in range(2)])(eval(config[teamName]['houguInfo']))
        (lambda dangerPos:[getattr(self.ui,f'TXT_DANGER_{i}').setText(str(dangerPos[i]))for i in range(3)])(eval(config[teamName]['dangerPos']))
        (lambda masterSkill:[getattr(self.ui,f'TXT_MASTER_{i}_{j}').setText(str(masterSkill[i]))for i in range(3)for j in range(3+(i==2))])(eval(config[teamName]['masterSkill']))
    def saveTeam(self):
        if not self.ui.CBX_TEAM.currentText():return
        config[self.ui.CBX_TEAM.currentText()]={
            'teamIndex':self.ui.TXT_TEAM.text(),
            'friendPos':self.ui.BTG_FRIEND.checkedButton().objectName()[-1],
            'skillInfo':str([[[int(getattr(self.ui,f'TXT_SKILL_{i}_{j}_{k}').text())for k in range(3)]for j in range(3)]for i in range(6)]).replace(' ',''),
            'houguInfo':str([[int(getattr(self.ui,f'TXT_HOUGU_{i}_{j}').text())for j in range(2)]for i in range(6)]).replace(' ',''),
            'dangerPos':str([int(getattr(self.ui,f'TXT_DANGER_{i}').text())for i in range(3)]).replace(' ',''),
            'masterSkill':str([[int(getattr(self.ui,f'TXT_MASTER_{i}_{j}').text())for j in range(3+(i==2))]for i in range(3)]).replace(' ','')}
        with open('fgoTeamup.ini','w')as f:config.write(f)
    def resetTeam(self):self.loadTeam('DEFAULT')
    def getDevice(self):
        text,ok=(lambda l:QInputDialog.getItem(self,'选取设备','在下拉列表中选择一个设备',l,l.index(fgoFunc.base.serialno)if fgoFunc.base.serialno and fgoFunc.base.serialno in l else 0,True,Qt.WindowType.WindowStaysOnTopHint))(fgoFunc.Base.enumDevices())
        if ok:
            if text.startswith('/'):
                try:
                    if text=='/gw':
                        import netifaces
                        text=f'{netifaces.gateways()["default"][netifaces.AF_INET][0]}:5555'
                    elif text=='/bs':
                        import winreg
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\BlueStacks_bgp64_hyperv\Guests\Android\Config')as key:text=f'127.0.0.1:{winreg.QueryValueEx(key,"BstAdbPort")[0]}'
                except Exception as e:return logger.exception(e)
            fgoFunc.base=fgoFunc.Base(text.replace(' ',''))
            self.ui.LBL_DEVICE.setText(fgoFunc.base.serialno)
    def checkCheck(self):
        if not self.isDeviceAvaliable():return QMessageBox.critical(self,'错误','未连接设备')
        try:fgoFunc.Check(0).show()
        except Exception as e:logger.exception(e)
    def applyAll(self):
        fgoFunc.Main.teamIndex=int(self.ui.TXT_TEAM.text())
        fgoFunc.Main.friendPos=int(self.ui.BTG_FRIEND.checkedButton().objectName()[-1])
        fgoFunc.Battle.skillInfo=[[[int(getattr(self.ui,f'TXT_SKILL_{i}_{j}_{k}').text())for k in range(3)]for j in range(3)]for i in range(6)]
        fgoFunc.Battle.houguInfo=[[int(getattr(self.ui,f'TXT_HOUGU_{i}_{j}').text())for j in range(2)]for i in range(6)]
        fgoFunc.Battle.dangerPos=[int(getattr(self.ui,f'TXT_DANGER_{i}').text())for i in range(3)]
        fgoFunc.Battle.masterSkill=[[int(getattr(self.ui,f'TXT_MASTER_{i}_{j}').text())for j in range(3+(i==2))]for i in range(3)]
    def runBattle(self):self.runFunc(fgoFunc.Battle())
    def runUserScript(self):self.runFunc(fgoFunc.userScript)
    def runGacha(self):self.runFunc(fgoFunc.gacha)
    def runJackpot(self):self.runFunc(fgoFunc.jackpot)
    def runMailFiltering(self):self.runFunc(fgoFunc.mailFiltering)
    def runMain(self):
        text,ok=QInputDialog.getItem(self,'肝哪个','在下拉列表中选择战斗函数',['完成战斗','用户脚本'],0,False)
        if ok and text:self.runFunc(fgoFunc.Main(self.ui.TXT_APPLE.value(),self.ui.CBX_APPLE.currentIndex(),{'完成战斗':lambda:fgoFunc.Battle()(),'用户脚本':fgoFunc.userScript}[text]))
    def pause(self,x):
        if not x and not self.isDeviceAvaliable():
            self.ui.BTN_PAUSE.setChecked(True)
            return QMessageBox.critical(self,'错误','未连接设备')
        fgoFunc.control.suspend()
    def stop(self):fgoFunc.control.terminate()
    def stopLater(self,x):
        if x:
            num,ok=QInputDialog.getInt(self,'输入','剩余的战斗数量',0,0,1919810,1)
            if ok:fgoFunc.control.terminateLater(num)
            else:self.ui.BTN_STOPLATER.setChecked(False)
        else:fgoFunc.control.terminateLater()
    def stopOnDefeated(self):fgoFunc.control.stopOnDefeated()
    def stopOnSpecialDrop(self):fgoFunc.control.stopOnSpecialDrop()
    def explorerHere(self):os.startfile('.')
    def stayOnTop(self,x):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,x)
        self.show()
    def mapKey(self,x):
        if x and not self.isDeviceAvaliable():
            self.ui.MENU_CONTROL_MAPKEY.setChecked(False)
            return QMessageBox.critical(self,'错误','未连接设备')
    def exec(self):
        s=QApplication.clipboard().text()
        if QMessageBox.information(self,'exec',s,QMessageBox.StandardButton.Ok|QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Ok:return
        try:exec(s)
        except BaseException as e:logger.exception(e)
    def about(self):QMessageBox.about(self,'关于','''
<style>
  body{font-family: "Microsoft YaHei UI Light"; font-size: 15px}
</style>
<body>
  <h1>FGO-py</h1>
  FGO全自动脚本
  <table border="0">
    <tr><td>当前版本</td><td>%s</td></tr>
    <tr><td>作者</td><td>hgjazhgj</td></tr>
    <tr><td>项目地址</td><td><a href="https://github.com/hgjazhgj/FGO-py">https://github.com/hgjazhgj/FGO-py</a></td></tr>
    <tr><td>电子邮箱</td><td><a href="mailto:huguangjing0411@geektip.cc">huguangjing0411@geektip.cc</a></td></tr>
  </table>
  <!-- 都看到这里了真的不考虑资瓷一下吗... -->
  这是我的<font color="#00A0E8">支付宝</font>/<font color="#22AB38">微信</font>收款码,请给我打钱,一分钱也行<br/>
  <img height="174" width="174" src="data:image/bmp;base64,Qk2yAAAAAAAAAD4AAAAoAAAAHQAAAB0AAAABAAEAAAAAAHQAAAB0EgAAdBIAAAAAAAAAAAAA6KAAAP///wABYWKofU/CKEV/ZtBFXEMwRbiQUH2a5yABj+Uo/zf3AKDtsBjeNa7YcUYb2MrQ04jEa/Ioh7TO6BR150Djjo3ATKgPmGLjdfDleznImz0gcA19mxD/rx/4AVVUAH2zpfBFCgUQRSgtEEVjdRB9/R3wATtkAA=="/>
  <img height="174" width="174" src="data:;base64,Qk2yAAAAAAAAAD4AAAAoAAAAHQAAAB0AAAABAAEAAAAAAHQAAAB0EgAAdBIAAAAAAAAAAAAAOKsiAP///wABNLhYfVLBqEUYG0hFcn7gRS8QAH2Pd2ABQiVY/x1nMFWzcFhidNUwaXr3GEp1khDJzDfAuqx06ChC9hhPvmIQMJX3SCZ13ehlXB9IVtJQUAQreqj/jv/4AVVUAH0iFfBFuxUQRRAlEEX2fRB9Wl3wAdBsAA"/>
</body>
'''%fgoFunc.__version__)
    def license(self):os.system(f'start notepad {"LICENSE"if os.path.isfile("LICENSE")else"../LICENSE"}')

if __name__=='__main__':
    app=QApplication(sys.argv)
    myWin=MyMainWindow()
    myWin.show()
    sys.exit(app.exec())
