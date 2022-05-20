import logging,sys,time,airtest.utils.logger
from copy import copy
from functools import wraps
from fgoConst import VERSION
if sys.platform=='win32':(lambda k:k.SetConsoleMode(k.GetStdHandle(-11),7))(__import__('ctypes').windll.kernel32) # -11:STD_OUTPUT_HANDLE, 7:ENABLE_VIRTUAL_TERMINAL_PROCESSING
def color(c,f='38'):return f'\033[{f};{c>>16&0xFF};{c>>8&0xFF};{c&0xFF}m'
logging.root.addHandler((lambda handler:(handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s]<%(name)s> %(message)s')),handler.setLevel(logging.DEBUG),handler)[-1])(logging.FileHandler(time.strftime('fgoLog/Log_%Y-%m-%d_%H.%M.%S.txt'))))
(lambda logger:(logger.setLevel(logging.DEBUG),logger.addHandler((lambda handler:(handler.setFormatter(type('ColoredFormatter',(logging.Formatter,),{'__init__':lambda self,*args,**kwargs:logging.Formatter.__init__(self,*args,**kwargs),'format':lambda self,record:((lambda record:(setattr(record,'levelname','\033[{}m[{}]'.format({'WARNING':'33','INFO':'34','DEBUG':'37','CRITICAL':'35','ERROR':'31'}.get(record.levelname,'0'),record.levelname)),logging.Formatter.format(self,record))[-1])(copy(record)))})('\033[32m[%(asctime)s]%(levelname)s\033[36m<%(name)s>\033[0m %(message)s')),handler.setLevel(logging.INFO),handler)[-1])(logging.StreamHandler()))))(logging.getLogger('fgo'))
(lambda handler:(handler.setLevel(logging.INFO),handler.setFormatter(logging.getLogger('fgo').handlers[-1].formatter)))((lambda logger:(logger.setLevel(logging.DEBUG),logger)[-1])(logging.getLogger('airtest')).handlers[0])
def getLogger(name):return logging.getLogger('fgo.'+name)
def logit(logger,level=logging.DEBUG):return lambda func:wraps(func)(lambda*args,**kwargs:(lambda x:(logger.log(level,' '.join((func.__name__,str(x)[:100].split('\n',1)[0]))),x)[-1]if x is not None else x)(func(*args,**kwargs)))
def logMeta(logger):return lambda name,bases,attrs:type(name,bases,{i:logit(logger)(j)if callable(j)and i[0]!='_'else j for i,j in attrs.items()})
logging.getLogger('fgo').info(f'FGO-py {VERSION}')
