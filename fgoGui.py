from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox,QInputDialog
from PyQt5.QtGui import QIntValidator,QRegExpValidator
from PyQt5.QtCore import Qt,QRegExp,pyqtSignal
from airtest.core.android.adb import ADB
import os,sys,cv2,threading,configparser,logging

from ui.fgoMainWindow import Ui_fgoMainWindow
import fgoFunc

QTK2VK={
    Qt.Key_Left:'\x25',
    Qt.Key_Up:'\x26',
    Qt.Key_Right:'\x27',
    Qt.Key_Down:'\x28',
    Qt.Key_Backspace:'\x08',
    Qt.Key_Tab:'\x09',
    Qt.Key_Clear:'\x0C',
    Qt.Key_Return:'\x0D',
    Qt.Key_Enter:'\x0D',
    Qt.Key_Shift:'\x10',
    Qt.Key_Control:'\x11',
    Qt.Key_Alt:'\x12',
    Qt.Key_Pause:'\x13',
    Qt.Key_CapsLock:'\x14',
    Qt.Key_Escape:'\x1B',
    Qt.Key_Space:'\x20',
    Qt.Key_PageUp:'\x21',
    Qt.Key_PageDown:'\x22',
    Qt.Key_End:'\x23',
    Qt.Key_Home:'\x24',
    Qt.Key_Select:'\x29',
    Qt.Key_Print:'\x2A',
    Qt.Key_Execute:'\x2B',
    Qt.Key_Printer:'\x2C',
    Qt.Key_Insert:'\x2D',
    Qt.Key_Delete:'\x2E',
    Qt.Key_Help:'\x2F',
    Qt.Key_0:'\x30',
    Qt.Key_ParenRight:'\x30', # )
    Qt.Key_1:'\x31',
    Qt.Key_Exclam:'\x31', # !
    Qt.Key_2:'\x32',
    Qt.Key_At:'\x32', # @
    Qt.Key_3:'\x33',
    Qt.Key_NumberSign:'\x33', # #
    Qt.Key_4:'\x34',
    Qt.Key_Dollar:'\x34', # $
    Qt.Key_5:'\x35',
    Qt.Key_Percent:'\x35', # %
    Qt.Key_6:'\x36',
    Qt.Key_AsciiCircum:'\x36', # ^
    Qt.Key_7:'\x37',
    Qt.Key_Ampersand:'\x37', # &
    Qt.Key_8:'\x38',
    Qt.Key_Asterisk:'\x38', # *
    Qt.Key_9:'\x39',
    Qt.Key_ParenLeft:'\x39', # (
    Qt.Key_A:'\x41',
    Qt.Key_B:'\x42',
    Qt.Key_C:'\x43',
    Qt.Key_D:'\x44',
    Qt.Key_E:'\x45',
    Qt.Key_F:'\x46',
    Qt.Key_G:'\x47',
    Qt.Key_H:'\x48',
    Qt.Key_I:'\x49',
    Qt.Key_J:'\x4A',
    Qt.Key_K:'\x4B',
    Qt.Key_L:'\x4C',
    Qt.Key_M:'\x4D',
    Qt.Key_N:'\x4E',
    Qt.Key_O:'\x4F',
    Qt.Key_P:'\x50',
    Qt.Key_Q:'\x51',
    Qt.Key_R:'\x52',
    Qt.Key_S:'\x53',
    Qt.Key_T:'\x54',
    Qt.Key_U:'\x55',
    Qt.Key_V:'\x56',
    Qt.Key_W:'\x57',
    Qt.Key_X:'\x58',
    Qt.Key_Y:'\x59',
    Qt.Key_Z:'\x5A',
    Qt.Key_multiply:'\x6A',
    Qt.Key_F1:'\x70',
    Qt.Key_F2:'\x71',
    Qt.Key_F3:'\x72',
    Qt.Key_F4:'\x73',
    Qt.Key_F5:'\x74',
    Qt.Key_F6:'\x75',
    Qt.Key_F7:'\x76',
    Qt.Key_F8:'\x77',
    Qt.Key_F9:'\x78',
    Qt.Key_F10:'\x79',
    Qt.Key_F11:'\x7A',
    Qt.Key_F12:'\x7B',
    Qt.Key_F13:'\x7C',
    Qt.Key_F14:'\x7D',
    Qt.Key_F15:'\x7E',
    Qt.Key_F16:'\x7F',
    Qt.Key_F17:'\x80',
    Qt.Key_F18:'\x81',
    Qt.Key_F19:'\x82',
    Qt.Key_F20:'\x83',
    Qt.Key_F21:'\x84',
    Qt.Key_F22:'\x85',
    Qt.Key_F23:'\x86',
    Qt.Key_F24:'\x87',
    Qt.Key_NumLock:'\x90',
    Qt.Key_ScrollLock:'\x91',
    Qt.Key_VolumeDown:'\xAE',
    Qt.Key_VolumeUp:'\xAF',
    Qt.Key_VolumeMute:'\xAD',
    Qt.Key_MediaStop:'\xB2',
    Qt.Key_MediaPlay:'\xB3',
    Qt.Key_Plus:'\xBB', # +
    Qt.Key_Minus:'\xBD', # -
    Qt.Key_Underscore:'\xBD', # _
    Qt.Key_Equal:'\xBB', # =
    Qt.Key_Semicolon:'\xBA', # #
    Qt.Key_Colon:'\xBA', # :
    Qt.Key_Comma:'\xBC', # ,
    Qt.Key_Less:'\xBC', # <
    Qt.Key_Period:'\xBE', # .
    Qt.Key_Greater:'\xBE', # >
    Qt.Key_Slash:'\xBF',  # /
    Qt.Key_Question:'\xBF', # ?
    Qt.Key_BracketLeft:'\xDB', # [
    Qt.Key_BraceLeft:'\xDB', # {
    Qt.Key_BracketRight:'\xDD', # ]
    Qt.Key_BraceRight:'\xDD', # }
    Qt.Key_Bar:'\xDC', # |
    Qt.Key_Backslash:'\xDC', # \\
    Qt.Key_Apostrophe:'\xDE', # '
    Qt.Key_QuoteDbl:'\xDE', # "
    Qt.Key_QuoteLeft:'\xC0', # `
    Qt.Key_AsciiTilde:'\xC0', # ~
}

