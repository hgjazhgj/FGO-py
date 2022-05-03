import time
ScriptStop=type('ScriptStop',(Exception,),{'__init__':lambda self,msg='Unknown Reason':Exception.__init__(self,f'Script Stopped: {msg}')})
class Schedule:
    speed=1
    def __init__(self):
        self.reset()
        self.__stopOnDefeatedFlag=False
        self.__stopOnKizunaReisouFlag=False
        self.__stopOnSpecialDropCount=0
    def reset(self):
        self.__stopMsg=''
        self.__pauseFlag=False
        self.__stopLaterCount=-1
    def stop(self,msg='Stopd'):self.__stopMsg=msg
    def checkStop(self):
        if self.__stopMsg:raise ScriptStop(self.__stopMsg)
    def pause(self):self.__pauseFlag=not self.__pauseFlag
    def checkSuspend(self):
        while self.__pauseFlag:
            self.checkStop()
            time.sleep(.07)
    def stopLater(self,count=-1):self.__stopLaterCount=count
    def checkStopLater(self):
        self.__stopLaterCount-=1
        if not self.__stopLaterCount:raise ScriptStop('Stop Appointment Effected')
    def sleep(self,x,part=.07):
        timer=time.time()+(x-part)/self.speed
        while time.time()<timer:
            self.checkSuspend()
            self.checkStop()
            time.sleep(part/self.speed)
        time.sleep(max(0,timer+part/self.speed-time.time()))
    def stopOnDefeated(self,x):self.__stopOnDefeatedFlag=x
    def checkDefeated(self):
        if self.__stopOnDefeatedFlag:raise ScriptStop('Battle Defeated')
    def stopOnKizunaReisou(self,x):self.__stopOnKizunaReisouFlag=x
    def checkKizunaReisou(self):
        if self.__stopOnKizunaReisouFlag:raise ScriptStop('Kizuna Reisou')
    def stopOnSpecialDrop(self,x=0):self.__stopOnSpecialDropCount=x
    def checkSpecialDrop(self):
        self.__stopOnSpecialDropCount-=1
        if not self.__stopOnSpecialDropCount:raise ScriptStop('Special Drop')
schedule=Schedule()
