import argparse,os
from fgoConst import VERSION

parser=argparse.ArgumentParser(description=f'FGO-py {VERSION}')
parser.add_argument('entrypoint',help='Program entry point (default: %(default)s)',type=str.lower,choices=['gui','cli','web'],default='gui',nargs='?')
parser.add_argument('-v','--version',help='Show FGO-py version',action='version',version=VERSION)
parser.add_argument('-l','--loglevel',help='Change the console log level (default: %(default)s)',type=str.upper,choices=['DEBUG','INFO','WARNING','CRITICAL','ERROR'],default='INFO')
parser.add_argument('-c','--config',help='Config file path (default: %(default)s)',type=str,default='fgoConfig.json')
parser.add_argument('--no-color',help='Disable colored console output',action='store_true')
arg=parser.parse_args()

if arg.no_color:os.environ['NO_COLOR']='1'

if arg.entrypoint=='gui':from fgoGui import main
elif arg.entrypoint=='cli':from fgoCli import main
elif arg.entrypoint=='web':from fgoWebServer import main

import fgoLogging
fgoLogging.logger.handlers[-1].setLevel(arg.loglevel)

from fgoConfig import Config
config=Config(arg.config)
if not config.runOnce:config.runOnce=VERSION
elif config.runOnce!=VERSION:
    from fgoRunOnce import runOnce
    if runOnce(config):
        config.runOnce=VERSION
        config.save()
        exit()
    config.runOnce=VERSION

if not config.farming:
    from fgoKernel import farming
    farming.stop=True

try:main(config)
except Exception as e:fgoLogging.logger.exception(e)
finally:config.save()
