import logging
from functools import wraps
(lambda logger:(logger.setLevel(logging.DEBUG),logger.addHandler((lambda handler:(handler.setFormatter(type('ColoredFormatter',(logging.Formatter,),{'__init__':lambda self,*args,**kwargs:logging.Formatter.__init__(self,*args,**kwargs),'format':lambda self,record:(setattr(record,'levelname','\033[{}m[{}]'.format({'WARNING':'33','INFO':'34','DEBUG':'37','CRITICAL':'35','ERROR':'31'}.get(record.levelname,'0'),record.levelname)),logging.Formatter.format(self,record))[-1]})('\033[32m[%(asctime)s]%(levelname)s\033[36m<%(name)s>\033[0m %(message)s')),handler)[-1])(logging.StreamHandler()))))(logging.getLogger('fgo'))
def getLogger(name):return logging.getLogger('fgo.'+name)
def logit(logger,level=logging.DEBUG):return lambda func:wraps(func)(lambda*args,**kwargs:(lambda x:(logger.log(level,' '.join((func.__name__,str(x)[:100].split("\n",1)[0]))),x)[-1]if x is not None else x)(func(*args,**kwargs)))
def logMeta(logger):return lambda name,bases,attrs:type(name,bases,{i:logit(logger)(j)if callable(j)and i[0]!='_'else j for i,j in attrs.items()})
