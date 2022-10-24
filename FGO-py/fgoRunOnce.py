from fgoLogging import getLogger
logger=getLogger('RunOnce')

RUNONCE=[]
def regRunOnce(func):
    RUNONCE.append(([int(i)for i in func.__name__.removeprefix('v').split('_')],func))
    return func

def runOnce(src):
    restart=False
    src=[int(i)for i in src.removeprefix('v').split('.')]
    for dst,func in RUNONCE:
        if src<dst:
            logger.info(f'Upgrading to v{".".join(dst)}')
            func()
            restart=True
    if restart:
        logger.debug('Please restart FGO-py manually to complete the upgrade.')
        logger.info('Please restart FGO-py manually to complete the upgrade.')
        logger.warning('Please restart FGO-py manually to complete the upgrade.')
        logger.critical('Please restart FGO-py manually to complete the upgrade.')
        logger.error('Please restart FGO-py manually to complete the upgrade.')
    return restart

@regRunOnce
def v9_8_0():
    import os
    os.system('pip install --upgrade airtest')
