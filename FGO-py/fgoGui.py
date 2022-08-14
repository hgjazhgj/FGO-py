import json,os,sys,time,platform
from threading import Thread
from PyQt6.QtCore import Qt,pyqtSignal
from PyQt6.QtGui import QAction,QIcon
from PyQt6.QtWidgets import QApplication,QInputDialog,QMainWindow,QMenu,QMessageBox,QSystemTrayIcon
import fgoDevice
import fgoKernel
from fgoMainWindow import Ui_fgoMainWindow
from fgoServerChann import ServerChann
logger=fgoKernel.getLogger('Gui')

class Config:
    def __init__(self,link=None):
        with open('fgoConfig.json')as f:self.config=json.load(f)
        self.link=link if isinstance(link,dict)else{}
        for configName,(uiObject,scheduleFunc)in self.link.items():
            value=self.config[configName]
            getattr(uiObject,{bool:'setChecked',int:'setValue',str:'setText'}[type(value)])(value)
            if callable(scheduleFunc):scheduleFunc(value)
            getattr(uiObject,{bool:'triggered',int:'valueChanged',str:'textChanged'}[type(value)])[type(value)].connect(lambda x,configName=configName:self.__setitem__(configName,x))
    def __getitem__(self,key):return self.config[key]
    def __setitem__(self,key,value):
        self.config[key]=value
        if key in self.link:
            # getattr(self.link[key][0],{bool:'setChecked',int:'setValue',str:'setText'}[type(value)])(value)
            if callable(self.link[key][1]):self.link[key][1](value)
    def save(self):
        with open('fgoConfig.json','w')as f:json.dump(self.config,f,indent=4)

