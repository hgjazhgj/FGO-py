from fgoLogging import getLogger
logger=getLogger('RunOnce')

RUNONCE=[]
def regRunOnce(func):
    RUNONCE.append(([int(i)for i in func.__name__.removeprefix('v').split('_')],func))
    return func

def runOnce(config):
    restart=False
    src=[int(i)for i in config.runOnce.removeprefix('v').split('.')]
    for dst,func in RUNONCE:
        if src<dst:
            logger.info(f'Upgrading to v{".".join(str(i)for i in dst)}')
            if func(config):break
            restart=True
    if restart:
        logger.debug('Please restart FGO-py manually to complete the upgrade.')
        logger.info('Please restart FGO-py manually to complete the upgrade.')
        logger.warning('Please restart FGO-py manually to complete the upgrade.')
        logger.critical('Please restart FGO-py manually to complete the upgrade.')
        logger.error('Please restart FGO-py manually to complete the upgrade.')
    return restart

@regRunOnce
def v9_8_0(config):
    import os
    os.system('pip install --upgrade airtest')
@regRunOnce
def v10_1_3(config):
    config.farming=False
    print('邪马台国7*24自动收菜功能已被禁用。')
