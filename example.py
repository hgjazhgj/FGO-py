from fgoFunc import *
import traceback
#show(windowCapture())
#Check().show()
#exit(0)
try:
    rect=win32gui.GetWindowRect(hFgoWnd)
    win32gui.MoveWindow(hConWnd,rect[0]+400,rect[1]+150,330,300,True)
    #draw()
    print(getTime())
    setInfo('assassin')
    oneBattle((0,1,0))
    #main(danger=(0,1,0))
    #oneBattle((0,2,1))
    #main(1,0,danger=(0,1,0))
    print(getTime())
    setForeground()
except BaseException as e:
    if type(e)!=SystemExit:
        print(e)
        traceback.print_exc()
finally:
    playSound()
    os.system("pause");
    win32gui.SetForegroundWindow(hPreFgoWnd)
    time.sleep(1)