class MyMainWindow(QMainWindow,Ui_fgoMainWindow):
    signalFuncBegin=pyqtSignal()
    signalFuncEnd=pyqtSignal(object)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        if platform.system()=='Darwin':fgoMainWindow.setStyleSheet("QWidget{font-family:\"PingFang SC\";font-size:15px}")
        self.setWindowIcon(QIcon('fgoIcon.ico'))
        self.TRAY=QSystemTrayIcon(self)
        self.TRAY.setIcon(QIcon('fgoIcon.ico'))
        self.TRAY.setToolTip('FGO-py')
        self.MENU_TRAY=QMenu(self)
        self.MENU_TRAY_QUIT=QAction('退出',self.MENU_TRAY)
        self.MENU_TRAY.addAction(self.MENU_TRAY_QUIT)
        self.MENU_TRAY_FORCEQUIT=QAction('强制退出',self.MENU_TRAY)
        self.MENU_TRAY.addAction(self.MENU_TRAY_FORCEQUIT)
        self.TRAY.setContextMenu(self.MENU_TRAY)
        self.TRAY.show()
        self.TRAY.activated.connect(lambda reason:self.show()if reason==QSystemTrayIcon.ActivationReason.Trigger else None)
        self.MENU_TRAY_QUIT.triggered.connect(lambda:QApplication.quit()if self.askQuit()else None)
        self.MENU_TRAY_FORCEQUIT.triggered.connect(QApplication.quit)
        self.signalFuncBegin.connect(self.funcBegin)
        self.signalFuncEnd.connect(self.funcEnd)
        self.worker=Thread()
        self.config=Config({
            'teamIndex':(self.TXT_TEAM,lambda x:setattr(fgoKernel.Main,'teamIndex',x)),
            'stopOnDefeated':(self.MENU_SETTINGS_DEFEATED,fgoKernel.schedule.stopOnDefeated),
            'stopOnKizunaReisou':(self.MENU_SETTINGS_KIZUNAREISOU,fgoKernel.schedule.stopOnKizunaReisou),
            'closeToTray':(self.MENU_CONTROL_TRAY,None),
            'stayOnTop':(self.MENU_CONTROL_STAYONTOP,lambda x:(self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,x),self.show())),
            'notifyEnable':(self.MENU_CONTROL_NOTIFY,None)})
        self.notifier=ServerChann(**self.config['notifyParam'])
        self.connect()
    def keyPressEvent(self,key):
        if self.MENU_CONTROL_MAPKEY.isChecked()and not key.modifiers()&~Qt.KeyboardModifier.KeypadModifier:
            try:fgoDevice.device.press(chr(key.nativeVirtualKey()))
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
        if not fgoDevice.device.available:
            self.LBL_DEVICE.clear()
            QMessageBox.critical(self,'FGO-py','未连接设备')
            return False
        return True
    def runFunc(self,func,*args,**kwargs):
        if not self.isDeviceAvailable():return
        def f():
            try:
                self.signalFuncBegin.emit()
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
                fgoKernel.fuse.reset()
                fgoKernel.schedule.reset()
                if self.config['notifyEnable']and not self.notifier(msg[0]):logger.critical('Notify post failed')
        self.worker=Thread(target=f,name=f'{getattr(func,"__qualname__",getattr(type(func),"__qualname__",repr(func)))}({",".join(repr(i)for i in args)}{","if kwargs else""}{",".join("%s=%r"%i for i in kwargs.items())})')
        self.worker.start()
    def funcBegin(self):
        self.BTN_ONEBATTLE.setEnabled(False)
        self.BTN_MAIN.setEnabled(False)
        self.BTN_PAUSE.setEnabled(True)
        self.BTN_PAUSE.setChecked(False)
        self.BTN_STOP.setEnabled(True)
        self.BTN_STOPLATER.setEnabled(True)
        self.MENU_SCRIPT.setEnabled(False)
        self.TXT_APPLE.setValue(0)
    def funcEnd(self,msg):
        self.BTN_ONEBATTLE.setEnabled(True)
        self.BTN_MAIN.setEnabled(True)
        self.BTN_PAUSE.setEnabled(False)
        self.BTN_STOP.setEnabled(False)
        self.BTN_STOPLATER.setChecked(False)
        self.BTN_STOPLATER.setEnabled(False)
        self.MENU_SCRIPT.setEnabled(True)
        QApplication.alert(self)
        self.TRAY.showMessage('FGO-py',*msg)
    def connect(self):
        dialog=QInputDialog(self,Qt.WindowType.WindowStaysOnTopHint)
        dialog.setWindowTitle('FGO-py')
        dialog.setLabelText('在下拉列表中选择一个设备')
        dialog.setComboBoxItems(fgoDevice.Device.enumDevices())
        dialog.setComboBoxEditable(True)
        dialog.setTextValue(self.config['device'])
        if not dialog.exec():return
        text=dialog.textValue().replace(' ','')
        self.config['device']=text
        fgoDevice.device=fgoDevice.Device(text,self.config['package'])
        self.LBL_DEVICE.setText(fgoDevice.device.name)
        self.MENU_CONTROL_MAPKEY.setChecked(False)
    def runBattle(self):self.runFunc(fgoKernel.Battle())
    def runMain(self):self.runFunc(fgoKernel.Main(self.TXT_APPLE.value(),self.CBX_APPLE.currentIndex(),fgoKernel.Battle))
    def pause(self,x):
        if not x and not self.isDeviceAvailable():return self.BTN_PAUSE.setChecked(True)
        fgoKernel.schedule.pause()
    def stop(self):fgoKernel.schedule.stop('Stop Command Effected')
    def stopLater(self,x):
        if x:
            num,ok=QInputDialog.getInt(self,'FGO-py','剩余的战斗数量',1,1,1919810,1)
            if ok:fgoKernel.schedule.stopLater(num)
            else:self.BTN_STOPLATER.setChecked(False)
        else:fgoKernel.schedule.stopLater()
    def screenshot(self):
        if not self.isDeviceAvailable():return
        try:fgoKernel.Detect(0).show()
        except Exception as e:logger.exception(e)
    def explorerHere(self):os.startfile('.')
    def runGacha(self):self.runFunc(fgoKernel.gacha)
    def runLottery(self):self.runFunc(fgoKernel.lottery)
    def runMail(self):self.runFunc(fgoKernel.mail)
    def runSynthesis(self):self.runFunc(fgoKernel.synthesis)
    def expBall(self):
        QMessageBox.information(self,'FGO-py','''
搓丸子是一个基于FGO-py的独立项目<br/>
<a href="https://github.com/hgjazhgj/FGO-ExpBall">FGO-ExpBall</a><br/>
你看见了这个弹窗,说明你已经能够运行FGO-py了<br/>
那么,无需任何其他配置,你可以直接运行FGO-ExpBall''')
    def stopOnSpecialDrop(self):
        num,ok=QInputDialog.getInt(self,'FGO-py','剩余的特殊掉落数量',1,0,1919810,1)
        if ok:fgoKernel.schedule.stopOnSpecialDrop(num)
    def mapKey(self,x):self.MENU_CONTROL_MAPKEY.setChecked(x and self.isDeviceAvailable())
    def invoke169(self):
        if not self.isDeviceAvailable():return
        fgoDevice.device.invoke169()
    def revoke169(self):
        if not self.isDeviceAvailable():return
        fgoDevice.device.revoke169()
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
全自动免配置跨平台开箱即用的FGO助手
<table border="0">
  <tr><td>当前版本</td><td>{fgoKernel.__version__}</td></tr>
  <tr><td>作者</td><td><a href="https://github.com/hgjazhgj">hgjazhgj</a></td></tr>
  <tr><td>项目主页</td><td><a href="https://fgo-py.hgjazhgj.top/">https://fgo-py.hgjazhgj.top/</a></td></tr>
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
B站大会员每月<a href="https://account.bilibili.com/account/big/myPackage">领</a>5B币券<a href="https://space.bilibili.com/2632341">充电</a>
''')
    def license(self):os.system(f'start notepad {"LICENSE"if os.path.isfile("LICENSE")else"../LICENSE"}')

def main(args):
    app=QApplication(sys.argv)
    myWin=MyMainWindow()
    myWin.show()
    sys.exit(app.exec())
