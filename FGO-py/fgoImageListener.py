import os,cv2,platform
from fgoLogging import getLogger
logger=getLogger('ImageListener')

if platform.system()=='Windows':
    import threading,win32con,win32file
    class DirListener:
        def __init__(self,dir):
            self.hDir=win32file.CreateFile(dir,win32con.GENERIC_READ,win32con.FILE_SHARE_READ|win32con.FILE_SHARE_WRITE|win32con.FILE_SHARE_DELETE,None,win32con.OPEN_EXISTING,win32con.FILE_FLAG_BACKUP_SEMANTICS,None)
            self.msg=[]
            self.lock=threading.Lock()
            self.ren=''
            def f():
                while True:self.add(win32file.ReadDirectoryChangesW(self.hDir,0x1000,False,win32con.FILE_NOTIFY_CHANGE_FILE_NAME|win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,None,None))
            threading.Thread(target=f,daemon=True,name=f'DirListener({dir})').start()
        def add(self,x):
            def onCreated(file):
                for i in(i for i in range(len(self.msg)-1,-1,-1)if self.msg[i][1]==file):
                    if self.msg[i][0]==2:
                        self.msg[i][0]=3
                        return
                    break
                self.msg.append([1,file])
            def onDeleted(file):
                for i in(i for i in range(len(self.msg)-1,-1,-1)if self.msg[i][1]==file):
                    if self.msg[i][0]==1:
                        del self.msg[i]
                        return
                    if self.msg[i][0]==3:
                        del self.msg[i]
                        break
                    temp=self.msg[i-1][1]
                    del self.msg[i-1:i+1]
                    return onDeleted(temp)
                self.msg.append([2,file])
            def onUpdated(file):
                for i in(i for i in range(len(self.msg)-1,-1,-1)if self.msg[i][1]==file):
                    if self.msg[i][0]==1 or self.msg[i][0]==3:return
                    if self.msg[i][0]==5:
                        temp=self.msg[i-1][1]
                        del self.msg[i-1:i+1]
                        onDeleted(temp)
                        return onCreated(file)
                    break
                self.msg.append([3,file])
            def onRenamedFrom(file):self.ren=file
            def onRenamedTo(file):
                for i in range(len(self.msg)-1,-1,-1):
                    if self.msg[i][1]==file:break
                    if self.msg[i][1]==self.ren:
                        if self.msg[i][0]==1:
                            del self.msg[i]
                            return onCreated(file)
                        if self.msg[i][0]==3:
                            self.msg[i][0]=2
                            return onCreated(file)
                        if self.msg[i][0]==5:
                            self.ren=self.msg[i-1][1]
                            del self.msg[i-1:i+1]
                            if self.ren==file:return
                        break
                self.msg+=[[4,self.ren],[5,file]]
            with self.lock:[{1:onCreated,2:onDeleted,3:onUpdated,4:onRenamedFrom,5:onRenamedTo}.get(i[0],lambda _:logger.warning(f'Unknown Operate {i}'))(i[1])for i in x]
        def get(self):
            with self.lock:ans,self.msg=self.msg,[]
            return ans
else:
    class DirListener:
        def __init__(self,dir):pass
        def get(self):return[]
class ImageListener(dict):
    def __init__(self,path,ends='.png'):
        super().__init__((file[:-len(ends)],cv2.imread(path+file))for file in os.listdir(path)if file.endswith(ends))
        self.path=path
        self.ends=ends
        self.listener=DirListener(path)
    def flush(self):
        lastAction=0
        oldName=None
        def onCreated(name):self[name]=cv2.imread(self.path+name+self.ends)
        def onDeleted(name):del self[name]
        def onUpdated(name):self[name]=cv2.imread(self.path+name+self.ends)
        def onRenamedFrom(name):
            nonlocal oldName
            if oldName is not None:del self[oldName]
            oldName=name
        def onRenamedTo(name):self[name]=self[oldName]if lastAction==4 else cv2.imread(self.path+name+self.ends)
        for action,name in((action,file[:-len(self.ends)])for action,file in self.listener.get()if file.endswith(self.ends)):
            {1:onCreated,2:onDeleted,3:onUpdated,4:onRenamedFrom,5:onRenamedTo}.get(action,lambda _:None)(name)
            logger.info(f'{dict(((1,"Create"),(2,"Delete"),(3,"Update"),(4,"RenameFrom"),(5,"RenameTo"))).get(action,None)} {name}')
            lastAction=action
        if oldName is not None:del self[oldName]
        return self
