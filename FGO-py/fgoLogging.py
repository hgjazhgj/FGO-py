import logging,platform,os,time
from copy import copy
from functools import wraps
from fgoConst import VERSION
if platform.system()=='Windows':(lambda k:k.SetConsoleMode(k.GetStdHandle(-11),7))(__import__('ctypes').windll.kernel32) # -11:STD_OUTPUT_HANDLE, 7:ENABLE_VIRTUAL_TERMINAL_PROCESSING
monoFormatter=logging.Formatter('[%(asctime)s][%(levelname)s]<%(name)s> %(message)s')
if os.getenv('NO_COLOR'):
    def color(*_,**__):return''
    coloredFormatter=monoFormatter
else:
    def color(c=None,f='38'):return'\033[0m'if c is None else f'\033[{f};2;{c>>16&0xFF};{c>>8&0xFF};{c&0xFF}m'
    coloredFormatter=type('ColoredFormatter',(logging.Formatter,),{'__init__':lambda self,*args,**kwargs:logging.Formatter.__init__(self,*args,**kwargs),'format':lambda self,record:((lambda record:(setattr(record,'levelname','\033[{}m[{}]'.format({'DEBUG':'37','INFO':'34','WARNING':'33','CRITICAL':'35','ERROR':'31'}.get(record.levelname,'0'),record.levelname)),logging.Formatter.format(self,record))[-1])(copy(record)))})('\033[32m[%(asctime)s]%(levelname)s\033[36m<%(name)s>\033[0m %(message)s')
logging.root.addHandler((lambda handler:(handler.setFormatter(monoFormatter),handler.setLevel(logging.DEBUG),handler)[-1])(logging.FileHandler(time.strftime('fgoLog/Log_%Y-%m-%d_%H.%M.%S.txt'))))
logger=logging.getLogger('fgo')
(logger.setLevel(logging.DEBUG),logger.addHandler((lambda handler:(handler.setFormatter(coloredFormatter),handler.setLevel(logging.INFO),handler)[-1])(logging.StreamHandler())))
(lambda handler:(handler.setLevel(logging.INFO),handler.setFormatter(logger.handlers[-1].formatter)))((lambda logger:(logger.setLevel(logging.DEBUG),logger)[-1])(logging.getLogger('airtest')).handlers[0])
def getLogger(name):return logging.getLogger('fgo.'+name)
def logit(logger,level=logging.DEBUG):return lambda func:wraps(func)(lambda*args,**kwargs:(lambda x:(logger.log(level,' '.join((func.__name__,str(x)[:100].split('\n',1)[0]))),x)[-1]if x is not None else x)(func(*args,**kwargs)))
def logMeta(logger):return lambda name,bases,attrs:type(name,bases,{i:logit(logger)(j)if callable(j)and i[0]!='_'else j for i,j in attrs.items()})
logger.info(f'FGO-py {VERSION}')
