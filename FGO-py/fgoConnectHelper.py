from fgoLogging import getLogger
logger=getLogger('ConnectHelper')

helpers={}
def regHelper(func):
    helpers[func.__name__]=func
    return func
def convert(text):
    if text is None:return None
    text=text.removeprefix(' ').removesuffix(' ')
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
