from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox,QInputDialog
from PyQt5.QtCore import Qt,QEvent
from ui.MainWindow import Ui_MainWindow
import time,os,sys,threading,configparser,traceback,win32gui,win32api

os.chdir(os.path.dirname(sys.argv[0]))
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
        self.ui.CBX_PARTY.clear()
        self.ui.CBX_PARTY.addItems(config.sections())
        self.ui.CBX_PARTY.setCurrentIndex(-1)
        self.loadParty('DEFAULT')
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
                fgoFunc.fuse.reset()
                fgoFunc.adbPath='adb -s '+self.ui.CBX_DEVICE.currentText()
                fgoFunc.setAndroid()
                fgoFunc.skillInfo=[[[int((lambda self:eval('self.ui.TXT_SKILL_'+str(i)+'_'+str(j)+'_'+str(k)+'.text()'))(self))for k in range(3)]for j in range(3)]for i in range(6)]
                fgoFunc.houguInfo=[[int((lambda self:eval('self.ui.TXT_HOUGU_'+str(i)+'_'+str(j)+'.text()'))(self))for j in range(2)]for i in range(6)]
                fgoFunc.dangerPos=[int((lambda self:eval('self.ui.TXT_DANGER_'+str(i)+'.text()'))(self))for i in range(3)]
                fgoFunc.friendPos=int(self.ui.BTG_FRIEND.checkedButton().objectName()[-1])
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
                fgoFunc.setForeground(fgoFunc.hPreFgoWnd)
                fgoFunc.beep()
        self.proc=threading.Thread(target=f)
        self.proc.start()
    def loadParty(self,x):
        skillInfo=eval(config[x]['skillInfo'])
        houguInfo=eval(config[x]['houguInfo'])
        dangerPos=eval(config[x]['dangerPos'])
        for i in range(6):
            for j in range(3):
                for k in range(3):
                    eval('self.ui.TXT_SKILL_'+str(i)+'_'+str(j)+'_'+str(k)+'.setText("'+str(skillInfo[i][j][k])+'")')
            for j in range(2):
                eval('self.ui.TXT_HOUGU_'+str(i)+'_'+str(j)+'.setText("'+str(houguInfo[i][j])+'")')
        for i in range(3):eval('self.ui.TXT_DANGER_'+str(i)+'.setText("'+str(dangerPos[i])+'")')
        eval('self.ui.RBT_FRIEND_'+config[x]['friendPos']+'.setChecked(True)')
    def saveParty(self):
        if not config.has_section(self.ui.CBX_PARTY.currentText()):return
        config[self.ui.CBX_PARTY.currentText()]={
            'skillInfo':str([[[int((lambda self:eval('self.ui.TXT_SKILL_'+str(i)+'_'+str(j)+'_'+str(k)+'.text()'))(self))for k in range(3)]for j in range(3)]for i in range(6)]).replace(' ',''),
            'houguInfo':str([[int((lambda self:eval('self.ui.TXT_HOUGU_'+str(i)+'_'+str(j)+'.text()'))(self))for j in range(2)]for i in range(6)]).replace(' ',''),
            'dangerPos':str([int((lambda self:eval('self.ui.TXT_DANGER_'+str(i)+'.text()'))(self))for i in range(3)]).replace(' ',''),
            'friendPos':self.ui.BTG_FRIEND.checkedButton().objectName()[-1]}
        with open('fgoConfig.ini','w')as f:config.write(f)
    def resetParty(self):
        self.loadParty('DEFAULT')
    def deleteParty(self):pass
    def checkCheck(self):fgoFunc.Check(0,fgoFunc.windowCapture(self.hFgoWnd)).show()
    def adbConnect(self):
        os.system('adb connect '+self.ui.TXT_ADDRESS.text())
        self.getDevice()
    def adbDisconnect(self):
        os.system('adb disconnect '+self.ui.TXT_ADDRESS.text())
        self.getDevice()
    def getDevice(self):
        self.ui.CBX_DEVICE.clear()
        with os.popen('adb devices')as p:self.ui.CBX_DEVICE.addItems([i[:-7]for i in p.read().split('\n')if i.endswith('\tdevice')])
    def getHwnd(self):
        if QMessageBox.information(self,'Hint','将鼠标移到fgo画面上方,\n然后回车.',QMessageBox.Ok|QMessageBox.Cancel,QMessageBox.Ok)==QMessageBox.Cancel:return
        self.hFgoWnd=win32gui.WindowFromPoint(win32api.GetCursorPos())
        self.hPreFgoWnd=self.hFgoWnd
        while win32gui.GetParent(self.hPreFgoWnd):self.hPreFgoWnd=win32gui.GetParent(self.hPreFgoWnd)
    def runOneBattle(self):self.runFunc(fgoFunc.oneBattle)
    def runMain(self):self.runFunc(fgoFunc.main,int(self.ui.TXT_APPLE.text()),self.ui.CBX_APPLE.currentIndex())
    def pause(self):fgoFunc.suspendFlag=True
    def stop(self):fgoFunc.terminateFlag=True

if __name__=='__main__':
    app=QApplication(sys.argv)
    fgoFunc.winScale=1
    myWin=MyMainWindow()
    fgoFunc.hQtWnd=myWin.winId()
    #myWin.setWindowFlags(Qt.WindowStaysOnTopHint)
    if win32gui.IsWindow(fgoFunc.hPreFgoWnd):
        x,y=win32gui.GetWindowPlacement(fgoFunc.hPreFgoWnd)[4][:2]
        if x>=0:
            myWin.move(x+600,y+150)
            win32gui.MoveWindow(fgoFunc.hConWnd,x+185,y+150,415,550,True)
    myWin.show()
    sys.exit(app.exec_())
