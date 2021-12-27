from fgoControl import ScriptTerminate
from fgoLogging import getLogger
logger=getLogger('Fuse')
class Fuse:
    def __init__(self,fv=300,logsize=10):
        self.value=0
        self.max=fv
        self.logsize=logsize
        self.log=[None]*logsize
        self.logptr=0
    def increase(self):
        logger.debug(f'{self.value}')
        if self.value>self.max:
            self.save()
            raise ScriptTerminate('Fused')
        self.value+=1
    def reset(self,check=None):
        self.value=0
        if check is not None and check is not self.log[(self.logptr-1)%self.logsize]:
            self.log[self.logptr]=check
            self.logptr=(self.logptr+1)%self.logsize
        return True
    def save(self,path='fgoLog'):[self.log[(i+self.logptr)%self.logsize].save(f'{path}/FuseLog_{i:02}') for i in range(self.logsize)if self.log[(i+self.logptr)%self.logsize]]
fuse=Fuse()
