import argparse,cmd,functools,json,os,platform,re,signal,time
import fgoDevice
import fgoKernel
from fgoLogging import getLogger,color
logger=getLogger('Cli')

def wrapTry(func):
    @functools.wraps(func)
    def wrapper(self,*args,**kwargs):
        try:return func(self,*args,**kwargs)
        except ArgError as e:
            if e.args[0]is not None:logger.error(e)
        except KeyboardInterrupt:logger.critical('KeyboardInterrupt')
        except BaseException as e:logger.exception(e)
        finally:self.prompt=f'FGO-py@{fgoDevice.device.name}> '
    return wrapper
def countdown(x):
    timer=time.time()+x
    while(rest:=timer-time.time())>0:
        print((lambda sec:f'{sec//3600:02}:{sec%3600//60:02}:{sec%60:02}')(round(rest)),end=' \r')
        time.sleep(min(1,max(0,rest)))

class Cmd(cmd.Cmd,metaclass=lambda name,bases,attrs:type(name,bases,{i:wrapTry(j)if i.startswith('do_')else j for i,j in attrs.items()})):
    intro=f'''
FGO-py {fgoKernel.__version__}, Copyright (c) 2019-2022 hgjazhgj

Connect device first, then type main to empty your AP gauge.
Type help or ? to list commands, help <command> to get more information.
Some commands support <command> [<subcommand> ...] {{-h, --help}} for further information.
'''
    prompt='FGO-py@Device> '
    def __init__(self):
        super().__init__()
        fgoDevice.Device.enumDevices()
        with open('fgoConfig.json')as f:self.config=json.load(f)
        fgoKernel.schedule.stopOnDefeated(self.config['stopOnDefeated'])
        fgoKernel.schedule.stopOnKizunaReisou(self.config['stopOnKizunaReisou'])
        fgoKernel.Main.teamIndex=self.config['teamIndex']
    def emptyline(self):return
    def precmd(self,line):
        if line:logger.info(line)
        return line
    def completenames(self,text,*ignored):return[f'{i} 'for i in super().completenames(text,*ignored)]
    def completecommands(self,table,text,line,begidx,endidx):return sum([[f'{k} 'for k in j if k.startswith(text)]for i,j in table.items()if re.match(f'{i}$',' '.join(line.split()[1:None if begidx==endidx else -1]))],[])
    def teamup_show(self,arg):print(f'team index: {fgoKernel.Main.teamIndex}')
    def teamup_set(self,arg):getattr(self,f'teamup_set_{arg.subcommand_1}')(arg)
    def teamup_set_index(self,arg):
        self.config['teamIndex']=fgoKernel.Main.teamIndex=arg.value
        print('Change team index to',arg.value)
    def do_exec(self,line):exec(line)
    def do_shell(self,line):os.system(line)
    def do_exit(self,line):
        'Exit FGO-py'
        with open('fgoConfig.json','w')as f:json.dump(self.config,f,indent=4)
        return True
    def do_EOF(self,line):return self.do_exit(line)
    def do_version(self,line):
        'Show FGO-py version'
        print(fgoKernel.__version__)
    def do_connect(self,line):
        'Connect to a device'
        arg=parser_connect.parse_args(line.split())
        if arg.list:return print(f'last connect: {self.config["device"]if self.config["device"]else None}',*fgoDevice.Device.enumDevices(),sep='\n')
        self.config['device']=arg.name if arg.name else self.config['device']
        fgoDevice.device=fgoDevice.Device(self.config['device'],self.config['package'])
    def complete_connect(self,text,line,begidx,endidx):
        return self.completecommands({
            '':['wsa','win']+[f'/{i}'for i in fgoDevice.helpers]+fgoDevice.Device.enumDevices()
        },text,line,begidx,endidx)
    def do_teamup(self,line):
        'Setup your teams'
        arg=parser_teamup.parse_args(line.split())
        getattr(self,f'teamup_{arg.subcommand_0}')(arg)
    def complete_teamup(self,text,line,begidx,endidx):
        return self.completecommands({
            '':['show','set'],
            'set':['index']
        },text,line,begidx,endidx)
    def do_battle(self,line):
        'Finish the current battle'
        arg=parser_battle.parse_args(line.split())
        self.work=fgoKernel.Battle()
        self.do_continue(f'-s {arg.sleep}')
    def do_main(self,line):
        'Loop for battle until AP empty'
        arg=parser_main.parse_args(line.split())
        fgoKernel.schedule.stopLater(arg.appoint)
        self.work=fgoKernel.Main(arg.appleCount,['gold','silver','bronze','quartz'].index(arg.appleKind),{'Battle':fgoKernel.Battle}[arg.battleClass])
        self.do_continue(f'-s {arg.sleep}')
    def complete_main(self,text,line,begidx,endidx):
        return self.completecommands({
            r'\d+':['gold','silver','bronze','quartz'],
            r'\d+ (gold|silver|bronze|quartz)':['Battle']
        },text,line,begidx,endidx)
    def do_continue(self,line):
        'Continue last battle after abnormal break, use it as same as battle'
        arg=parser_battle.parse_args(line.split())
        assert fgoDevice.device.available
        countdown(arg.sleep)
        try:
            signal.signal(signal.SIGINT,lambda*_:fgoKernel.schedule.stop())
            if platform.system()=='Windows':signal.signal(signal.SIGBREAK,lambda*_:fgoKernel.schedule.pause())
            self.work()
        except fgoKernel.ScriptStop as e:
            logger.critical(e)
            msg=str(e)
        except KeyboardInterrupt:raise
        except BaseException as e:
            logger.exception(e)
            msg=repr(e)
        else:msg='Done'
        finally:
            result=getattr(self.work,'result',None)
            signal.signal(signal.SIGINT,signal.SIG_DFL)
            if platform.system()=='Windows':signal.signal(signal.SIGBREAK,signal.SIG_DFL)
            fgoKernel.fuse.reset()
            fgoKernel.schedule.reset()
        if isinstance(result,dict)and(t:=result.get('type',None)):
            if t=='Battle':...
            elif t=='Main':
                logger.warning(f'{color(0xC5E0B4)}{result["battle"]}{color()} battle(s) finished in {color(0xC5E0B4)}{result["time"]//3600:.0f}:{result["time"]//60%60:02.0f}:{result["time"]%60:02.0f}{color()}')
                logger.warning(f'{color(0xC5E0B4)}{result["turnPerBattle"]:.1f}{color()} turns, {color(0xC5E0B4)}{result["timePerBattle"]//60:.0f}:{result["timePerBattle"]%60:02.1f}{color()} per battle in average')
                if result["material"]:logger.warning(f'{", ".join(f"{i}{color(0xFFD966)}x{j}{color()}"for i,j in result["material"].items())} earned')
        # todo: notify
        # if self.config['notifyEnable']:
        #     for i in self.config['notifyParam']:
        #         if not notify(**i,title='FGO-py',content=msg):logger.warning(f'Notify {self.config["notifyParam"]["provider"]} failed')
    def do_call(self,line):
        'Call a Additional feature'
        arg=parser_call.parse_args(line.split())
        self.work=getattr(fgoKernel,arg.func)
        self.do_continue(f'-s {arg.sleep}')
    def complete_call(self,text,line,begidx,endidx):
        return self.completecommands({
            '':['gacha','lottery','mail','synthesis']
        },text,line,begidx,endidx)
    def do_config(self,line):
        'Edit config item if exists and forward to schedule'
        key,value=line.split()
        value=eval(value)
        if hasattr(fgoKernel.schedule,key):getattr(fgoKernel.schedule,key)(value)
        if key in self.config:self.config[key]=value
    def complete_config(self,text,line,begidx,endidx):
        return self.completecommands({
            '':['notifyEnable','stopLater','stopOnDefeated','stopOnKizunaReisou','stopOnSpecialDrop']
        },text,line,begidx,endidx)
    def do_screenshot(self,line):
        'Take a screenshot'
        assert fgoDevice.device.available
        fgoKernel.Detect(0).save()
    def do_169(self,line):
        'Adapt none 16:9 screen'
        arg=parser_169.parse_args(line.split())
        assert fgoDevice.device.available
        getattr(fgoDevice.device,f'{arg.action}169')()
    def complete_169(self,text,line,begidx,endidx):
        return self.completecommands({
            '':['invoke','revoke']
        },text,line,begidx,endidx)
    def do_press(self,line):
        'Map key press'
        arg=parser_press.parse_args(line.split())
        fgoDevice.device.press(chr(eval(arg.button))if arg.code else arg.button)
    def do_bench(self,line):
        'Benchmark'
        assert fgoDevice.device.available
        arg=parser_bench.parse_args(line.split())
        if not(arg.input or arg.output):arg.input=arg.output=True
        fgoKernel.bench(max(3,arg.number),arg.input,arg.output)

