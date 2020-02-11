from PyQt5.QtWidgets import QApplication,QMainWindow
from ui.MainWindow import Ui_MainWindow
import sys,threading,ctypes
from fgoFunc import *

class MyMainWindow(QMainWindow):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
    def runFunc(self,func,*args,**kwargs):
        self.ui.BTN_ONEBATTLE.setEnabled(False)
        self.ui.BTN_MAIN.setEnabled(False)
        setInfo(self.ui.TXT_INFO.text())
        def f():
            try:
                func(*args,**kwargs)
            finally:
                beep()
                self.ui.BTN_ONEBATTLE.setEnabled(True)
                self.ui.BTN_MAIN.setEnabled(True)
        self.thread=threading.Thread(target=f)
        self.thread.start()
    def loadData(self,x):
        pass
    def saveData(self,x):
        pass
    def runOneBattle(self):self.runFunc(oneBattle)
    def runMain(self):self.runFunc(main)
    def loadData1(self):self.loadData(1)
    def loadData2(self):self.loadData(2)
    def loadData3(self):self.loadData(3)
    def loadData4(self):self.loadData(4)
    def loadData5(self):self.loadData(5)
    def loadData6(self):self.loadData(6)
    def loadData7(self):self.loadData(7)
    def loadData8(self):self.loadData(8)
    def saveData1(self):self.saveData(1)
    def saveData2(self):self.saveData(2)
    def saveData3(self):self.saveData(3)
    def saveData4(self):self.saveData(4)
    def saveData5(self):self.saveData(5)
    def saveData6(self):self.saveData(6)
    def saveData7(self):self.saveData(7)
    def saveData8(self):self.saveData(8)

if __name__=='__main__':
    app=QApplication(sys.argv)
    myWin=MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
