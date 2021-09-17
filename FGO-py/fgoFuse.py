from fgoControl import ScriptTerminate
from fgoLogging import getLogger
logger=getLogger('Fuse')
class Fuse:
    def __init__(self,fv=300,logsize=10):
        self.__value=0
        self.__max=fv
        self.logsize=logsize
        self.log=[None]*logsize
        self.logptr=0
    @property
    def value(self):return self.__value
    @property
    def max(self):return self.__max
    def increase(self):
        logger.debug(f'{self.__value}')
        if self.__value>self.__max:
            self.save()
            raise ScriptTerminate('Fused')
        self.__value+=1
    def reset(self,check=None):
        self.__value=0
        if check is not None and check is not self.log[(self.logptr-1)%self.logsize]:
            self.log[self.logptr]=check
            self.logptr=(self.logptr+1)%self.logsize
        return True
    def save(self,path='.'):[self.log[(i+self.logptr)%self.logsize].save(f'{path}/FuseLog_%Y-%m-%d_%H.%M.%S_{i:02}.png') for i in range(self.logsize)if self.log[(i+self.logptr)%self.logsize]]
fuse=Fuse()
