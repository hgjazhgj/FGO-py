import numpy,platform
from fgoLogging import getLogger
logger=getLogger('Win32')

BLACK=numpy.zeros((720,1280,3),numpy.uint8)
if platform.system()=='Windows':
    import ctypes,time,cv2,win32api,win32con,win32gui,win32ui
    from fgoConst import KEYMAP

    user32=ctypes.windll.user32
    user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4)) # -4:DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 win10 1703
    class Window:
        def __init__(self,hWnd=0):
            self.hWnd=hWnd
            self.name=f'Win32_{hex(self.hWnd)}'
            # self.dpiAwareness=user32.GetAwarenessFromDpiAwarenessContext(user32.GetThreadDpiAwarenessContext()) # win10 1607
            self.hWndDC=win32gui.GetDC(self.hWnd)
            self.hMfcDc=win32ui.CreateDCFromHandle(self.hWndDC)
            self.hMemDc=self.hMfcDc.CreateCompatibleDC()
        @property
        def available(self):
            return win32gui.IsWindow(self.hWnd)
        @staticmethod
        def enumDevices():
            wnds=[win32gui.WindowFromPoint(win32api.GetCursorPos())]
            win32gui.EnumChildWindows(wnds[0],lambda hWnd,_:wnds.append(hWnd),0)
            result=None
            for hWnd in wnds:
                w=Window(hWnd)
                cv2.imshow(f'{hex(hWnd)} - press i to test mouse input, q to quit, y to confirm, any other key to next',cv2.resize(w.screenshot(),(0,0),fx=.6,fy=.6))
                while True:
                    key=cv2.waitKey(0)
                    if key==ord('y'):
                        result=hWnd
                        break
                    elif key==ord('i'):w.press(' ')
                    elif key==ord('q'):
                        result=0
                        break
                    else:break
                cv2.destroyAllWindows()
                if result is not None:return[result]
            return[0]
        # def adjustIterableForDpi(self,pos): # when SetProcessDpiAwarenessContext failed, use this instead
        #     self.dpi=user32.GetDpiForWindow(self.hWnd) # win10 1607
        #     if self.dpiAwareness==2:return pos # 2:DPI_AWARENESS_PER_MONITOR_AWARE
        #     # elif self.dpiAwareness==1: # 1:DPI_AWARENESS_SYSTEM_AWARE current unable to handle this
        #     elif self.dpiAwareness==0:return[i*self.dpi//96 for i in pos] # 0:DPI_AWARENESS_UNAWARE
        def screenshot(self):
            self.width,self.height=win32gui.GetClientRect(self.hWnd)[2:]
            if self.width==0 or self.height==0:return BLACK
            self.scale,self.border=(720/self.height,(round(self.width-self.height*16/9)>>1,0))if self.width*9>self.height*16 else(1280/self.width,(0,round(self.height-self.width*9/16)>>1))
            hBmp=win32ui.CreateBitmap()
            hBmp.CreateCompatibleBitmap(self.hMfcDc,self.width,self.height)
            self.hMemDc.SelectObject(hBmp)
            self.hMemDc.BitBlt((0,0),(self.width,self.height),self.hMfcDc,(0,0),win32con.SRCCOPY)
            result=numpy.frombuffer(hBmp.GetBitmapBits(True),dtype=numpy.uint8)
            win32gui.DeleteObject(hBmp.GetHandle())
            return cv2.resize(result.reshape(self.height,self.width,4)[slice(self.border[1],-self.border[1])if self.border[1]else slice(None),slice(self.border[0],-self.border[0])if self.border[0]else slice(None),:3],(1280,720),interpolation=cv2.INTER_CUBIC)
        def touch(self,pos):
            lParam=round(pos[1]/self.scale+self.border[1])<<16|round(pos[0]/self.scale+self.border[0])
            win32api.PostMessage(self.hWnd,win32con.WM_LBUTTONDOWN,0,lParam)
            win32api.PostMessage(self.hWnd,win32con.WM_LBUTTONUP,0,lParam)
        def swipe(self,rect):
            p1,p2=[numpy.array([rect[i<<1|j]/self.scale+self.border[j]for j in range(2)])for i in range(2)]
            vd=p2-p1
            lvd=numpy.linalg.norm(vd)
            vd/=.2*self.scale*lvd
            vx=numpy.array([0.,0.])
            def makeLParam(p):return int(p[1])<<16|int(p[0])
            win32api.PostMessage(self.hWnd,win32con.WM_LBUTTONDOWN,0,makeLParam(p1))
            time.sleep(.01)
            for _ in range(2):
                win32api.PostMessage(self.hWnd,win32con.WM_MOUSEMOVE,win32con.MK_LBUTTON,makeLParam(p1+vx))
                vx+=vd
                time.sleep(.02)
            vd*=5
            while numpy.linalg.norm(vx)<lvd:
                win32api.PostMessage(self.hWnd,win32con.WM_MOUSEMOVE,win32con.MK_LBUTTON,makeLParam(p1+vx))
                vx+=vd
                time.sleep(.008)
            time.sleep(.35)
            win32api.PostMessage(self.hWnd,win32con.WM_LBUTTONUP,0,makeLParam(p2))
        def press(self,key):self.touch(KEYMAP[key])
        def __del__(self):
            self.hMemDc.DeleteDC()
            self.hMfcDc.DeleteDC()
            win32gui.ReleaseDC(self.hWnd,self.hWndDC)
else:
    class Window:
        name='Unavailable_on_current_platform'
        available=False
        def __init__(self,hWnd):logger.critical('Win 32 is not available on this platform')
        @staticmethod
        def enumDevices():return[0]
        def touch(self,pos):pass
        def press(self):pass
        def swipe(self):pass
        def screenshot(self):return BLACK
