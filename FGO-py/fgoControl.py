import time
ScriptTerminate=type('ScriptTerminate',(Exception,),{'__init__':lambda self,msg='Unknown Reason':Exception.__init__(self,f'Script Stopped: {msg}')})
class Control:
    speed=1
    def __init__(self):
        self.reset()
        self.__stopOnDefeatedFlag=False
        self.__stopOnKizunaReisouFlag=False
        self.__stopOnSpecialDropCount=0
    def reset(self):
        self.__terminateMsg=''
        self.__suspendFlag=False
        self.__terminateLaterCount=-1
    def terminate(self,msg='Terminated'):self.__terminateMsg=msg
    def checkTerminate(self):
        if self.__terminateMsg:raise ScriptTerminate(self.__terminateMsg)
    def suspend(self):self.__suspendFlag=not self.__suspendFlag
    def checkSuspend(self):
        while self.__suspendFlag:
            self.checkTerminate()
            time.sleep(.07)
    def terminateLater(self,count=-1):self.__terminateLaterCount=count
    def checkTerminateLater(self):
        self.__terminateLaterCount-=1
        if not self.__terminateLaterCount:raise ScriptTerminate('Terminate Appointment Effected')
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
    def stopOnKizunaReisou(self,x):self.__stopOnKizunaReisouFlag=x
    def checkKizunaReisou(self):
        if self.__stopOnKizunaReisouFlag:raise ScriptTerminate('Kizuna Reisou')
    def stopOnSpecialDrop(self,x=0):self.__stopOnSpecialDropCount=x
    def checkSpecialDrop(self):
        self.__stopOnSpecialDropCount-=1
        if not self.__stopOnSpecialDropCount:raise ScriptTerminate('Special Drop')
control=Control()
