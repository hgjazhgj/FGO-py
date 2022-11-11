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
def v10_1_0(config):
    print('可提供邪马台国7*24自动收菜,会在空闲时主动运行,是否启用?(Y/n)')
    choose=input().lower()
    if not choose or choose=='y':
        config.farming=True
    print('你可以稍后在fgoConfig.json中farming字段对此设置进行更改。')
