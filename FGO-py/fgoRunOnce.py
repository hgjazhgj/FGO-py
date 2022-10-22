from fgoLogging import getLogger
logger=getLogger('RunOnce')

def less(x,y):
    logger.info(f'Upgrading to {x}')
    return x.removeprefix('v').split('.')<y.removeprefix('v').split('.')

RUNONCE=[]
def regRunOnce(func):
    RUNONCE.append((func.__name__,func))
    return func

def runOnce(src):
    for dst,func in RUNONCE:
        if less(src,dst):
            func()
    logger.debug('Please restart FGO-py manually to complete the upgrade.')
    logger.info('Please restart FGO-py manually to complete the upgrade.')
    logger.warning('Please restart FGO-py manually to complete the upgrade.')
    logger.critical('Please restart FGO-py manually to complete the upgrade.')
    logger.error('Please restart FGO-py manually to complete the upgrade.')

@regRunOnce
def v9_8_0():
    import os
    os.system('pip install --upgrade airtest')
