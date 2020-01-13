from os import system as cmd

cmd('adb connect localhost:5555')
adbPath='adb -s localhost:5555'
dpx=0
#adbPath='adb -s emulator-5554'
#adbPath='adb -s 1e1b7921'
#dpx=120
#slnPath='E:/VisualStudioDocs/fgo_py/'

def tap(x,y):
    cmd(adbPath+' shell input tap {} {}'.format(x+dpx,y))
def swipe(rect,interval=500):
    cmd(adbPath+' shell input swipe {} {} {} {} {}'.format(rect[0]+dpx,rect[1],rect[2]+dpx,rect[3],interval))
#def screenShot(path=slnPath,name=''):
#    cmd(adbPath+' shell screencap /sdcard/adbtemp/screen.png')
#    cmd(adbPath+' pull /sdcard/adbtemp/screen.png "{path}ScreenShots/{name}.png"'.format(path=path,name=name if name!=''else time.strftime("%Y-%m-%d_%H.%M.%S",time.localtime())))

