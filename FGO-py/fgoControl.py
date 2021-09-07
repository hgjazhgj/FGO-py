import time
ScriptTerminate=type('ScriptTerminate',(Exception,),{'__init__':lambda self,msg='Unknown Reason':Exception.__init__(self,f'Script Stopped: {msg}')})
class Control:
    speed=1
    def __init__(self):
        self.reset()
        self.__stopOnDefeatedFlag=False
        self.__stopOnSpecialDropFlag=False
    def reset(self):
        self.__terminateFlag=False
        self.__suspendFlag=False
        self.__terminateLaterFlag=-1
    def terminate(self):self.__terminateFlag=True
    def checkTerminate(self):
        if self.__terminateFlag:raise ScriptTerminate('Terminate Command Effected')
    def suspend(self):self.__suspendFlag=not self.__suspendFlag
    def checkSuspend(self):
        while self.__suspendFlag:
            self.checkTerminate()
            time.sleep(.07/self.speed)
    def terminateLater(self,count=-1):self.__terminateLaterFlag=count
    def checkTerminateLater(self):
        if not self.__terminateLaterFlag:raise ScriptTerminate('Terminate Appointment Effected')
        self.__terminateLaterFlag-=1
    def sleep(self,x,part=.07):
        timer=time.time()+(x-part)/self.speed
        while time.time()<timer:
            self.checkSuspend()
            self.checkTerminate()
            time.sleep(part/self.speed)
        time.sleep(max(0,timer+part/self.speed-time.time()))
    def stopOnDefeated(self,x):self.__stopOnDefeatedFlag=x
    def checkDefeated(self):
        if self.__stopOnDefeatedFlag:raise ScriptTerminate('Battle Defeated')
    def stopOnSpecialDrop(self,x):self.__stopOnSpecialDropFlag=x
    def checkSpecialDrop(self):
        if self.__stopOnSpecialDropFlag:raise ScriptTerminate('Special Drop')
control=Control()