ArgError=type('ArgError',(Exception,),{})
def validator(type,func,desc='\b'):
    def f(x):
        if not func(x:=type(x)):raise ValueError
        return x
    f.__name__=desc
    return f
class ArgParser(argparse.ArgumentParser):
    def exit(self,status=0,message=None):raise ArgError(message)

parser_battle=ArgParser(prog='battle',description=Cmd.do_battle.__doc__)
parser_battle.add_argument('-s','--sleep',help='Sleep before run (default: %(default)s)',type=validator(float,lambda x:x>=0,'nonnegative'),default=0)

parser_main=ArgParser(prog='main',description=Cmd.do_main.__doc__)
parser_main.add_argument('appleCount',help='Apple Count (default: %(default)s)',type=validator(int,lambda x:x>=0,'nonnegative int'),default=0,nargs='?')
parser_main.add_argument('appleKind',help='Apple Kind (default: %(default)s)',type=str.lower,choices=['gold','silver','bronze','quartz'],default='gold',nargs='?')
parser_main.add_argument('battleClass',help='Battle Class (default: %(default)s)',choices=['Battle'],default='Battle',nargs='?')
parser_main.add_argument('-s','--sleep',help='Sleep before run (default: %(default)s)',type=validator(float,lambda x:x>=0,'nonnegative'),default=0)
parser_main.add_argument('-a','--appoint',help='Battle count limit (default: %(default)s for no limit)',type=validator(int,lambda x:x>=0,'nonnegative int'),default=0)

