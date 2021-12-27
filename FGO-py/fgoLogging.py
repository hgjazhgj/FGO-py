import logging,time
from copy import copy
from functools import wraps
logging.root.addHandler((lambda handler:(handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s]<%(name)s> %(message)s')),handler.setLevel(logging.DEBUG),handler)[-1])(logging.FileHandler(time.strftime('fgoLog/Log_%Y-%m-%d_%H.%M.%S.txt'))))
(lambda logger:(logger.setLevel(logging.DEBUG),logger.addHandler((lambda handler:(handler.setFormatter(type('ColoredFormatter',(logging.Formatter,),{'__init__':lambda self,*args,**kwargs:logging.Formatter.__init__(self,*args,**kwargs),'format':lambda self,record:((lambda record:(setattr(record,'levelname','\033[{}m[{}]'.format({'WARNING':'33','INFO':'34','DEBUG':'37','CRITICAL':'35','ERROR':'31'}.get(record.levelname,'0'),record.levelname)),logging.Formatter.format(self,record))[-1])(copy(record)))})('\033[32m[%(asctime)s]%(levelname)s\033[36m<%(name)s>\033[0m %(message)s')),handler.setLevel(logging.INFO),handler)[-1])(logging.StreamHandler()))))(logging.getLogger('fgo'))
(lambda handler:(handler.setLevel(logging.INFO),handler.setFormatter(logging.getLogger('fgo').handlers[-1].formatter)))((lambda logger:(logger.setLevel(logging.DEBUG),logger)[-1])(logging.getLogger('airtest')).handlers[0])
def getLogger(name):return logging.getLogger('fgo.'+name)
def logit(logger,level=logging.DEBUG):return lambda func:wraps(func)(lambda*args,**kwargs:(lambda x:(logger.log(level,' '.join((func.__name__,str(x)[:100].split("\n",1)[0]))),x)[-1]if x is not None else x)(func(*args,**kwargs)))
def logMeta(logger):return lambda name,bases,attrs:type(name,bases,{i:logit(logger)(j)if callable(j)and i[0]!='_'else j for i,j in attrs.items()})
