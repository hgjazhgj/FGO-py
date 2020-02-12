from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from ui.MainWindow import Ui_MainWindow
import sys,threading,configparser,win32gui
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
    def runFunc(self,func,*args,**kwargs):
        self.ui.BTN_APPLY.setEnabled(False)
        self.ui.BTN_ONEBATTLE.setEnabled(False)
        self.ui.BTN_MAIN.setEnabled(False)
        def f():
            try:
                func(*args,**kwargs)
            finally:
                fgoFunc.beep()
                self.ui.BTN_APPLY.setEnabled(True)
                self.ui.BTN_ONEBATTLE.setEnabled(True)
                self.ui.BTN_MAIN.setEnabled(True)
                #self.setWindowState(Qt.WindowActive)
                win32gui.SetForegroundWindow(hPreFgoWnd)
        self.thread=threading.Thread(target=f)
        self.thread.start()
    def loadData(self,x):
        fgoFunc.skillInfo[:]=eval(config.get(x,'skillInfo'))
        fgoFunc.houguInfo[:]=eval(config.get(x,'houguInfo'))
        fgoFunc.dangerPos[:]=eval(config.get(x,'dangerPos'))
        fgoFunc.friendPos=config.getint(x,'friendPos')
        for i in range(6):
            for j in range(3):
                for k in range(3):
                    eval('self.ui.TXT_SKILL_'+str(i)+'_'+str(j)+'_'+str(k)+'.setText("'+str(fgoFunc.skillInfo[i][j][k])+'")')
            for j in range(2):
                eval('self.ui.TXT_HOUGU_'+str(i)+'_'+str(j)+'.setText("'+str(fgoFunc.houguInfo[i][j])+'")')
        for i in range(3):
            eval('self.ui.TXT_DANGER_'+str(i)+'.setText("'+str(fgoFunc.dangerPos[i])+'")')
        eval('self.ui.RBT_'+str(fgoFunc.friendPos)+'.setChecked(True)')
    def saveData(self,x):
        if QMessageBox.warning(self,'Warning','先前的数据将丢失且不可找回',QMessageBox.Ok|QMessageBox.Cancel,QMessageBox.Cancel)==QMessageBox.Cancel:return
        self.applyData()
        config.set(x,'skillInfo',str(fgoFunc.skillInfo).replace(' ',''))
        config.set(x,'houguInfo',str(fgoFunc.houguInfo).replace(' ',''))
        config.set(x,'dangerPos',str(fgoFunc.dangerPos).replace(' ',''))
        config.set(x,'friendPos',str(fgoFunc.friendPos))
        with open('fgoConfig.ini','w')as f:
            config.write(f)
    def applyData(self):
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
    def runOneBattle(self):self.runFunc(fgoFunc.oneBattle)
    def runMain(self):self.runFunc(fgoFunc.main,int(self.ui.TXT_APPLE.text()),'金银铜'.find(self.ui.CBX_APPLE.currentText()))
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
    myWin=MyMainWindow()
    #myWin.setWindowFlags(Qt.WindowStaysOnTopHint)
    rect=win32gui.GetWindowRect(fgoFunc.hFgoWnd)
    myWin.move(rect[0]+600,rect[1]+225)
    myWin.show()
    sys.exit(app.exec_())
