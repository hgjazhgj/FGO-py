import argparse
from fgoConst import version

parser=argparse.ArgumentParser(description=f'FGO-py {version}')
parser.add_argument('entrypoint',help='Program entry point',choices=['qt','cli','web'],type=str.lower,default='qt',nargs='?')
parser.add_argument('-v','--version',help='Show FGO-py version',action='version',version=version)
parser.add_argument('-l','--loglevel',help='Change the console log level',choices=['DEBUG','INFO','WARNING','CRITICAL','ERROR'],type=str.upper,default='INFO')
arg=parser.parse_args()

if arg.entrypoint=='qt':from fgoGui import main
elif arg.entrypoint=='cli':from fgoCmd import main
elif arg.entrypoint=='web':raise NotImplementedError

import fgoLogging
fgoLogging.logging.getLogger('fgo').handlers[-1].setLevel(arg.loglevel)

main()
