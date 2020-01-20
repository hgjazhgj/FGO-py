import os,re

os.system('adb connect localhost:5555')
adbPath='adb -s localhost:5555'
#adbPath='adb -s emulator-5554'
#adbPath='adb -s 1e1b7921'
with os.popen(adbPath+' shell wm size')as p:
    pixelOffset,androidScale=(lambda size:((0,round(960*size[0]/size[1])-540),1920/size[1])if size[1]*1080<size[0]*1920else((round(540*size[1]/size[0])-960,0),1080/size[0]))(sorted((lambda x:[int(i)for i in x])(re.search('[0-9]{1,}x[0-9]{1,}',p.read()).group().split('x'))))

tap=lambda x,y:os.system(adbPath+' shell input tap {} {}'.format(*[round(i*androidScale)for i in[x+pixelOffset[0],y+pixelOffset[1]]]))
swipe=lambda rect,interval=500:os.system(adbPath+' shell input swipe {} {} {} {} {}'.format(*[round(i*androidScale)for i in[rect[0]+pixelOffset[0],rect[1]+pixelOffset[1],rect[2]+pixelOffset[0],rect[3]+pixelOffset[1]]],interval))

#slnPath='E:/VisualStudioDocs/fgo_py/'
#def screenShot(path=slnPath,name=''):
#    os.system(adbPath+' shell screencap /sdcard/adbtemp/screen.png')
#    os.system(adbPath+' pull /sdcard/adbtemp/screen.png "{path}ScreenShots/{name}.png"'.format(path=path,name=name if name!=''else time.strftime("%Y-%m-%d_%H.%M.%S",time.localtime())))
