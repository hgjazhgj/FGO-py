from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox,QInputDialog
from PyQt5.QtCore import Qt,QEvent
import time,os,sys,cv2,re,threading,configparser,traceback#,win32gui,win32api

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
        #self.hFgoWnd=fgoFunc.hFgoWnd
        #self.hPreFgoWnd=fgoFunc.hPreFgoWnd
        #self.adbPath=fgoFunc.adbPath
        #self.tapOffset=fgoFunc.tapOffset
        #self.androidScale=fgoFunc.androidScale
        self.IMG_FRIEND=fgoFunc.IMG_FRIEND
    def runFunc(self,func,*args,**kwargs):
        #if self.adbPath=='adb':
        #    QMessageBox.critical(self,'Error','无设备连接',QMessageBox.Ok)
        #    return
        def f():
            try:
                self.ui.BTN_ONEBATTLE.setEnabled(False)
                self.ui.BTN_MAIN.setEnabled(False)
                self.ui.BTN_PAUSE.setEnabled(True)
                self.ui.BTN_STOP.setEnabled(True)
                fgoFunc.suspendFlag=False
                fgoFunc.terminateFlag=False
                fgoFunc.fuse.reset()
                fgoFunc.skillInfo=[[[int((lambda self:eval('self.ui.TXT_SKILL_'+str(i)+'_'+str(j)+'_'+str(k)+'.text()'))(self))for k in range(3)]for j in range(3)]for i in range(6)]
                fgoFunc.houguInfo=[[int((lambda self:eval('self.ui.TXT_HOUGU_'+str(i)+'_'+str(j)+'.text()'))(self))for j in range(2)]for i in range(6)]
                fgoFunc.dangerPos=[int((lambda self:eval('self.ui.TXT_DANGER_'+str(i)+'.text()'))(self))for i in range(3)]
                fgoFunc.friendPos=int(self.ui.BTG_FRIEND.checkedButton().objectName()[-1])
                #fgoFunc.hFgoWnd=self.hFgoWnd
                #fgoFunc.hPreFgoWnd=self.hPreFgoWnd
                #fgoFunc.adbPath=self.adbPath
                #fgoFunc.tapOffset=self.tapOffset
                #fgoFunc.androidScale=self.androidScale
                #fgoFunc.IMG_FRIEND=self.IMG_FRIEND
                func(*args,**kwargs)
            except BaseException as e:
                if type(e)!=SystemExit:
                    print(e)
                    print(win32api.GetLastError())
                    traceback.print_exc()
            finally:
                self.ui.BTN_ONEBATTLE.setEnabled(True)
                self.ui.BTN_MAIN.setEnabled(True)
                self.ui.BTN_PAUSE.setEnabled(False)
                self.ui.BTN_STOP.setEnabled(False)
                #self.setWindowState(Qt.WindowActive)
                #fgoFunc.setForeground(fgoFunc.hPreFgoWnd)
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
    def getDevice(self):pass
        #with os.popen('adb devices')as p:text,ok=(lambda adbList:QInputDialog.getItem(self,'更改安卓设备','在下拉列表中选择或输入',adbList,adbList.index(self.adbPath[7:])if self.adbPath[7:]in adbList else 0))([i[:-7]for i in p.read().split('\n')if i.endswith('\tdevice')])
        #if ok and text:
        #    try:
        #        with os.popen('adb -s '+text+' shell wm size')as p:self.adbPath,self.tapOffset,self.androidScale=('adb -s '+text,)+(lambda size:((0,round(960*size[0]/size[1])-540),1920/size[1])if size[1]*1080<size[0]*1920else((round(540*size[1]/size[0])-960,0),1080/size[0]))(sorted((lambda x:[int(i)for i in x])(re.search('[0-9]{1,}x[0-9]{1,}',p.read()).group().split('x'))))
        #    except:pass
    def adbConnect(self):pass
        #text,ok=QInputDialog.getText(self,'连接远程设备','adb connect',text='localhost:5555')
        #if ok and text:
        #    with os.popen('adb connect '+text)as p:
        #        if p.read().startswith('connected to'):
        #            self.adbPath='adb -s '+text
        #            self.getDevice()
    def getHwnd(self):pass
        #if QMessageBox.information(self,'Hint','将鼠标移到fgo画面上方,\n然后回车.',QMessageBox.Ok|QMessageBox.Cancel,QMessageBox.Ok)==QMessageBox.Cancel:return
        #self.hFgoWnd=win32gui.WindowFromPoint(win32api.GetCursorPos())
        #self.hPreFgoWnd=self.hFgoWnd
        #while win32gui.GetParent(self.hPreFgoWnd):self.hPreFgoWnd=win32gui.GetParent(self.hPreFgoWnd)
    def checkCheck(self):pass#fgoFunc.Check(0).show()
    def getFriend(self):self.IMG_FRIEND=[[file[:-4],cv2.imread('image/friend/'+file)]for file in os.listdir('image/friend')if file.endswith('.png')]
    def runOneBattle(self):self.runFunc(fgoFunc.oneBattle)
    def runMain(self):self.runFunc(fgoFunc.main,int(self.ui.TXT_APPLE.text()),self.ui.CBX_APPLE.currentIndex())
    def pause(self):fgoFunc.suspendFlag=True
    def stop(self):fgoFunc.terminateFlag=True
    def openFolder(self):os.startfile(os.getcwd())
    def about(self):QMessageBox.about(self,'关于','作者:\thgjazhgj\n项目地址:https://github.com/hgjazhgj/FGO-py\n联系方式:huguangjing0411@geektip.cc')

if __name__=='__main__':
    app=QApplication(sys.argv)
    #fgoFunc.winScale=1
    myWin=MyMainWindow()
    #fgoFunc.hQtWnd=myWin.winId()
    #myWin.setWindowFlags(Qt.WindowStaysOnTopHint)
    #if win32gui.IsWindow(fgoFunc.hPreFgoWnd):
    #    x,y=win32gui.GetWindowPlacement(fgoFunc.hPreFgoWnd)[4][:2]
    #    if x>=0:
    #        myWin.move(x+600,y+150)
    #        win32gui.MoveWindow(fgoFunc.hConWnd,x+185,y+150,415,550,True)
    myWin.show()
    sys.exit(app.exec_())
