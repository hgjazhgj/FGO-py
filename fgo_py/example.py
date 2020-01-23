from fgo_py import *
import traceback
show(windowCapture())
Check().show()
exit(0)
try:
    #draw()
    #show(windowCapture())
    print(getTime())
    setInfo('archer')
    oneBattle()
    #main(danger=(0,0,1))
    #oneBattle((0,2,1))
    #main(0,0,danger=(0,2,1))
except BaseException as e:
    if type(e)!=SystemExit:
        print(e)
        traceback.print_exc()
finally:
    print(getTime())
    playSound()
    os.system("pause");

