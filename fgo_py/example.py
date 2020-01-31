from fgo_py import *
import traceback
#show(windowCapture())
#Check().show()
#exit(0)
try:
    #draw()
    print(getTime())
    setInfo('saber')
    #oneBattle()
    main(danger=(0,1,0))
    #oneBattle((0,2,1))
    #main(1,0,danger=(0,1,0))
except BaseException as e:
    if type(e)!=SystemExit:
        print(e)
        traceback.print_exc()
finally:
    print(getTime())
    win32gui.SetForegroundWindow(win32console.GetConsoleWindow())
    playSound()
    os.system("pause");