parser_connect=ArgParser(prog='connect',description=Cmd.do_connect.__doc__)
parser_connect.add_argument('-l','--list',help='List all available devices',action='store_true')
parser_connect.add_argument('name',help='Device name (default to the last connected one)',default='',nargs='?')

parser_teamup=ArgParser(prog='teamup',description=Cmd.do_teamup.__doc__)
parser_teamup_=parser_teamup.add_subparsers(title='subcommands',required=True,dest='subcommand_0')
parser_teamup_show=parser_teamup_.add_parser('show',help='Show current team info')
parser_teamup_set=parser_teamup_.add_parser('set',help='Setup a filed in current team')
parser_teamup_set_=parser_teamup_set.add_subparsers(title='subcommands',required=True,dest='subcommand_1')
parser_teamup_set_index=parser_teamup_set_.add_parser('index',help='Setup team index')
parser_teamup_set_index.add_argument('value',help='Team index (0-10)',type=int,choices=range(0,11))

parser_call=ArgParser(prog='call',description=Cmd.do_call.__doc__)
parser_call.add_argument('func',help='Additional feature name',choices=['gacha','lottery','mail','synthesis'])
parser_call.add_argument('-s','--sleep',help='Sleep several seconds before run (default: %(default)s)',type=validator(float,lambda x:x>=0,'nonnegative'),default=0)

parser_169=ArgParser(prog='169',description=Cmd.do_169.__doc__)
parser_169.add_argument('action',help='Action',type=str.lower,choices=['invoke','revoke'])

parser_press=ArgParser(prog='press',description=Cmd.do_press.__doc__)
parser_press.add_argument('button',help='Button',type=str.upper)
parser_press.add_argument('-c','--code',help='Use virtual key code',action='store_true')

parser_bench=ArgParser(prog='bench',description=Cmd.do_bench.__doc__)
parser_bench.add_argument('-n','--number',help='Number of runs (default: %(default)s)',type=validator(int,lambda x:x>=3,'not-less-than-3 int'),default=20)
parser_bench.add_argument('-i','--input',help='Bench touch, if neither -i nor -o specified, bench them both',action='store_true')
parser_bench.add_argument('-o','--output',help='Bench screenshot, if neither -i nor -o specified, bench them both',action='store_true')

def main(args):Cmd().cmdloop()
