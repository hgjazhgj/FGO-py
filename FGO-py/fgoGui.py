import json,os,sys,time
from threading import Thread
from PyQt6.QtCore import Qt,pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication,QInputDialog,QMainWindow,QMenu,QMessageBox,QStyle,QSystemTrayIcon
import fgoKernel
from fgoIniParser import IniParser
from fgoMainWindow import Ui_fgoMainWindow
from fgoServerChann import ServerChann
logger=fgoKernel.getLogger('Gui')

class Config:
    def __init__(self,link=None):
        with open('fgoConfig.json')as f:self.config=json.load(f)
        self.link=link if isinstance(link,dict)else{}
        for configName,(menuItem,scheduleFunc)in self.link.items():
            menuItem.setChecked(bool(self.config[configName]))
            if callable(scheduleFunc):scheduleFunc(self.config[configName])
    def __getitem__(self,key):return self.config[key]
    def __setitem__(self,key,value):
        self.config[key]=value
        # self.link[key][0].setChecked(bool(value))
        if callable(self.link[key][1]):self.link[key][1](value)
    def save(self):
        with open('fgoConfig.json','w')as f:json.dump(self.config,f,indent=4)

class MyMainWindow(QMainWindow,Ui_fgoMainWindow):
    signalFuncBegin=pyqtSignal()
    signalFuncEnd=pyqtSignal(object)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.TRAY=QSystemTrayIcon(self)
        self.TRAY.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        self.TRAY.setToolTip('FGO-py')
        self.MENU_TRAY=QMenu(self)
        self.MENU_TRAY_QUIT=QAction('退出',self.MENU_TRAY)
        self.MENU_TRAY.addAction(self.MENU_TRAY_QUIT)
        self.MENU_TRAY_FORCEQUIT=QAction('强制退出',self.MENU_TRAY)
        self.MENU_TRAY.addAction(self.MENU_TRAY_FORCEQUIT)
        self.TRAY.setContextMenu(self.MENU_TRAY)
        self.TRAY.show()
        self.reloadTeamup()
        self.config=Config({
            'stopOnDefeated':(self.MENU_SETTINGS_DEFEATED,fgoKernel.schedule.stopOnDefeated),
            'stopOnKizunaReisou':(self.MENU_SETTINGS_KIZUNAREISOU,fgoKernel.schedule.stopOnKizunaReisou),
            'closeToTray':(self.MENU_CONTROL_TRAY,None),
            'stayOnTop':(self.MENU_CONTROL_STAYONTOP,lambda x:self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,x)),
            'notifyEnable':(self.MENU_CONTROL_NOTIFY,None)})
        self.notifier=ServerChann(**self.config['notifyParam'])
        self.worker=Thread()
        self.signalFuncBegin.connect(self.funcBegin)
        self.signalFuncEnd.connect(self.funcEnd)
        self.TRAY.activated.connect(lambda reason:self.show()if reason==QSystemTrayIcon.ActivationReason.Trigger else None)
        self.MENU_TRAY_QUIT.triggered.connect(lambda:QApplication.quit()if self.askQuit()else None)
        self.MENU_TRAY_FORCEQUIT.triggered.connect(QApplication.quit)
        self.getDevice()
    def keyPressEvent(self,key):
        if self.MENU_CONTROL_MAPKEY.isChecked()and not key.modifiers()&~Qt.KeyboardModifier.KeypadModifier:
            try:fgoKernel.device.press(chr(key.nativeVirtualKey()))
            except KeyError:pass
            except Exception as e:logger.critical(e)
    def closeEvent(self,event):
        if self.config['closeToTray']:
            self.hide()
            return event.ignore()
        if self.askQuit():return event.accept()
        event.ignore()
    def askQuit(self):
        if self.worker.is_alive():
            if QMessageBox.warning(self,'FGO-py','战斗正在进行,确认关闭?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes:return False
            fgoKernel.schedule.stop('Quit')
            self.worker.join()
        self.TRAY.hide()
        self.config.save()
        return True
    def isDeviceAvailable(self):
        if not fgoKernel.device.available:
            self.LBL_DEVICE.clear()
            QMessageBox.critical(self,'FGO-py','未连接设备')
            return False
        return True
    def runFunc(self,func,*args,**kwargs):
        if not self.isDeviceAvailable():return
        def f():
            try:
                self.signalFuncBegin.emit()
                self.applyAll()
                fgoKernel.schedule.reset()
                fgoKernel.fuse.reset()
                func(*args,**kwargs)
            except fgoKernel.ScriptStop as e:
                logger.critical(e)
                msg=(str(e),QSystemTrayIcon.MessageIcon.Warning)
            except BaseException as e:
                logger.exception(e)
                msg=(repr(e),QSystemTrayIcon.MessageIcon.Critical)
            else:msg=('Done',QSystemTrayIcon.MessageIcon.Information)
            finally:
                self.signalFuncEnd.emit(msg)
                if self.config['notifyEnable']and not self.notifier(msg[0]):logger.critical('Notify post failed')
        self.worker=Thread(target=f,name=f'{getattr(func,"__qualname__",getattr(type(func),"__qualname__",repr(func)))}({",".join(repr(i)for i in args)}{","if kwargs else""}{",".join("%s=%r"%i for i in kwargs.items())})')
        self.worker.start()
    def funcBegin(self):
        self.BTN_ONEBATTLE.setEnabled(False)
        self.BTN_MAIN.setEnabled(False)
        self.BTN_USER.setEnabled(False)
        self.BTN_PAUSE.setEnabled(True)
        self.BTN_PAUSE.setChecked(False)
        self.BTN_STOP.setEnabled(True)
        self.BTN_STOPLATER.setEnabled(True)
        self.MENU_SCRIPT.setEnabled(False)
        self.TXT_APPLE.setValue(0)
    def funcEnd(self,msg):
        self.BTN_ONEBATTLE.setEnabled(True)
        self.BTN_MAIN.setEnabled(True)
        self.BTN_USER.setEnabled(True)
        self.BTN_PAUSE.setEnabled(False)
        self.BTN_STOP.setEnabled(False)
        self.BTN_STOPLATER.setChecked(False)
        self.BTN_STOPLATER.setEnabled(False)
        self.MENU_SCRIPT.setEnabled(True)
        QApplication.alert(self)
        self.TRAY.showMessage('FGO-py',*msg)
    def loadTeam(self,teamName):
        self.TXT_TEAM.setValue(int(self.teamup[teamName]['teamIndex']))
        (lambda skillInfo:[getattr(self,f'TXT_SKILL_{i}_{j}_{k}').setValue(skillInfo[i][j][k])for i in range(6)for j in range(3)for k in range(4)])(eval(self.teamup[teamName]['skillInfo']))
        (lambda houguInfo:[getattr(self,f'TXT_HOUGU_{i}_{j}').setValue(houguInfo[i][j])for i in range(6)for j in range(2)])(eval(self.teamup[teamName]['houguInfo']))
        (lambda masterSkill:[getattr(self,f'TXT_MASTER_{i}_{j}').setValue(masterSkill[i][j])for i in range(3)for j in range(4+(i==2))])(eval(self.teamup[teamName]['masterSkill']))
    def saveTeam(self):
        if not self.CBX_TEAM.currentText():return
        self.teamup[self.CBX_TEAM.currentText()]={
            'teamIndex':self.TXT_TEAM.value(),
            'skillInfo':str([[[getattr(self,f'TXT_SKILL_{i}_{j}_{k}').value()for k in range(4)]for j in range(3)]for i in range(6)]).replace(' ',''),
            'houguInfo':str([[getattr(self,f'TXT_HOUGU_{i}_{j}').value()for j in range(2)]for i in range(6)]).replace(' ',''),
            'masterSkill':str([[getattr(self,f'TXT_MASTER_{i}_{j}').value()for j in range(4+(i==2))]for i in range(3)]).replace(' ','')}
        with open('fgoTeamup.ini','w')as f:self.teamup.write(f)
    def resetTeam(self):self.loadTeam('DEFAULT')
    def getDevice(self):
        text,ok=QInputDialog.getItem(self,'FGO-py','在下拉列表中选择一个设备',l:=fgoKernel.Device.enumDevices(),l.index(fgoKernel.device.name)if fgoKernel.device.name and fgoKernel.device.name in l else 0,True,Qt.WindowType.WindowStaysOnTopHint)
        if not ok:return
        fgoKernel.device=fgoKernel.Device(text.replace(' ',''))
        self.LBL_DEVICE.setText(fgoKernel.device.name)
        self.MENU_CONTROL_MAPKEY.setChecked(False)
    def runBattle(self):self.runFunc(fgoKernel.Battle())
    def runUserScript(self):self.runFunc(fgoKernel.UserScript())
    def runMain(self):
        text,ok=QInputDialog.getItem(self,'肝哪个','在下拉列表中选择战斗函数',['完成战斗','用户脚本'],0,False)
        if ok and text:self.runFunc(fgoKernel.Main(self.TXT_APPLE.value(),self.CBX_APPLE.currentIndex(),{'完成战斗':fgoKernel.Battle,'用户脚本':fgoKernel.UserScript}[text]))
    def pause(self,x):
        if not x and not self.isDeviceAvailable():return self.BTN_PAUSE.setChecked(True)
        fgoKernel.schedule.pause()
    def stop(self):fgoKernel.schedule.stop('Stop Command Effected')
    def stopLater(self,x):
        if x:
            num,ok=QInputDialog.getInt(self,'输入','剩余的战斗数量',1,1,1919810,1)
            if ok:fgoKernel.schedule.stopLater(num)
            else:self.BTN_STOPLATER.setChecked(False)
        else:fgoKernel.schedule.stopLater()
    def checkScreenshot(self):
        if not self.isDeviceAvailable():return
        try:fgoKernel.Detect(0,blockFuse=True).show()
        except Exception as e:logger.exception(e)
    def applyAll(self):
        fgoKernel.Main.teamIndex=self.TXT_TEAM.value()
        fgoKernel.Turn.skillInfo=[[[getattr(self,f'TXT_SKILL_{i}_{j}_{k}').value()for k in range(4)]for j in range(3)]for i in range(6)]
        fgoKernel.Turn.houguInfo=[[getattr(self,f'TXT_HOUGU_{i}_{j}').value()for j in range(2)]for i in range(6)]
        fgoKernel.Turn.masterSkill=[[getattr(self,f'TXT_MASTER_{i}_{j}').value()for j in range(4+(i==2))]for i in range(3)]
    def explorerHere(self):os.startfile('.')
    def runGacha(self):self.runFunc(fgoKernel.gacha)
    def runLottery(self):self.runFunc(fgoKernel.jackpot)
    def runMail(self):self.runFunc(fgoKernel.mail)
    def runSynthesis(self):self.runFunc(fgoKernel.synthesis)
    def stopOnDefeated(self,x):self.config['stopOnDefeated']=x
    def stopOnKizunaReisou(self,x):self.config['stopOnKizunaReisou']=x
    def stopOnSpecialDrop(self):
        num,ok=QInputDialog.getInt(self,'输入','剩余的特殊掉落数量',1,0,1919810,1)
        if ok:fgoKernel.schedule.stopOnSpecialDrop(num)
    def stayOnTop(self,x):
        self.config['stayOnTop']=x
        self.show()
    def closeToTray(self,x):self.config['closeToTray']=x
    def reloadTeamup(self):
        self.teamup=IniParser('fgoTeamup.ini')
        self.CBX_TEAM.clear()
        self.CBX_TEAM.addItems(self.teamup.sections())
        self.CBX_TEAM.setCurrentIndex(-1)
        self.loadTeam('DEFAULT')
    def mapKey(self,x):self.MENU_CONTROL_MAPKEY.setChecked(x and self.isDeviceAvailable())
    def invoke169(self):
        if not self.isDeviceAvailable():return
        fgoKernel.device.invoke169()
    def revoke169(self):
        if not self.isDeviceAvailable():return
        fgoKernel.device.revoke169()
    def notify(self,x):self.config['notifyEnable']=x
    def bench(self):
        if not self.isDeviceAvailable():return
        QMessageBox.information(self,'FGO-py',(lambda bench:f'{f"点击 {bench[0]:.2f}ms"if bench[0]else""}{", "if all(bench)else""}{f"截图 {bench[1]:.2f}ms"if bench[1]else""}')(fgoKernel.bench()))
    def exec(self):
        s=QApplication.clipboard().text()
        if QMessageBox.information(self,'FGO-py',s,QMessageBox.StandardButton.Ok|QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Ok:return
        try:exec(s)
        except BaseException as e:logger.exception(e)
    def about(self):QMessageBox.about(self,'FGO-py - About',f'''
<h2>FGO-py</h2>
FGO全自动脚本
<table border="0">
  <tr><td>当前版本</td><td>{fgoKernel.__version__}</td></tr>
  <tr><td>作者</td><td>hgjazhgj</td></tr>
  <tr><td>项目地址</td><td><a href="https://github.com/hgjazhgj/FGO-py">https://github.com/hgjazhgj/FGO-py</a></td></tr>
  <tr><td>电子邮箱</td><td><a href="mailto:huguangjing0411@geektip.cc">huguangjing0411@geektip.cc</a></td></tr>
  <tr><td>QQ群</td><td>932481680</td></tr>
</table>
<!-- 都看到这里了真的不考虑资瓷一下吗... -->
这是我的<font color="#00A0E8">支付宝</font>/<font color="#22AB38">微信</font>收款码和Monero地址<br/>请给我打钱<br/>
<img height="116" width="116" src="data:image/bmp;base64,Qk2yAAAAAAAAAD4AAAAoAAAAHQAAAB0AAAABAAEAAAAAAHQAAAB0EgAAdBIAAAAAAAAAAAAA6KAAAP///wABYWKofU/CKEV/ZtBFXEMwRbiQUH2a5yABj+Uo/zf3AKDtsBjeNa7YcUYb2MrQ04jEa/Ioh7TO6BR150Djjo3ATKgPmGLjdfDleznImz0gcA19mxD/rx/4AVVUAH2zpfBFCgUQRSgtEEVjdRB9/R3wATtkAA=="/>
<img height="116" width="116" src="data:image/bmp;base64,Qk2yAAAAAAAAAD4AAAAoAAAAHQAAAB0AAAABAAEAAAAAAHQAAAB0EgAAdBIAAAAAAAAAAAAAOKsiAP///wABNLhYfVLBqEUYG0hFcn7gRS8QAH2Pd2ABQiVY/x1nMFWzcFhidNUwaXr3GEp1khDJzDfAuqx06ChC9hhPvmIQMJX3SCZ13ehlXB9IVtJQUAQreqj/jv/4AVVUAH0iFfBFuxUQRRAlEEX2fRB9Wl3wAdBsAA=="/>
<table border="0"><tr>
  <td><img height="148" width="148" src="data:image/bmp;base64,Qk1mAQAAAAAAAD4AAAAoAAAAJQAAACUAAAABAAEAAAAAACgBAAB0EgAAdBIAAAAAAAAAAAAAAAAAAP///wABNpugAAAAAH0Q2oL4AAAARb1nmkAAAABFZnR3IAAAAEXpv9AwAAAAfZSA10AAAAABXdMVYAAAAP8qTsdQAAAAMd998EgAAACighiQeAAAAFCt3LiwAAAAo3aTXIAAAACAQzl8SAAAAEehYzFgAAAAcZ0FlEAAAACmEjZXoAAAAD2l77w4AAAAvy27zoAAAAD4P5FWQAAAAEYVS3VwAAAAyXKhYYAAAACvQwA4OAAAALyhfNNwAAAAhuODSLAAAABIC/+BMAAAABpa6jMwAAAA6TltfQAAAAATihl8wAAAACzQ8IxIAAAA/zQAZ/gAAAABVVVUAAAAAH0qre3wAAAARXxupRAAAABFiJ3tEAAAAEUGtG0QAAAAfWa6DfAAAAABsL3cAAAAAA=="/></td>
  <td><font face="Courier New">42Cnr V9Tuz E1jiS<br/>2ucGw tzN8g F6o4y<br/>9SkHs X1eZE vtiDf<br/>4QcL1 NXvfZ PhDu7<br/>LYStW rbsQM 9UUGW<br/>nqXgh ManMB dqjEW<br/>5oaDY</font></td>
</tr></table>
''')
    def license(self):os.system(f'start notepad {"LICENSE"if os.path.isfile("LICENSE")else"../LICENSE"}')

def main(args):
    app=QApplication(sys.argv)
    myWin=MyMainWindow()
    myWin.show()
    sys.exit(app.exec())
