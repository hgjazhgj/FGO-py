from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox,QInputDialog
from PyQt5.QtCore import Qt,QTranslator
import PyQt5
from airtest.core.android.adb import ADB
import os,sys,cv2,threading,configparser,traceback

from ui.fgoMainWindow import Ui_fgoMainWindow
import fgoFunc

class NewConfigParser(configparser.ConfigParser):
    def optionxform(self,optionstr):return optionstr
config=NewConfigParser()
config.read('fgoConfig.ini')

class MyMainWindow(QMainWindow):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.ui=Ui_fgoMainWindow()
        self.ui.setupUi(self)
        self.ui.CBX_PARTY.clear()
        self.ui.CBX_PARTY.addItems(config.sections())
        self.ui.CBX_PARTY.setCurrentIndex(-1)
        self.loadParty('DEFAULT')
        self.serialno=fgoFunc.base.serialno
        self.IMG_FRIEND=fgoFunc.IMG_FRIEND
    def runFunc(self,func,*args,**kwargs):
        if self.serialno is None:
            QMessageBox.critical(self,'Error','无设备连接',QMessageBox.Ok)
            return
        def f():
            try:
                self.ui.BTN_ONEBATTLE.setEnabled(False)
                self.ui.BTN_MAIN.setEnabled(False)
                self.ui.BTN_PAUSE.setEnabled(True)
                self.ui.BTN_STOP.setEnabled(True)
                self.applyAll()
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
                fgoFunc.beep()
        threading.Thread(target=f).start()
    def loadParty(self,x):
        skillInfo=eval(config[x]['skillInfo'])
        houguInfo=eval(config[x]['houguInfo'])
        dangerPos=eval(config[x]['dangerPos'])
        for i,j,k in((i,j,k)for i in range(6)for j in range(3)for k in range(3)):eval('self.ui.TXT_SKILL_'+str(i)+'_'+str(j)+'_'+str(k)+'.setText("'+str(skillInfo[i][j][k])+'")')
        for i,j in((i,j)for i in range(6)for j in range(2)):eval('self.ui.TXT_HOUGU_'+str(i)+'_'+str(j)+'.setText("'+str(houguInfo[i][j])+'")')
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
    def resetParty(self):self.loadParty('DEFAULT')
    def getDevice(self):
        text,ok=(lambda adbList:QInputDialog.getItem(self,'更改安卓设备','在下拉列表中选择',adbList,adbList.index(self.serialno)if self.serialno and self.serialno in adbList else 0))([i for i,j in ADB().devices()if j=='device'])
        if ok and text:self.serialno=text
    def adbConnect(self):
        text,ok=QInputDialog.getText(self,'连接远程设备','adb connect',text='localhost:5555')
        if ok and text:ADB(text)
    def checkCheck(self):fgoFunc.Check(0).show()
    def getFriend(self):self.IMG_FRIEND=[[file[:-4],cv2.imread('image/friend/'+file)]for file in os.listdir('image/friend')if file.endswith('.png')]
    def applyAll(self):
        fgoFunc.suspendFlag=False
        fgoFunc.terminateFlag=False
        fgoFunc.fuse.reset()
        fgoFunc.skillInfo=[[[int((lambda self:eval('self.ui.TXT_SKILL_'+str(i)+'_'+str(j)+'_'+str(k)+'.text()'))(self))for k in range(3)]for j in range(3)]for i in range(6)]
        fgoFunc.houguInfo=[[int((lambda self:eval('self.ui.TXT_HOUGU_'+str(i)+'_'+str(j)+'.text()'))(self))for j in range(2)]for i in range(6)]
        fgoFunc.dangerPos=[int((lambda self:eval('self.ui.TXT_DANGER_'+str(i)+'.text()'))(self))for i in range(3)]
        fgoFunc.friendPos=int(self.ui.BTG_FRIEND.checkedButton().objectName()[-1])
        if self.serialno!=fgoFunc.base.serialno:
            fgoFunc.base=fgoFunc.Base(self.serialno)
        fgoFunc.IMG_FRIEND=self.IMG_FRIEND
    def runOneBattle(self):self.runFunc(fgoFunc.oneBattle)
    def runMain(self):self.runFunc(fgoFunc.main,self.ui.TXT_APPLE.value(),self.ui.CBX_APPLE.currentIndex())
    def runUser(self):pass
    def pause(self):fgoFunc.suspendFlag=not fgoFunc.suspendFlag
    def stop(self):fgoFunc.terminateFlag=True
    def openFolder(self):os.startfile(os.getcwd())
    def stayOnTop(self):
        self.setWindowFlags(self.windowFlags()^Qt.WindowStaysOnTopHint)
        self.show()
    def about(self):QMessageBox.about(self,'关于','作者:\thgjazhgj\n项目地址:https://github.com/hgjazhgj/FGO-py\n联系方式:huguangjing0411@geektip.cc')

if __name__=='__main__':
    app=QApplication(sys.argv)
    translator=QTranslator()
    translator.load(os.path.dirname(PyQt5.__file__)+r'\Qt\translations\qt_zh_CN.qm')
    app.installTranslator(translator)
    myWin=MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
