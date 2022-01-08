import json,os,sys
from configparser import ConfigParser
from threading import Thread
from PyQt6.QtCore import Qt,pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication,QInputDialog,QMainWindow,QMessageBox,QStyle,QSystemTrayIcon,QMenu

import fgoFunc
from fgoConst import version
from fgoServerChann import ServerChann
from fgoMainWindow import Ui_fgoMainWindow

logger=fgoFunc.getLogger('Gui')

NewConfigParser=type('NewConfigParser',(ConfigParser,),{'__init__':lambda self,file:(ConfigParser.__init__(self),self.read(file))[0],'optionxform':lambda self,optionstr:optionstr})

class Config:
    def __init__(self,link=None):
        with open('fgoConfig.json','r')as f:self.config=json.load(f)
        self.link=link if isinstance(link,dict)else{}
        for configName,(menuItem,controlFunc)in self.link.items():
            menuItem.setChecked(bool(self.config[configName]))
            if callable(controlFunc):controlFunc(self.config[configName])
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
            'stopOnDefeated':(self.MENU_SETTINGS_DEFEATED,fgoFunc.control.stopOnDefeated),
            'stopOnKizunaReisou':(self.MENU_SETTINGS_KIZUNAREISOU,fgoFunc.control.stopOnKizunaReisou),
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
            try:fgoFunc.device.press(chr(key.nativeVirtualKey()))
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
            fgoFunc.control.terminate('Quit')
            self.worker.join()
        self.TRAY.hide()
        self.config.save()
        return True
    def isDeviceAvaliable(self):
        if not fgoFunc.device.avaliable:
            self.LBL_DEVICE.clear()
            QMessageBox.critical(self,'FGO-py','未连接设备')
            return False
        return True
    def runFunc(self,func,*args,**kwargs):
        if not self.isDeviceAvaliable():return
        def f():
            try:
                self.signalFuncBegin.emit()
                self.applyAll()
                fgoFunc.control.reset()
                fgoFunc.fuse.reset()
                func(*args,**kwargs)
            except fgoFunc.ScriptTerminate as e:
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
        text,ok=QInputDialog.getItem(self,'FGO-py','在下拉列表中选择一个设备',l:=fgoFunc.Device.enumDevices(),l.index(fgoFunc.device.name)if fgoFunc.device.name and fgoFunc.device.name in l else 0,True,Qt.WindowType.WindowStaysOnTopHint)
        if not ok:return
        if text.startswith('/'):
            try:
                if text=='/gw':
                    import netifaces
                    text=f'{netifaces.gateways()["default"][netifaces.AF_INET][0]}:5555'
                elif text=='/bs4':
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\BlueStacks_bgp64_hyperv\Guests\Android\Config')as key:text='127.0.0.1:'+winreg.QueryValueEx(key,"BstAdbPort")[0]
                elif text=='/bs5':
                    import re,winreg
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\BlueStacks_nxt')as key:text=winreg.QueryValueEx(key,'UserDefinedDir')[0]
                    with open(os.path.join(text,'bluestacks.conf'))as f:text='127.0.0.1:'+re.search(r'bst\.instance\.Nougat64\.status\.adb_port="(\d*)"',f.read()).group(1)
            except Exception as e:return logger.exception(e)
        fgoFunc.device=fgoFunc.Device(text.replace(' ',''))
        self.LBL_DEVICE.setText(fgoFunc.device.name)
        self.MENU_CONTROL_MAPKEY.setChecked(False)
    def runBattle(self):self.runFunc(fgoFunc.Battle())
    def runUserScript(self):self.runFunc(fgoFunc.UserScript())
    def runMain(self):
        text,ok=QInputDialog.getItem(self,'肝哪个','在下拉列表中选择战斗函数',['完成战斗','用户脚本'],0,False)
        if ok and text:self.runFunc(fgoFunc.Main(self.TXT_APPLE.value(),self.CBX_APPLE.currentIndex(),{'完成战斗':fgoFunc.Battle,'用户脚本':fgoFunc.UserScript}[text]))
    def pause(self,x):
        if not x and not self.isDeviceAvaliable():return self.BTN_PAUSE.setChecked(True)
        fgoFunc.control.suspend()
    def stop(self):fgoFunc.control.terminate('Terminate Command Effected')
    def stopLater(self,x):
        if x:
            num,ok=QInputDialog.getInt(self,'输入','剩余的战斗数量',1,1,1919810,1)
            if ok:fgoFunc.control.terminateLater(num)
            else:self.BTN_STOPLATER.setChecked(False)
        else:fgoFunc.control.terminateLater()
    def checkScreenshot(self):
        if not self.isDeviceAvaliable():return
        try:fgoFunc.Check(0,blockFuse=True).show()
        except Exception as e:logger.exception(e)
    def applyAll(self):
        fgoFunc.Main.teamIndex=self.TXT_TEAM.value()
        fgoFunc.Battle.skillInfo=[[[getattr(self,f'TXT_SKILL_{i}_{j}_{k}').value()for k in range(4)]for j in range(3)]for i in range(6)]
        fgoFunc.Battle.houguInfo=[[getattr(self,f'TXT_HOUGU_{i}_{j}').value()for j in range(2)]for i in range(6)]
        fgoFunc.Battle.masterSkill=[[getattr(self,f'TXT_MASTER_{i}_{j}').value()for j in range(4+(i==2))]for i in range(3)]
    def explorerHere(self):os.startfile('.')
    def runGacha(self):self.runFunc(fgoFunc.gacha)
    def runJackpot(self):self.runFunc(fgoFunc.jackpot)
    def runMailFiltering(self):self.runFunc(fgoFunc.mailFiltering)
    def stopOnDefeated(self,x):self.config['stopOnDefeated']=x
    def stopOnKizunaReisou(self,x):self.config['stopOnKizunaReisou']=x
    def stopOnSpecialDrop(self):
        num,ok=QInputDialog.getInt(self,'输入','剩余的特殊掉落数量',1,0,1919810,1)
        if ok:fgoFunc.control.stopOnSpecialDrop(num)
    def stayOnTop(self,x):
        self.config['stayOnTop']=x
        self.show()
    def closeToTray(self,x):self.config['closeToTray']=x
    def reloadTeamup(self):
        self.teamup=NewConfigParser('fgoTeamup.ini')
        self.CBX_TEAM.clear()
        self.CBX_TEAM.addItems(self.teamup.sections())
        self.CBX_TEAM.setCurrentIndex(-1)
        self.loadTeam('DEFAULT')
    def mapKey(self,x):self.MENU_CONTROL_MAPKEY.setChecked(x and self.isDeviceAvaliable())
    def invoke169(self):
        if not self.isDeviceAvaliable():return
        fgoFunc.device.invoke169()
    def revoke169(self):
        if not self.isDeviceAvaliable():return
        fgoFunc.device.revoke169()
    def notify(self,x):self.config['notifyEnable']=x
    def exec(self):
        s=QApplication.clipboard().text()
        if QMessageBox.information(self,'FGO-py',s,QMessageBox.StandardButton.Ok|QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Ok:return
        try:exec(s)
        except BaseException as e:logger.exception(e)
    def about(self):QMessageBox.about(self,'FGO-py - About',f'''
<h2>FGO-py</h2>
FGO全自动脚本
<table border="0">
  <tr><td>当前版本</td><td>{version}</td></tr>
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

def main():
    app=QApplication(sys.argv)
    myWin=MyMainWindow()
    myWin.show()
    sys.exit(app.exec())
