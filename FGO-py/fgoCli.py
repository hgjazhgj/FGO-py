import argparse,cmd,json,os,platform,re,signal,time
import fgoDevice
import fgoKernel
from functools import reduce,wraps
from fgoLogging import getLogger,color
from fgoTeamupParser import IniParser
logger=getLogger('Cli')

prompt='FGO-py@{Device}({Team})> 'if os.getenv('NO_COLOR')else'FGO-py\033[32m@{Device}\033[36m({Team})\033[0m> '
def wrapTry(func):
    @wraps(func)
    def wrapper(self,*args,**kwargs):
        try:return func(self,*args,**kwargs)
        except ArgError as e:
            if e.args[0]is not None:logger.error(e)
        except KeyboardInterrupt:logger.critical('KeyboardInterrupt')
        except BaseException as e:logger.exception(e)
        finally:self.prompt=prompt.format(Device=fgoDevice.device.name,Team=fgoKernel.Main.teamIndex)
    return wrapper
def countdown(x):
    timer=time.time()+x
    while(rest:=timer-time.time())>0:
        print((lambda sec:f'{sec//3600:02}:{sec%3600//60:02}:{sec%60:02}')(round(rest)),end=' \r')
        time.sleep(min(1,rest))
    print('        ',end=' \r')

class Cmd(cmd.Cmd,metaclass=lambda name,bases,attrs:type(name,bases,{i:wrapTry(j)if i.startswith('do_')else j for i,j in attrs.items()})):
    intro=f'''
FGO-py {fgoKernel.__version__}, Copyright (c) 2019-2022 hgjazhgj

Connect device first, then type main to empty your AP gauge.
Type help or ? to list commands, help <command> to get more information.
Some commands support <command> [<subcommand> ...] {{-h, --help}} for further information.
'''
    prompt=prompt.format(Device='Device',Team='Team')
    def __init__(self,config):
        super().__init__()
        fgoDevice.Device.enumDevices()
        self.teamup=IniParser('fgoTeamup.ini')
        self.teamup_load(argparse.Namespace(name='DEFAULT'))
        self.config=config
        fgoKernel.schedule.stopOnDefeated(self.config.stopOnDefeated)
        fgoKernel.schedule.stopOnKizunaReisou(self.config.stopOnKizunaReisou)
        fgoKernel.Main.teamIndex=self.config.teamIndex
    def emptyline(self):return
    def precmd(self,line):
        if line:logger.info(line)
        return line
    def completenames(self,text,*ignored):return[f'{i} 'for i in super().completenames(text,*ignored)]
    def completecommands(self,table,text,line,begidx,endidx):return sum([[f'{k} 'for k in j if k.startswith(text)]for i,j in table.items()if re.match(f'{i}$',' '.join(line.split()[1:None if begidx==endidx else -1]))],[])
    def teamup_load(self,arg):
        self.currentTeam=arg.name
        fgoKernel.ClassicTurn.skillInfo=eval(self.teamup[arg.name]['skillInfo'])
        fgoKernel.ClassicTurn.houguInfo=eval(self.teamup[arg.name]['houguInfo'])
        fgoKernel.ClassicTurn.masterSkill=eval(self.teamup[arg.name]['masterSkill'])
        if arg.name!='DEFAULT':self.teamup_show(0)
    def teamup_save(self,arg):
        if self.currentTeam=='DEFAULT':return
        self.teamup[self.currentTeam]={
            'skillInfo':str(fgoKernel.ClassicTurn.skillInfo).replace(' ',''),
            'houguInfo':str(fgoKernel.ClassicTurn.houguInfo).replace(' ',''),
            'masterSkill':str(fgoKernel.ClassicTurn.masterSkill).replace(' ','')}
        with open('fgoTeamup.ini','w')as f:self.teamup.write(f)
    def teamup_clear(self,arg):
        store=self.currentTeam
        self.teamup_load(argparse.Namespace(name='DEFAULT'))
        self.currentTeam=store
    def teamup_reload(self,arg):self.teamup=IniParser('teamup.ini')
    def teamup_list(self,arg):print('\n'.join(self.teamup.sections()))
    def teamup_show(self,arg):print('\n'.join([f'team name: {self.currentTeam}',f'team index: {fgoKernel.Main.teamIndex}','servant skill & hougu:','\n'.join(['  '.join([str(i+1),'-'.join([''.join([hex(x)[2:]for x in fgoKernel.ClassicTurn.skillInfo[i][j]])for j in range(3)]+[''.join([hex(x)[2:]for x in fgoKernel.ClassicTurn.houguInfo[i]])])])for i in range(6)]),'master skill:','   '+'-'.join([''.join([hex(x)[2:]for x in fgoKernel.ClassicTurn.masterSkill[i]])for i in range(3)])]))
    def teamup_set(self,arg):getattr(self,f'teamup_set_{arg.subcommand_1}')(arg)
    def teamup_set_servant(self,arg):
        if self.currentTeam=='DEFAULT':return
        pos=arg.pos-1
        fgoKernel.ClassicTurn.skillInfo[pos],fgoKernel.ClassicTurn.houguInfo[pos]=(lambda r:(lambda p:([[[fgoKernel.ClassicTurn.skillInfo[pos][i][j]if p[i*4+j]=='X'else int(p[i*4+j],16)for j in range(4)]for i in range(3)],[fgoKernel.ClassicTurn.houguInfo[pos][i]if p[i+12]=='X'else int(p[i+12],16)for i in range(2)]]))(r.group())if r else[fgoKernel.ClassicTurn.skillInfo[pos],fgoKernel.ClassicTurn.houguInfo[pos]])(re.match('([0-9X]{3}[0-9A-FX]){3}[0-9X][0-9A-FX]$',arg.value.replace('-','')))
        print('Change skill & hougu info of servant',arg.pos,'to','-'.join([''.join([str(x)for x in fgoKernel.ClassicTurn.skillInfo[pos][i]])for i in range(3)]+[''.join([str(x)for x in fgoKernel.ClassicTurn.houguInfo[pos]])]))
    def teamup_set_master(self,arg):
        if self.currentTeam=='DEFAULT':return
        fgoKernel.ClassicTurn.masterSkill=(lambda r:(lambda p:[[int(p[i*4+j],16)for j in range(4+(i==2))]for i in range(3)])(r.group())if r else fgoKernel.ClassicTurn.masterSkill)(re.match('([0-9X]{3}[0-9A-FX]){2}[0-9X]{4}[0-9A-FX]$',arg.value.replace('-','')))
        print('Change master skill info to','-'.join([''.join([str(x)for x in fgoKernel.ClassicTurn.masterSkill[i]])for i in range(3)]))
    def teamup_set_index(self,arg):
        self.config.teamIndex=fgoKernel.Main.teamIndex=arg.value
        print('Change team index to',arg.value)
    def do_exec(self,line):exec(line)
    def do_shell(self,line):os.system(line)
    def do_exit(self,line):
        'Exit FGO-py'
        return True
    def do_EOF(self,line):return self.do_exit(line)
    def do_version(self,line):
        'Show FGO-py version'
        print(fgoKernel.__version__)
    def do_connect(self,line):
        'Connect to a device'
        arg=parser_connect.parse_args(line.split())
        if arg.list:return print(f'last connect: {self.config.device if self.config.device else None}',*fgoDevice.Device.enumDevices(),sep='\n')
        self.config.device=arg.name if arg.name else self.config.device
        fgoDevice.device=fgoDevice.Device(self.config.device,self.config.package)
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
            '':['load','save','clear','reload','list','show','set'],
            'load':self.teamup.sections(),
            'set':['servant','master','index']
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
        self.work=fgoKernel.Main(arg.appleCount,['gold','silver','bronze','quartz'].index(arg.appleKind))
        self.do_continue(f'-s {arg.sleep}')
    def complete_main(self,text,line,begidx,endidx):
        return self.completecommands({
            r'\d+':['gold','silver','bronze','quartz']
        },text,line,begidx,endidx)
    def do_classic(self,line):
        'Use classic battle'
        arg=parser_main.parse_args(line.split())
        fgoKernel.schedule.stopLater(arg.appoint)
        self.work=fgoKernel.Main(arg.appleCount,['gold','silver','bronze','quartz'].index(arg.appleKind),lambda:fgoKernel.Battle(fgoKernel.ClassicTurn))
        self.do_continue(f'-s {arg.sleep}')
    def complete_old(self,text,line,begidx,endidx):return self.complete_main(text,line,begidx,endidx)
    def do_continue(self,line):
        'Continue last battle after abnormal break, use it as same as battle'
        arg=parser_battle.parse_args(line.split())
        assert fgoDevice.device.available
        assert not fgoKernel.lock.locked()
        countdown(reduce(lambda x,y:x*60+int(y),arg.sleep.split(':'),0))
        try:
            signal.signal(signal.SIGINT,lambda*_:fgoKernel.schedule.stop())
            if platform.system()=='Windows':signal.signal(signal.SIGBREAK,lambda*_:fgoKernel.schedule.pause())
            self.work()
        except fgoKernel.ScriptStop as e:
            logger.critical(e)
            msg=str(e)
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
        # if self.config.notifyEnable:
        #     for i in self.config.notifyParam:
        #         if not notify(**i,title='FGO-py',content=msg):logger.warning(f'Notify {i} failed')
    def do_call(self,line):
        'Call a Additional feature'
        arg=parser_call.parse_args(line.split())
        self.work=getattr(fgoKernel,arg.func)
        self.do_continue(f'-s {arg.sleep}')
    def complete_call(self,text,line,begidx,endidx):
        return self.completecommands({
            '':['gacha','lottery','mail','synthesis','gachaHistory']
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
        arg=parser_screenshot.parse_args(line.split())
        assert fgoDevice.device.available
        fgoKernel.Detect(0).save(arg.file,appendTime=arg.notime)
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
        arg=parser_bench.parse_args(line.split())
        assert fgoDevice.device.available
        if not(arg.input or arg.output):arg.input=arg.output=True
        fgoKernel.bench(max(3,arg.number),arg.input,arg.output)
    def do_lock(self,line):
        'Lock FGO-py to temporary disable all functions without exiting or disconnecting'
        arg=parser_lock.parse_args(line.split())
        assert arg.unlock or not fgoKernel.lock.locked()
        if arg.unlock:fgoKernel.lock.release()
        else:fgoKernel.lock.acquire()

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
parser_battle.add_argument('-s','--sleep',help='Sleep before run (default: %(default)s)',type=validator(str,lambda x:re.match(r'\d+(:\d+)*$',x),'timedelta'),default='0')

parser_main=ArgParser(prog='main',description=Cmd.do_main.__doc__)
parser_main.add_argument('appleCount',help='Apple Count (default: %(default)s)',type=validator(int,lambda x:x>=0,'nonnegative int'),default=0,nargs='?')
parser_main.add_argument('appleKind',help='Apple Kind (default: %(default)s)',type=str.lower,choices=['gold','silver','bronze','quartz'],default='gold',nargs='?')
parser_main.add_argument('-s','--sleep',help='Sleep before run (default: %(default)s)',type=validator(str,lambda x:re.match(r'\d+(:\d+)*$',x),'timedelta'),default='0')
parser_main.add_argument('-a','--appoint',help='Battle count limit (default: %(default)s for no limit)',type=validator(int,lambda x:x>=0,'nonnegative int'),default=0)

parser_connect=ArgParser(prog='connect',description=Cmd.do_connect.__doc__)
parser_connect.add_argument('-l','--list',help='List all available devices',action='store_true')
parser_connect.add_argument('name',help='Device name (default to the last connected one)',default='',nargs='?')

parser_teamup=ArgParser(prog='teamup',description=Cmd.do_teamup.__doc__)
parser_teamup_=parser_teamup.add_subparsers(title='subcommands',required=True,dest='subcommand_0')
parser_teamup_load=parser_teamup_.add_parser('load',help='Load a team to current')
parser_teamup_load.add_argument('name',help='Teamup Name (default: %(default)s)',default='DEFAULT',nargs='?')
parser_teamup_save=parser_teamup_.add_parser('save',help='Save all teams')
parser_teamup_clear=parser_teamup_.add_parser('clear',help='Reset current team to DEFAULT')
parser_teamup_reload=parser_teamup_.add_parser('reload',help='Reload fgoTeamup.ini')
parser_teamup_list=parser_teamup_.add_parser('list',help='List all teams')
parser_teamup_show=parser_teamup_.add_parser('show',help='Show current team info')
parser_teamup_set=parser_teamup_.add_parser('set',help='Setup a field of current team')
parser_teamup_set_=parser_teamup_set.add_subparsers(title='subcommands',required=True,dest='subcommand_1')
parser_teamup_set_servant=parser_teamup_set_.add_parser('servant',help='Setup servant skill & hougu info')
parser_teamup_set_servant.add_argument('pos',help='Servant # (1-6)',type=int,choices=range(1,7))
parser_teamup_set_servant.add_argument('value',help='Info value (e.g. 1007-xxxx-1007-2x, add hyphens(-) anywhere as they will be removed, x for no change)',type=str.upper)
parser_teamup_set_master=parser_teamup_set_.add_parser('master',help='Setup master skill info')
parser_teamup_set_master.add_argument('value',help='Info value (e.g. 1107-xxxx-21347, add hyphens(-) anywhere as they will be removed, x for no change)',type=str.upper)
parser_teamup_set_index=parser_teamup_set_.add_parser('index',help='Setup team index')
parser_teamup_set_index.add_argument('value',help='Team index (0-10)',type=int,choices=range(0,11))

parser_call=ArgParser(prog='call',description=Cmd.do_call.__doc__)
parser_call.add_argument('func',help='Additional feature name',choices=['gacha','lottery','mail','synthesis','gachaHistory'])
parser_call.add_argument('-s','--sleep',help='Sleep before run (default: %(default)s)',type=validator(str,lambda x:re.match(r'\d+(:\d+)*$',x),'timedelta'),default='0')

parser_169=ArgParser(prog='169',description=Cmd.do_169.__doc__)
parser_169.add_argument('action',help='Action',type=str.lower,choices=['invoke','revoke'])

parser_press=ArgParser(prog='press',description=Cmd.do_press.__doc__)
parser_press.add_argument('button',help='Button',type=str.upper)
parser_press.add_argument('-c','--code',help='Use virtual key code',action='store_true')

parser_bench=ArgParser(prog='bench',description=Cmd.do_bench.__doc__)
parser_bench.add_argument('-n','--number',help='Number of runs (default: %(default)s)',type=validator(int,lambda x:x>=3,'not-less-than-3 int'),default=20)
parser_bench.add_argument('-i','--input',help='Bench touch, if neither -i nor -o specified, bench them both',action='store_true')
parser_bench.add_argument('-o','--output',help='Bench screenshot, if neither -i nor -o specified, bench them both',action='store_true')

parser_lock=ArgParser(prog='lock',description=Cmd.do_lock.__doc__)
parser_lock.add_argument('-u','--unlock',help='Unlock (lock if not specified)',action='store_true')

parser_screenshot=ArgParser(prog='screenshot',description=Cmd.do_screenshot.__doc__)
parser_screenshot.add_argument('file',help='Filename/path prefix (default: %(default)s)',default='Screenshot',nargs='?')
parser_screenshot.add_argument('-t','--notime',help='Do not append Time after filename',action='store_false')

def main(config):Cmd(config).cmdloop()
