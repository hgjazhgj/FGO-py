from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from ui.MainWindow import Ui_MainWindow
import time,os,sys,threading,configparser,traceback,win32gui,win32api
import fgoFunc

class NewConfigParser(configparser.ConfigParser):
    def optionxform(self,optionstr):return optionstr
config=NewConfigParser()
config.read('fgoConfig.ini')

class MyMainWindow(QMainWindow):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.loadData('DEFAULT')
        self.getDevice()
        self.hFgoWnd=fgoFunc.hFgoWnd
        self.hPreFgoWnd=fgoFunc.hPreFgoWnd
    def runFunc(self,func,*args,**kwargs):
        self.ui.BTN_ONEBATTLE.setEnabled(False)
        self.ui.BTN_MAIN.setEnabled(False)
        self.ui.BTN_PAUSE.setEnabled(True)
        self.ui.BTN_STOP.setEnabled(True)
        def f():
            try:
                fgoFunc.suspendFlag=False
                fgoFunc.terminateFlag=False
                fgoFunc.adbPath='adb -s '+self.ui.CBX_DEVICE.currentText()
                fgoFunc.setAndroid()
                for i in range(6):
                    for j in range(3):
                        for k in range(3):
                            fgoFunc.skillInfo[i][j][k]=int(eval('self.ui.TXT_SKILL_'+str(i)+'_'+str(j)+'_'+str(k)+'.text()'))
                    for j in range(2):
                        fgoFunc.houguInfo[i][j]=int(eval('self.ui.TXT_HOUGU_'+str(i)+'_'+str(j)+'.text()'))
                for i in range(3):
                    fgoFunc.dangerPos[i]=int(eval('self.ui.TXT_DANGER_'+str(i)+'.text()'))
                for i in range(6):
                    if eval('self.ui.RBT_'+str(i)+'.isChecked()'):
                        fgoFunc.friendPos=i
                        break
                fgoFunc.hFgoWnd=self.hFgoWnd
                fgoFunc.hPreFgoWnd=self.hPreFgoWnd
                func(*args,**kwargs)
            except BaseException as e:
                if type(e)!=SystemExit:
                    print(e)
                    traceback.print_exc()
            finally:
                self.ui.BTN_ONEBATTLE.setEnabled(True)
                self.ui.BTN_MAIN.setEnabled(True)
                self.ui.BTN_PAUSE.setEnabled(False)
                self.ui.BTN_STOP.setEnabled(False)
                #self.setWindowState(Qt.WindowActive)
                win32gui.SetForegroundWindow(fgoFunc.hPreFgoWnd)
                fgoFunc.beep()
        self.proc=threading.Thread(target=f)
        self.proc.start()
    def loadData(self,x):
        skillInfo=eval(config.get(x,'skillInfo'))
        houguInfo=eval(config.get(x,'houguInfo'))
        dangerPos=eval(config.get(x,'dangerPos'))
        friendPos=config.getint(x,'friendPos')
        for i in range(6):
            for j in range(3):
                for k in range(3):
                    eval('self.ui.TXT_SKILL_'+str(i)+'_'+str(j)+'_'+str(k)+'.setText("'+str(skillInfo[i][j][k])+'")')
            for j in range(2):
                eval('self.ui.TXT_HOUGU_'+str(i)+'_'+str(j)+'.setText("'+str(houguInfo[i][j])+'")')
        for i in range(3):
            eval('self.ui.TXT_DANGER_'+str(i)+'.setText("'+str(dangerPos[i])+'")')
        eval('self.ui.RBT_'+str(friendPos)+'.setChecked(True)')
    def saveData(self,x):
        if QMessageBox.warning(self,'Warning','先前的数据将丢失且不可找回.',QMessageBox.Ok|QMessageBox.Cancel,QMessageBox.Cancel)==QMessageBox.Cancel:return
        skillInfo=[[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]],[[4,0,0],[4,0,0],[4,0,0]]]
        houguInfo=[[1,1],[1,1],[1,1],[1,1],[1,1],[1,1]]
        dangerPos=[0,0,1]
        for i in range(6):
            for j in range(3):
                for k in range(3):
                    skillInfo[i][j][k]=int(eval('self.ui.TXT_SKILL_'+str(i)+'_'+str(j)+'_'+str(k)+'.text()'))
            for j in range(2):
                houguInfo[i][j]=int(eval('self.ui.TXT_HOUGU_'+str(i)+'_'+str(j)+'.text()'))
        for i in range(3):
            dangerPos[i]=int(eval('self.ui.TXT_DANGER_'+str(i)+'.text()'))
        for i in range(6):
            if eval('self.ui.RBT_'+str(i)+'.isChecked()'):
                friendPos=i
                break
        config.set(x,'skillInfo',str(skillInfo).replace(' ',''))
        config.set(x,'houguInfo',str(houguInfo).replace(' ',''))
        config.set(x,'dangerPos',str(dangerPos).replace(' ',''))
        config.set(x,'friendPos',str(friendPos))
        with open('fgoConfig.ini','w')as f:
            config.write(f)
    def runOneBattle(self):self.runFunc(fgoFunc.oneBattle)
    def runMain(self):self.runFunc(fgoFunc.main,int(self.ui.TXT_APPLE.text()),self.ui.CBX_APPLE.currentIndex())
    def checkCheck(self):fgoFunc.Check(0,fgoFunc.windowCapture(self.hFgoWnd)).show()
    def getHwnd(self):
        if QMessageBox.information(self,'Hint','将此对话框移到fgo画面上方,\n然后鼠标点击OK按钮.',QMessageBox.Ok|QMessageBox.Cancel,QMessageBox.Cancel)==QMessageBox.Cancel:return
        fgoFunc.hFgoWnd=win32gui.WindowFromPoint(win32api.GetCursorPos())
        fgoFunc.hPreFgoWnd=fgoFunc.hFgoWnd
        while win32gui.GetParent(fgoFunc.hPreFgoWnd)!=0:
            fgoFunc.hPreFgoWnd=win32gui.GetParent(fgoFunc.hPreFgoWnd)
    def adbConnect(self):
        os.system('adb connect '+self.ui.TXT_ADDRESS.text())
        self.getDevice()
    def adbDisconnect(self):
        os.system('adb disconnect '+self.ui.TXT_ADDRESS.text())
        self.getDevice()
    def getDevice(self):
        self.ui.CBX_DEVICE.clear()
        with os.popen('adb devices')as p:
            self.ui.CBX_DEVICE.addItems([i[:-7]for i in p.read().split('\n')if i.endswith('\tdevice')])
    def pause(self):fgoFunc.suspendFlag=True
    def stop(self):fgoFunc.terminateFlag=True
    def loadData1(self):self.loadData('party1')
    def loadData2(self):self.loadData('party2')
    def loadData3(self):self.loadData('party3')
    def loadData4(self):self.loadData('party4')
    def loadData5(self):self.loadData('party5')
    def loadData6(self):self.loadData('party6')
    def loadData7(self):self.loadData('party7')
    def loadData8(self):self.loadData('party8')
    def loadDataDefault(self):self.loadData('DEFAULT')
    def saveData1(self):self.saveData('party1')
    def saveData2(self):self.saveData('party2')
    def saveData3(self):self.saveData('party3')
    def saveData4(self):self.saveData('party4')
    def saveData5(self):self.saveData('party5')
    def saveData6(self):self.saveData('party6')
    def saveData7(self):self.saveData('party7')
    def saveData8(self):self.saveData('party8')

if __name__=='__main__':
    app=QApplication(sys.argv)
    fgoFunc.winScale=1
    myWin=MyMainWindow()
    #myWin.setWindowFlags(Qt.WindowStaysOnTopHint)
    #rect=win32gui.GetWindowRect(fgoFunc.hFgoWnd)
    #myWin.move(rect[0]+600,rect[1]+225)
    #win32gui.MoveWindow(fgoFunc.hConWnd,rect[0]+185,rect[1]+225,415,600,True)
    myWin.show()
    sys.exit(app.exec_())
