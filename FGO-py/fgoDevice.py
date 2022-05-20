from fgoAndroid import Android
from fgoDetect import Detect
from fgoSchedule import schedule
from fgoWin32 import Window
from fgoWsa import Wsa
from fgoLogging import getLogger
logger=getLogger('Device')

helpers={}
def regHelper(func):
    helpers[func.__name__]=func
    return func
def convert(text):
    if text is None:return None
    if not text.startswith('/'):return text
    try:return helpers[text[1:]]()
    except Exception as e:return logger.exception(e)

@regHelper
def gw():
    import netifaces
    return f'{netifaces.gateways()["default"][netifaces.AF_INET][0]}:5555'
@regHelper
def bs4():
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\BlueStacks_bgp64_hyperv\Guests\Android\Config')as key:return'127.0.0.1:'+winreg.QueryValueEx(key,"BstAdbPort")[0]
@regHelper
def bs5():
    import os,re,winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\BlueStacks_nxt')as key:dir=winreg.QueryValueEx(key,'UserDefinedDir')[0]
    with open(os.path.join(dir,'bluestacks.conf'))as f:return'127.0.0.1:'+re.search(r'bst\.instance\.Nougat64\.status\.adb_port="(\d*)"',f.read()).group(1)

class Device:
    def __init__(self,name=None):
        if not name:self.I=self.O=Android()
        elif'|'in name:self.I,self.O=[self.createDevice(i)for i in name.split('|')]
        else:self.I=self.O=self.createDevice(name)
        self.press=self.I.press
        self.touch=self.I.touch
        self.swipe=self.I.swipe
        Detect.screenshot=self.screenshot=self.O.screenshot
    @staticmethod
    def createDevice(name):
        if name.lower()=='wsa':return Wsa()
        if name.lower().startswith('win32'):return Window(int(name.split('_')[1],16)if'_'in name else Window.enumDevices()[0])
        return Android(convert(name))
    @property
    def available(self):return self.I.available and self.O.available
    @property
    def name(self):return self.I.name if self.I is self.O else'|'.join((self.I.name,self.O.name))
    def perform(self,pos,wait):[(self.press(i),schedule.sleep(j*.001))for i,j in zip(pos,wait)]
    enumDevices=Android.enumDevices