import json,os,sys,time,platform
from threading import Thread
from PySide6.QtCore import Qt,QCoreApplication,QLocale,QTranslator,Signal,Slot
from PySide6.QtGui import QAction,QIcon
from PySide6.QtWidgets import QApplication,QInputDialog,QMainWindow,QMenu,QMessageBox,QSystemTrayIcon
import fgoDevice
import fgoKernel
from fgoMainWindow import Ui_fgoMainWindow
from fgoGuiTeamup import Teamup
from fgoServerChann import ServerChann
logger=fgoKernel.getLogger('Gui')

class MainWindow(QMainWindow,Ui_fgoMainWindow):
    signalFuncBegin=Signal()
    signalFuncEnd=Signal(object)
    def __init__(self,config,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        if platform.system()=='Darwin':self.setStyleSheet("QWidget{font-family:\"PingFang SC\";font-size:15px}")
        self.setWindowIcon(QIcon('fgoIcon.ico'))
        self.TRAY=QSystemTrayIcon(self)
        self.TRAY.setIcon(QIcon('fgoIcon.ico'))
        self.TRAY.setToolTip('FGO-py')
        self.MENU_TRAY=QMenu(self)
        self.MENU_TRAY_QUIT=QAction(self.tr('退出'),self.MENU_TRAY)
        self.MENU_TRAY.addAction(self.MENU_TRAY_QUIT)
        self.MENU_TRAY_FORCEQUIT=QAction(self.tr('强制退出'),self.MENU_TRAY)
        self.MENU_TRAY.addAction(self.MENU_TRAY_FORCEQUIT)
        self.TRAY.setContextMenu(self.MENU_TRAY)
        self.TRAY.show()
        self.TRAY.activated.connect(lambda reason:self.show()if reason==QSystemTrayIcon.ActivationReason.Trigger else None)
        self.MENU_TRAY_QUIT.triggered.connect(lambda:QApplication.quit()if self.askQuit()else None)
        self.MENU_TRAY_FORCEQUIT.triggered.connect(QApplication.quit)
        self.signalFuncBegin.connect(self.funcBegin)
        self.signalFuncEnd.connect(self.funcEnd)
        self.worker=Thread()
        self.config=config
        for key,ui,callback in[
            ('teamIndex',self.TXT_TEAM,lambda x:setattr(fgoKernel.Main,'teamIndex',x)),
            ('stopOnDefeated',self.MENU_SETTINGS_DEFEATED,fgoKernel.schedule.stopOnDefeated),
            ('stopOnKizunaReisou',self.MENU_SETTINGS_KIZUNAREISOU,fgoKernel.schedule.stopOnKizunaReisou),
            ('closeToTray',self.MENU_CONTROL_TRAY,None),
            ('stayOnTop',self.MENU_CONTROL_STAYONTOP,lambda x:(self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,x),self.show())),
            ('notifyEnable',self.MENU_CONTROL_NOTIFY,None),
        ]:
            value=self.config[key]
            getattr(ui,{bool:'toggled',int:'valueChanged',str:'textChanged'}[type(value)])[type(value)].connect((lambda x,key=key,callback=callback:(self.config.__setitem__(key,x),callback(x)))if callback else(lambda x,key=key:self.config.__setitem__(key,x)))
            getattr(ui,{bool:'setChecked',int:'setValue',str:'setText'}[type(value)])(value)
        self.notifier=[ServerChann(**i)for i in self.config.notifyParam]
        self.connectDevice()
    def keyPressEvent(self,key):
        if self.MENU_CONTROL_MAPKEY.isChecked()and not key.modifiers()&~Qt.KeyboardModifier.KeypadModifier:
            try:fgoDevice.device.press(chr(key.nativeVirtualKey()))
            except KeyError:pass
            except Exception as e:logger.critical(e)
    def closeEvent(self,event):
        if self.config.closeToTray:
            self.hide()
            return event.ignore()
        if self.askQuit():return event.accept()
        event.ignore()
    def askQuit(self):
        if self.worker.is_alive():
            if QMessageBox.warning(self,'FGO-py',self.tr('战斗正在进行,确认关闭?'),QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes:return False
            fgoKernel.schedule.stop('Quit')
            self.worker.join()
        self.TRAY.hide()
        return True
    def isDeviceAvailable(self):
        if not fgoDevice.device.available:
            self.LBL_DEVICE.clear()
            QMessageBox.critical(self,'FGO-py',self.tr('未连接设备'))
            return False
        return True
    def runFunc(self,func):
        if not self.isDeviceAvailable():return
        def f():
            try:
                self.signalFuncBegin.emit()
                func()
            except fgoKernel.ScriptStop as e:
                logger.critical(e)
                msg=(str(e),QSystemTrayIcon.MessageIcon.Warning)
            except BaseException as e:
                logger.exception(e)
                msg=(repr(e),QSystemTrayIcon.MessageIcon.Critical)
            else:msg=('Done',QSystemTrayIcon.MessageIcon.Information)
            finally:
                self.result=getattr(func,'result',None)
                self.signalFuncEnd.emit(msg)
                fgoKernel.fuse.reset()
                fgoKernel.schedule.reset()
                if self.config.notifyEnable and not all(success:=[i(msg[0])for i in self.notifier]):logger.critical(f'Notify post failed {success.count(False)} of {len(success)}')
        self.worker=Thread(target=f,name=f'{getattr(func,"__qualname__",repr(func))}')
        self.worker.start()
    @Slot()
    def funcBegin(self):
        self.BTN_MAIN.setEnabled(False)
        self.BTN_BATTLE.setEnabled(False)
        self.BTN_CLASSIC.setEnabled(False)
        self.BTN_STORY.setEnabled(False)
        self.BTN_PAUSE.setEnabled(True)
        self.BTN_PAUSE.setChecked(False)
        self.BTN_STOP.setEnabled(True)
        self.BTN_STOPLATER.setEnabled(True)
        self.MENU_SCRIPT.setEnabled(False)
        self.TXT_APPLE.setValue(0)
        self.result=None
    @Slot(object)
    def funcEnd(self,msg):
        self.BTN_MAIN.setEnabled(True)
        self.BTN_BATTLE.setEnabled(True)
        self.BTN_CLASSIC.setEnabled(True)
        self.BTN_STORY.setEnabled(True)
        self.BTN_PAUSE.setEnabled(False)
        self.BTN_STOP.setEnabled(False)
        self.BTN_STOPLATER.setChecked(False)
        self.BTN_STOPLATER.setEnabled(False)
        self.MENU_SCRIPT.setEnabled(True)
        QApplication.alert(self)
        self.TRAY.showMessage('FGO-py',*msg)
        if isinstance(self.result,dict)and(t:=self.result.get('type',None)):
            if t=='Battle':QMessageBox.information(self,'FGO-py',f'''
<h2>{msg[0].split(':',1)[0]}</h2>
<font color="#006400">{self.result['turn']:.1f}</font>{self.tr('回合完成战斗')},{self.tr('用时')}<font color="#006400">{self.result['time']//3600:.0f}:{self.result['time']//60%60:02.0f}:{self.result['time']%60:02.0f}</font><br/>
{self.tr('获得了以下素材')}:<br/>
{'<br/>'.join(f'<img src="fgoImage/material/{i}.png" height="18" width="18">{QCoreApplication.translate("material",i)}<font color="#7030A0">x{j}</font>'for i,j in self.result['material'].items())if self.result['material']else self.tr('无')}
''')
            elif t=='Main':
                QMessageBox.information(self,'FGO-py',f'''
<h2>{msg[0].split(':',1)[0]}</h2>
{self.tr('在过去的')}<font color="#006400">{self.result['time']//3600:.0f}:{self.result['time']//60%60:02.0f}:{self.result['time']%60:02.0f}</font>{self.tr('中完成了')}<font color="#006400">{self.result['battle']}</font>{self.tr('场战斗')}<br/>
{self.tr('平均每场战斗')}<font color="#006400">{self.result['turnPerBattle']:.1f}</font>{self.tr('回合')},{self.tr('用时')}<font color="#006400">{self.result['timePerBattle']//60:.0f}:{self.result['timePerBattle']%60:04.1f}</font><br/>
{self.tr('获得了以下素材')}:<br/>
{'<br/>'.join(f'<img src="fgoImage/material/{i}.png" height="18" width="18">{QCoreApplication.translate("material",i)}<font color="#7030A0">x{j}</font>'for i,j in self.result['material'].items())if self.result['material']else self.tr('无')}
''')
            elif t=='SummonHistory':
                QMessageBox.information(self,'FGO-py',f'''
<h2>{msg[0].split(':',1)[0]}</h2>
{self.tr('获取到')}<font color="#006400">{self.result['value']}</font>{self.tr('条抽卡记录')},{self.tr('图片保存至')}</br>
<font color="#7030A0">{self.result['file']}</font>
''')
        self.result=None
    def connectDevice(self):
        dialog=QInputDialog(self,Qt.WindowType.WindowStaysOnTopHint)
        dialog.setWindowTitle('FGO-py')
        dialog.setLabelText(self.tr('选择或填写一个设备'))
        dialog.setComboBoxItems(fgoDevice.Device.enumDevices())
        dialog.setComboBoxEditable(True)
        dialog.setTextValue(self.config.device)
        if not dialog.exec():return
        text=dialog.textValue().replace(' ','')
        self.config.device=text
        fgoDevice.device=fgoDevice.Device(text)
        self.LBL_DEVICE.setText(fgoDevice.device.name)
        self.MENU_CONTROL_MAPKEY.setChecked(False)
    def runMain(self):self.runFunc(fgoKernel.Main(self.TXT_APPLE.value(),self.CBX_APPLE.currentIndex()))
    def runBattle(self):self.runFunc(fgoKernel.Battle())
    def runClassic(self):
        if not Teamup(self).exec():return
        self.runFunc(fgoKernel.Main(self.TXT_APPLE.value(),self.CBX_APPLE.currentIndex(),lambda:fgoKernel.Battle(fgoKernel.ClassicTurn)))
    def runStory(self):self.runFunc(fgoKernel.MainStory(self.TXT_APPLE.value(),self.CBX_APPLE.currentIndex(),lambda:fgoKernel.BattleStory(fgoKernel.Turn)))

    def pause(self,x):
        if not x and not self.isDeviceAvailable():return self.BTN_PAUSE.setChecked(True)
        fgoKernel.schedule.pause()
    def stop(self):fgoKernel.schedule.stop('Stop Command Effected')
    def stopLater(self,x):
        if x:
            num,ok=QInputDialog.getInt(self,'FGO-py',self.tr('剩余的战斗数量'),1,1,1919810,1)
            if ok:fgoKernel.schedule.stopLater(num)
            else:self.BTN_STOPLATER.setChecked(False)
        else:fgoKernel.schedule.stopLater()
    def screenshot(self):
        if not self.isDeviceAvailable():return
        try:fgoKernel.Detect(0).show()
        except Exception as e:logger.exception(e)
    def explorerHere(self):os.startfile('.') if platform.system()=="Windows" else os.system("xdg-open .") if platform.system() == "Linux" else os.system("open .")
    def runFpSummon(self):self.runFunc(fgoKernel.fpSummon)
    def runLottery(self):self.runFunc(fgoKernel.lottery)
    def runMail(self):self.runFunc(fgoKernel.mail)
    def runSynthesis(self):self.runFunc(fgoKernel.synthesis)
    def runSummonHistory(self):self.runFunc(fgoKernel.summonHistory)
    def expBall(self):
        QMessageBox.information(self,'FGO-py',f'''
{self.tr('搓丸子是一个基于FGO-py的独立项目')}<br/>
<a href="https://github.com/hgjazhgj/FGO-ExpBall">FGO-ExpBall</a><br/>
{self.tr('你看见了这个弹窗,说明你已经能够运行FGO-py了')}<br/>
{self.tr('那么,无需任何其他配置,你可以直接运行FGO-ExpBall')}''')
    def stopOnSpecialDrop(self):
        num,ok=QInputDialog.getInt(self,'FGO-py',self.tr('剩余的特殊掉落数量'),1,0,1919810,1)
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
        QMessageBox.information(self,'FGO-py',(lambda bench:f'''{f"{self.tr('点击')} {bench[0]:.2f}ms"if bench[0]else""}{", "if all(bench)else""}{f"{self.tr('截图')} {bench[1]:.2f}ms"if bench[1]else""}''')(fgoKernel.bench()))
    def exec(self):
        s=QApplication.clipboard().text()
        if QMessageBox.information(self,'FGO-py',s,QMessageBox.StandardButton.Ok|QMessageBox.StandardButton.Cancel)!=QMessageBox.StandardButton.Ok:return
        try:exec(s)
        except BaseException as e:logger.exception(e)
    def about(self):QMessageBox.about(self,'FGO-py - About',f'''
<h2>FGO-py</h2>
{self.tr('全自动免配置跨平台开箱即用的FGO助手')}
<table border="0">
  <tr><td>{self.tr('当前版本')}</td><td>{fgoKernel.__version__}</td></tr>
  <tr><td>{self.tr('作者')}</td><td><a href="https://github.com/hgjazhgj">hgjazhgj</a></td></tr>
  <tr><td>{self.tr('项目主页')}</td><td><a href="https://fgo-py.hgjazhgj.top/">https://fgo-py.hgjazhgj.top/</a></td></tr>
  <tr><td>{self.tr('QQ群')}</td><td>932481680({self.tr('请按readme指引操作')})</td></tr>
</table>
<!-- 都看到这里了真的不考虑资瓷一下吗... -->
{self.tr('这是我的')}<font color="#00A0E8">{self.tr('支付宝')}</font>/<font color="#22AB38">{self.tr('微信')}</font>{self.tr('收款码和Monero地址')}<br/>{self.tr('请给我打钱')}<br/>
<img height="116" width="116" src="data:image/bmp;base64,Qk2yAAAAAAAAAD4AAAAoAAAAHQAAAB0AAAABAAEAAAAAAHQAAAB0EgAAdBIAAAAAAAAAAAAA6KAAAP///wABYWKofU/CKEV/ZtBFXEMwRbiQUH2a5yABj+Uo/zf3AKDtsBjeNa7YcUYb2MrQ04jEa/Ioh7TO6BR150Djjo3ATKgPmGLjdfDleznImz0gcA19mxD/rx/4AVVUAH2zpfBFCgUQRSgtEEVjdRB9/R3wATtkAA=="/>
<img height="116" width="116" src="data:image/bmp;base64,Qk2yAAAAAAAAAD4AAAAoAAAAHQAAAB0AAAABAAEAAAAAAHQAAAB0EgAAdBIAAAAAAAAAAAAAOKsiAP///wABNLhYfVLBqEUYG0hFcn7gRS8QAH2Pd2ABQiVY/x1nMFWzcFhidNUwaXr3GEp1khDJzDfAuqx06ChC9hhPvmIQMJX3SCZ13ehlXB9IVtJQUAQreqj/jv/4AVVUAH0iFfBFuxUQRRAlEEX2fRB9Wl3wAdBsAA=="/>
<table border="0"><tr>
  <td><img height="148" width="148" src="data:image/bmp;base64,Qk1mAQAAAAAAAD4AAAAoAAAAJQAAACUAAAABAAEAAAAAACgBAAB0EgAAdBIAAAAAAAAAAAAAAAAAAP///wABNpugAAAAAH0Q2oL4AAAARb1nmkAAAABFZnR3IAAAAEXpv9AwAAAAfZSA10AAAAABXdMVYAAAAP8qTsdQAAAAMd998EgAAACighiQeAAAAFCt3LiwAAAAo3aTXIAAAACAQzl8SAAAAEehYzFgAAAAcZ0FlEAAAACmEjZXoAAAAD2l77w4AAAAvy27zoAAAAD4P5FWQAAAAEYVS3VwAAAAyXKhYYAAAACvQwA4OAAAALyhfNNwAAAAhuODSLAAAABIC/+BMAAAABpa6jMwAAAA6TltfQAAAAATihl8wAAAACzQ8IxIAAAA/zQAZ/gAAAABVVVUAAAAAH0qre3wAAAARXxupRAAAABFiJ3tEAAAAEUGtG0QAAAAfWa6DfAAAAABsL3cAAAAAA=="/></td>
  <td><font face="Courier New">42Cnr V9Tuz E1jiS<br/>2ucGw tzN8g F6o4y<br/>9SkHs X1eZE vtiDf<br/>4QcL1 NXvfZ PhDu7<br/>LYStW rbsQM 9UUGW<br/>nqXgh ManMB dqjEW<br/>5oaDY</font></td>
</tr></table>
<a href="https://github.com/sponsors/hgjazhgj/">GitHub Sponsor</a><br/>
<a href="https://patreon.com/hgjazhgj">Patreon</a><br/>
<a href="https://paypal.me/hgjazhgjpp">Paypal</a><br/>
{self.tr('B站大会员每月')}<a href="https://account.bilibili.com/account/big/myPackage">{self.tr('领')}</a>{self.tr('5B币券')}<a href="https://space.bilibili.com/2632341">{self.tr('充电')}</a>
''')
    def license(self):os.system(f'start notepad ../LICENSE')

def main(config):
    app=QApplication(sys.argv)
    app.setStyle('Fusion')
    translator=QTranslator()
    translator.load(QLocale(),'fgoI18n','.')
    app.installTranslator(translator)
    myWin=MainWindow(config)
    myWin.show()
    sys.exit(app.exec())
