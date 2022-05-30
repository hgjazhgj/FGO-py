# fgoAlas* 系列文件是为在 AzurLaneAutoScript 中运行提供的组件
# 显然本项目不符合 alas 的代码标准,所以仅在此处提供这一解决方案

# mkdir module/FGOpy

# 复制以下文件和目录到前述目录
# fgoImage
# fgoAlas.py
# fgoAlasDevice.py
# fgoConst.py
# fgoDetect.py
# fgoFuse.py
# fgoImageListener.py
# fgoIniParser.py
# fgoKernel.py
# fgoLogging.py
# fgoSchedule.py
# fgoTeamup.ini

# 将 fgoLogging.py 的内容替换为
# import logging
# from module.logger import logger
# from functools import wraps
# from module.FGOpy.fgoConst import VERSION
# def getLogger(name):return logger
# def logit(logger,level=logging.DEBUG):return lambda func:wraps(func)(lambda*args,**kwargs:(lambda x:(logger.log(level,' '.join((func.__name__,str(x)[:100].split('\n',1)[0]))),x)[-1]if x is not None else x)(func(*args,**kwargs)))
# def logMeta(logger):return lambda name,bases,attrs:type(name,bases,{i:logit(logger)(j)if callable(j)and i[0]!='_'else j for i,j in attrs.items()})
# logger.hr(f'FGO-py {VERSION}')
# 即使用 alas 的 logger

# 修改其他除 fgoAlas.py 和 fgoAlasDevice.py 以外所有 .py 文件中的 import path
# 比如 from fgoDetect import Detect 就要改为 from module.FGOpy.fgoDetect import Detect

# 搜索所有「海象牙运算符(:=)」,将其改写为等效的 python 3.7 写法
# 例如 [t:=Detect(.2).getStage(),1+self.stageTurn*(self.stage==t)] 可以改成 (lambda t:[t,1+self.stageTurn*(self.stage==t)])(Detect(.2).getStage())
# 大约要修改 8 处

# 在 module/config/argument/task.yaml 末尾添加一些内容,加完后看起来是这样
# 249  AzurLaneUncensored:
# 250     - AzurLaneUncensored
# 251 + FGOpy:
# 252 +   - FGOpy
# 253   GameManager:
# 254     - GameManager

# 在 module/config/argument/argument.yaml 末尾添加一些内容,加完后看起来是这样
# 524   AzurLaneUncensored:
# 525     Repository: https://gitee.com/LmeSzinc/AzurLaneUncensored
# 526 + FGOpy:
# 527 +   TeamName: DEFAULT
# 528   GameManager:
# 529     AutoRestart: true

# 运行 module/config/config_updater.py
# 你可能需要 sys.path.append(os.path.abspath('../..'))

# 在 module/webui/process_manager.py 中间添加一些内容,加完后看起来是这样
# 147   elif func == "GameManager":
# 148       from module.daemon.game_manager import GameManager
# 149
# 150       GameManager(config=config_name, task="GameManager").run()
# 151 + elif func == "FGOpy":
# 152 +     from module.FGOpy.fgoAlas import fgoAlas
# 153 +
# 154 +     fgoAlas(config=config_name).run()
# 155   else:
# 156       logger.critical("No function matched")

# 现在,你可以在 alas 中使用 FGO-py

from module.config.config import AzurLaneConfig
from module.logger import logger
from module.FGOpy import fgoKernel
from module.FGOpy.fgoAlasDevice import Device
from module.FGOpy.fgoIniParser import IniParser

teamup = IniParser("module/FGOpy/fgoTeamup.ini")


class fgoAlas:
    def __init__(self, config):
        self.config = AzurLaneConfig(config, task='FGOpy')
        fgoKernel.device = Device(config=self.config)

    def run(self):
    #   logger.setLevel('DEBUG')
        teamName = self.config.FGOpy_TeamName
        logger.info(f'{teamName}')
        if teamName not in teamup:
            logger.critical("Team not found")
            return
        fgoKernel.Main.teamIndex = eval(teamup[teamName]['teamIndex'])
        fgoKernel.Turn.skillInfo = eval(teamup[teamName]['skillInfo'])
        fgoKernel.Turn.houguInfo = eval(teamup[teamName]['houguInfo'])
        fgoKernel.Turn.masterSkill = eval(teamup[teamName]['masterSkill'])
        fgoKernel.Main()()
    #   logger.setLevel("INFO")


def main():
    fgoAlas(config='FGOpy').run()
