import re,threading,time,cv2,numpy
from airtest.core.android.adb import ADB
from airtest.core.android.android import Android as Airtest
from airtest.core.android.constant import CAP_METHOD
from fgoConst import KEYMAP
from fgoLogging import getLogger
logger=getLogger('Android')

class Android(Airtest):
    def __init__(self,serial=None,**kwargs):
        self.lock=threading.Lock()
        if serial is None or serial=='None':
            self.name=None
            return
        try:
            super().__init__(serial,**{'cap_method':CAP_METHOD.JAVACAP}|kwargs)
            self.rotation_watcher.reg_callback(lambda _:self.adjustOffset())
        except Exception as e:
            logger.exception(e)
            self.name=None
        else:self.name=self.serialno
    @property
    def available(self):
        if not self.name:return False
        if self.touch_proxy.server_proc.poll()is None:return True # Only compatible with minitouch & maxtouch
        self.name=None
        return False
    @staticmethod
    def enumDevices():return[i for i,_ in ADB().devices('device')]
    def adjustOffset(self):
        self.render=[round(i)for i in self.get_render_resolution(True)]
        self.scale,self.border=(720/self.render[3],(round(self.render[2]-self.render[3]*16/9)>>1,0))if self.render[2]*9>self.render[3]*16 else(1280/self.render[2],(0,round(self.render[3]-self.render[2]*9/16)>>1))
        self.key={c:[round(p[i]/self.scale+self.border[i]+self.render[i])for i in range(2)]for c,p in KEYMAP.items()}
    def touch(self,pos):
        with self.lock:super().touch([round(pos[i]/self.scale+self.border[i]+self.render[i])for i in range(2)])
    # def swipe(self,rect):
    #     with self.lock:super().swipe(*[[rect[i<<1|j]/self.scale+self.border[j]+self.render[j]for j in range(2)]for i in range(2)])
    def swipe(self,rect): # If this doesn't work, use the above one instead
        p1,p2=[numpy.array(self._touch_point_by_orientation([rect[i<<1|j]/self.scale+self.border[j]+self.render[j]for j in range(2)]))for i in range(2)]
        vd=p2-p1
        lvd=numpy.linalg.norm(vd)
        vd/=.2*self.scale*lvd
        vx=numpy.array([0.,0.])
        def send(method,pos):self.touch_proxy.handle(' '.join((method,'0',*[str(i)for i in self.touch_proxy.transform_xy(*pos)],'50\nc\n')))
        with self.lock:
            send('d',p1)
            time.sleep(.01)
            for _ in range(2):
                send('m',p1+vx)
                vx+=vd
                time.sleep(.02)
            vd*=5
            while numpy.linalg.norm(vx)<lvd:
                send('m',p1+vx)
                vx+=vd
                time.sleep(.008)
            send('m',p2)
            time.sleep(.35)
            self.touch_proxy.handle('u 0\nc\n')
            time.sleep(.02)
    def press(self,key):
        with self.lock:super().touch(self.key[key])
    def screenshot(self):return cv2.resize(super().snapshot()[self.render[1]+self.border[1]:self.render[1]+self.render[3]-self.border[1],self.render[0]+self.border[0]:self.render[0]+self.render[2]-self.border[0]],(1280,720),interpolation=cv2.INTER_CUBIC)
    def invoke169(self):
        x,y=(lambda r:(int(r.group(1)),int(r.group(2))))(re.search(r'(\d+)x(\d+)',self.adb.raw_shell('wm size')))
        if x<y:
            if x*16<y*9:self.adb.raw_shell('wm size %dx%d'%(x,x*16//9))
        else:
            if y*16<x*9:self.adb.raw_shell('wm size %dx%d'%(y*16//9,y))
        self.adjustOffset()
    def revoke169(self):self.adb.raw_shell('wm size reset')
