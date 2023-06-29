from fgoLogging import getLogger
logger=getLogger('RunOnce')

RUNONCE=[]
def regRunOnce(func):
    RUNONCE.append(([int(i)for i in func.__name__.removeprefix('v').split('_')],func))
    return func

def runOnce(config):
    src=[int(i)for i in config.runOnce.removeprefix('v').split('.')]
    for dst,func in RUNONCE:
        if src<dst:
            logger.info(f'Upgrading to v{".".join(str(i)for i in dst)}')
            if func(config):break
    else:return False
    logger.debug('Please restart FGO-py manually to complete the upgrade.')
    logger.info('Please restart FGO-py manually to complete the upgrade.')
    logger.warning('Please restart FGO-py manually to complete the upgrade.')
    logger.critical('Please restart FGO-py manually to complete the upgrade.')
    logger.error('Please restart FGO-py manually to complete the upgrade.')
    return True

