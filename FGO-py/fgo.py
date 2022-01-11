import argparse
from fgoConst import version

parser=argparse.ArgumentParser(description=f'FGO-py {version}')
parser.add_argument('entrypoint',help='Program entry point (default: %(default)s)',type=str.lower,choices=['qt','cli','web'],default='qt',nargs='?')
parser.add_argument('-v','--version',help='Show FGO-py version',action='version',version=version)
parser.add_argument('-l','--loglevel',help='Change the console log level (default: %(default)s)',type=str.upper,choices=['DEBUG','INFO','WARNING','CRITICAL','ERROR'],default='INFO')
arg=parser.parse_args()

if arg.entrypoint=='qt':from fgoGui import main
elif arg.entrypoint=='cli':from fgoCli import main
elif arg.entrypoint=='web':raise NotImplementedError

import fgoLogging
fgoLogging.logging.getLogger('fgo').handlers[-1].setLevel(arg.loglevel)

main()