logger=logging.getLogger('fgoFunc.fgoGui')
logger.name='fgoGui'

class NewConfigParser(configparser.ConfigParser):
    def optionxform(self,optionstr):return optionstr
config=NewConfigParser()
config.read('fgoConfig.ini')

class MyMainWindow(QMainWindow):
    signalFuncBegin=pyqtSignal()
    signalFuncEnd=pyqtSignal()
    def __init__(self,parent=None):
        super().__init__(parent)
        self.ui=Ui_fgoMainWindow()
        self.ui.setupUi(self)
        self.ui.CBX_PARTY.addItems(config.sections())
        self.ui.CBX_PARTY.setCurrentIndex(-1)
        self.ui.TXT_PARTY.setValidator(QRegExpValidator(QRegExp('10|[0-9]'),self))
        self.loadParty('DEFAULT')
        self.serialno=fgoFunc.base.serialno
        self.getDevice()
        self.IMG_FRIEND=fgoFunc.IMG_FRIEND
        self.signalFuncBegin.connect(self.funcBegin)#,Qt.BlockingQueuedConnection)
        self.signalFuncEnd.connect(self.funcEnd)
    def keyPressEvent(self,key):
        if key.modifiers()==Qt.NoModifier:
            try:fgoFunc.base.press(QTK2VK[key.key()])
            except:pass
    def runFunc(self,func,*args,**kwargs):
        if self.serialno is None:return QMessageBox.critical(self,'错误','无设备连接',QMessageBox.Ok)
        def f():
            try:
                fgoFunc.suspendFlag=False
                fgoFunc.terminateFlag=False
                fgoFunc.fuse.reset()
                self.signalFuncBegin.emit()
                self.applyAll()
                func(*args,**kwargs)
            except Exception as e:logger.exception(e)
            finally:
                self.signalFuncEnd.emit()
                QApplication.beep()
        threading.Thread(target=f).start()
    def funcBegin(self):
        self.ui.BTN_ONEBATTLE.setEnabled(False)
        self.ui.BTN_MAIN.setEnabled(False)
        self.ui.BTN_USER.setEnabled(False)
        self.ui.MENU_SCRIPT_GACHA.setEnabled(False)
        self.ui.BTN_PAUSE.setEnabled(True)
        self.ui.BTN_STOP.setEnabled(True)
        self.ui.BTN_PAUSE.setChecked(False)
        #self.repaint()
        #self.applyAll()
    def funcEnd(self):
        self.ui.BTN_ONEBATTLE.setEnabled(True)
        self.ui.BTN_MAIN.setEnabled(True)
        self.ui.BTN_USER.setEnabled(True)
        self.ui.MENU_SCRIPT_GACHA.setEnabled(True)
        self.ui.BTN_PAUSE.setEnabled(False)
        self.ui.BTN_STOP.setEnabled(False)
    def loadParty(self,x):
        self.ui.TXT_PARTY.setText(config[x]['partyIndex'])
        skillInfo=eval(config[x]['skillInfo'])
        for i,j,k in((i,j,k)for i in range(6)for j in range(3)for k in range(3)):eval(f'self.ui.TXT_SKILL_{i}_{j}_{k}.setText("{skillInfo[i][j][k]}")')
        houguInfo=eval(config[x]['houguInfo'])
        for i,j in((i,j)for i in range(6)for j in range(2)):eval(f'self.ui.TXT_HOUGU_{i}_{j}.setText("{houguInfo[i][j]}")')
        dangerPos=eval(config[x]['dangerPos'])
        for i in range(3):eval(f'self.ui.TXT_DANGER_{i}.setText("{dangerPos[i]}")')
        eval(f'self.ui.RBT_FRIEND_{config[x]["friendPos"]}.setChecked(True)')
        masterSkill=eval(config[x]['masterSkill'])
        for i,j in((i,j)for i in range(3)for j in(range(4)if i==2else range(3))):eval(f'self.ui.TXT_MASTER_{i}_{j}.setText("{masterSkill[i][j]}")')
    def saveParty(self):
        config[self.ui.CBX_PARTY.currentText()]={
            'partyIndex':self.ui.TXT_PARTY.text(),
            'skillInfo':str([[[int((lambda self:eval(f'self.ui.TXT_SKILL_{i}_{j}_{k}.text()'))(self))for k in range(3)]for j in range(3)]for i in range(6)]).replace(' ',''),
            'houguInfo':str([[int((lambda self:eval(f'self.ui.TXT_HOUGU_{i}_{j}.text()'))(self))for j in range(2)]for i in range(6)]).replace(' ',''),
            'dangerPos':str([int((lambda self:eval(f'self.ui.TXT_DANGER_{i}.text()'))(self))for i in range(3)]).replace(' ',''),
            'friendPos':self.ui.BTG_FRIEND.checkedButton().objectName()[-1],
            'masterSkill':str([[int((lambda self:eval(f'self.ui.TXT_MASTER_{i}_{j}.text()'))(self))for j in(range(4)if i==2else range(3))]for i in range(3)]).replace(' ','')}
        with open('fgoConfig.ini','w')as f:config.write(f)
    def resetParty(self):self.loadParty('DEFAULT')
    def getDevice(self):
        text,ok=(lambda adbList:QInputDialog.getItem(self,'选取安卓设备','在下拉列表中选择一个设备',adbList,adbList.index(self.serialno)if self.serialno and self.serialno in adbList else 0,True,Qt.WindowStaysOnTopHint))([i for i,j in ADB().devices()if j=='device'])
        if ok and text:self.serialno=text
    def adbConnect(self):
        text,ok=QInputDialog.getText(self,'连接远程设备','设备地址',text='localhost:5555')
        if ok and text:ADB(text)
    def refreshDevice(self):fgoFunc.base=fgoFunc.Base(fgoFunc.base.serialno)
    def checkCheck(self):
        if fgoFunc.base.serialno is None:return QMessageBox.critical(self,'错误','无设备连接',QMessageBox.Ok)
        fgoFunc.Check(0).show()
    def getFriend(self):self.IMG_FRIEND=[[file[:-4],cv2.imread(f'image/friend/{i}')]for i in os.listdir('image/friend')if i.endswith('.png')]
    def applyAll(self):
        fgoFunc.partyIndex=int(self.ui.TXT_PARTY.text())
        fgoFunc.skillInfo=[[[int((lambda self:eval(f'self.ui.TXT_SKILL_{i}_{j}_{k}.text()'))(self))for k in range(3)]for j in range(3)]for i in range(6)]
        fgoFunc.houguInfo=[[int((lambda self:eval(f'self.ui.TXT_HOUGU_{i}_{j}.text()'))(self))for j in range(2)]for i in range(6)]
        fgoFunc.dangerPos=[int((lambda self:eval(f'self.ui.TXT_DANGER_{i}.text()'))(self))for i in range(3)]
        fgoFunc.friendPos=int(self.ui.BTG_FRIEND.checkedButton().objectName()[-1])
        fgoFunc.masterSkill=[[int((lambda self:eval(f'self.ui.TXT_MASTER_{i}_{j}.text()'))(self))for j in(range(4)if i==2else range(3))]for i in range(3)]
        if self.serialno!=fgoFunc.base.serialno:fgoFunc.base=fgoFunc.Base(self.serialno)
        fgoFunc.IMG_FRIEND=self.IMG_FRIEND
    def runOneBattle(self):self.runFunc(fgoFunc.oneBattle)
    def runUser(self):self.runFunc(fgoFunc.userScript)
    def runGacha(self):self.runFunc(fgoFunc.gacha)
    def runMain(self):
        text,ok=QInputDialog.getItem(self,'肝哪个','在下拉列表中选择战斗函数',['oneBattle','userScript'])
        if ok and text:self.runFunc(fgoFunc.main,self.ui.TXT_APPLE.value(),self.ui.CBX_APPLE.currentIndex(),eval('fgoFunc.'+text))
    def pause(self):fgoFunc.suspendFlag=not fgoFunc.suspendFlag
    def stop(self):fgoFunc.terminateFlag=True
    def openFolder(self):os.startfile(os.getcwd())
    def cmdHere(self):os.system('start cmd')
    def stayOnTop(self):
        self.setWindowFlags(self.windowFlags()^Qt.WindowStaysOnTopHint)
        self.show()
    def mapKey(self,x):self.grabKeyboard()if x else self.releaseKeyboard()
    def about(self):QMessageBox.about(self,'关于','作者:\thgjazhgj  \n项目地址:https://github.com/hgjazhgj/FGO-py  \n联系方式:huguangjing0411@geektip.cc  \n防呆不放蠢,大力出奇迹!')

if __name__=='__main__':
    app=QApplication(sys.argv)
    myWin=MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())
