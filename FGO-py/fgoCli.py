import argparse,cmd,functools,json,os,re,time
import fgoCore
from fgoIniParser import IniParser

logger=fgoCore.getLogger('Cli')

def wrapTry(func):
    @functools.wraps(func)
    def wrapper(self,*args,**kwargs):
        try:return func(self,*args,**kwargs)
        except ArgError as e:
            if e.args[0]is not None:logger.error(e)
        except Exception as e:logger.exception(e)
        except KeyboardInterrupt:pass
        finally:self.prompt='FGO-py\033[32m@{}\033[36m({})\033[0m> '.format(fgoCore.device.name,self.currentTeam)
    return wrapper

class Cmd(cmd.Cmd,metaclass=lambda name,bases,attrs:type(name,bases,{i:wrapTry(j)if i.startswith('do_')else j for i,j in attrs.items()})):
    intro=f'''
FGO-py {fgoCore.version}, Copyright (c) 2019-2022 by hgjazhgj

Connect device and load teamup first, then type main to empty your AP gauge.
Type help or ? to list commands, help <command> to get more information.
Some commands support <command> [<subcommand> ...] {{-h, --help}} for further information.
'''
    prompt='FGO-py\033[32m@Device\033[36m(Team)\033[0m> '
    def __init__(self):
        super().__init__()
        self.teamup=IniParser('fgoTeamup.ini')
        self.teamup_load(argparse.Namespace(name='DEFAULT'))
        with open('fgoConfig.json','r')as f:self.config=json.load(f)
        fgoCore.control.stopOnDefeated(self.config['stopOnDefeated'])
        fgoCore.control.stopOnKizunaReisou(self.config['stopOnKizunaReisou'])
    def emptyline(self):return
    def precmd(self,line):
        if line:logger.info(line)
        return line
    def teamup_load(self,arg):
        self.currentTeam=arg.name
        fgoCore.Main.teamIndex=int(self.teamup[arg.name]['teamIndex'])
        fgoCore.Battle.skillInfo=eval(self.teamup[arg.name]['skillInfo'])
        fgoCore.Battle.houguInfo=eval(self.teamup[arg.name]['houguInfo'])
        fgoCore.Battle.masterSkill=eval(self.teamup[arg.name]['masterSkill'])
        if arg.name!='DEFAULT':self.teamup_show(0)
    def teamup_save(self,arg):
        if self.currentTeam=='DEFAULT':return
        self.teamup[self.currentTeam]={
            'teamIndex':fgoCore.Main.teamIndex,
            'skillInfo':str(fgoCore.Battle.skillInfo).replace(' ',''),
            'houguInfo':str(fgoCore.Battle.houguInfo).replace(' ',''),
            'masterSkill':str(fgoCore.Battle.masterSkill).replace(' ','')}
        with open('fgoTeamup.ini','w')as f:self.teamup.write(f)
    def teamup_clear(self,arg):
        store=self.currentTeam
        self.teamup_load(argparse.Namespace(name='DEFAULT'))
        self.currentTeam=store
    def teamup_reload(self,arg):self.teamup=IniParser('teamup.ini')
    def teamup_list(self,arg):print('\n'.join(self.teamup.sections()))
    def teamup_show(self,arg):print('\n'.join([f'team name: {self.currentTeam}',f'team index: {fgoCore.Main.teamIndex}','servant skill & hougu:','\n'.join(['  '.join([str(i+1),'-'.join([''.join([str(x)for x in fgoCore.Battle.skillInfo[i][j]])for j in range(3)]+[''.join([str(x)for x in fgoCore.Battle.houguInfo[i]])])])for i in range(6)]),'master skill:','   '+'-'.join([''.join([str(x)for x in fgoCore.Battle.masterSkill[i]])for i in range(3)])]))
    def teamup_set(self,arg):getattr(self,f'teamup_set_{arg.subcommand_1}')(arg)
    def teamup_set_servant(self,arg):
        if self.currentTeam=='DEFAULT':return
        pos=arg.pos-1
        fgoCore.Battle.skillInfo[pos],fgoCore.Battle.houguInfo[pos]=(lambda r:(lambda p:([[[fgoCore.Battle.skillInfo[pos][i][j]if p[i*4+j]=='X'else int(p[i*4+j],16)for j in range(4)]for i in range(3)],[fgoCore.Battle.houguInfo[pos][i]if p[i+12]=='X'else int(p[i+12],16)for i in range(2)]]))(r.group())if r else[fgoCore.Battle.skillInfo[pos],fgoCore.Battle.houguInfo[pos]])(re.match('([0-9X]{3}[0-9A-FX]){3}[0-9X][0-9A-FX]$',arg.value))
        print('Change skill & hougu info of servant',arg.pos,'to','-'.join([''.join([str(x)for x in fgoCore.Battle.skillInfo[pos][i]])for i in range(3)]+[''.join([str(x)for x in fgoCore.Battle.houguInfo[pos]])]))
    def teamup_set_master(self,arg):
        if self.currentTeam=='DEFAULT':return
        fgoCore.Battle.masterSkill=(lambda r:(lambda p:[[int(p[i*4+j])for j in range(4+(i==2))]for i in range(3)])(r.group())if r else fgoCore.Battle.masterSkill)(re.match('([0-9X]{3}[0-9A-FX]){2}[0-9X]{4}[0-9A-FX]$',arg.value))
        print('Change master skill info to','-'.join([''.join([str(x)for x in fgoCore.Battle.masterSkill[i]])for i in range(3)]))
    def teamup_set_index(self,arg):
        if self.currentTeam=='DEFAULT':return
        fgoCore.Main.teamIndex=arg.value
        print('Change team index to',fgoCore.Main.teamIndex)
    def do_test(self,line):pass
    def do_exec(self,line):exec(line)
    def do_shell(self,line):os.system(line)
    def do_exit(self,line):
        'Exit FGO-py'
        with open('fgoConfig.json','w')as f:json.dump(self.config,f,indent=4)
        return True
    def do_EOF(self,line):return self.do_exit(line)
    def do_version(self,line):
        'Show FGO-py version'
        print(fgoCore.version)
    def do_connect(self,line):
        'Connect to a device'
        arg=parser_connect.parse_args(line.split())
        if arg.list:return print('\n'.join(fgoCore.Device.enumDevices()))
        fgoCore.device=fgoCore.Device(arg.name)
    def do_teamup(self,line):
        'Setup your teams'
        arg=parser_teamup.parse_args(line.split())
        getattr(self,f'teamup_{arg.subcommand_0}')(arg)
    def complete_teamup(self,text,line,begidx,endidx):
        # todo: auto-complete teamup subcommands
        # print()
        # print(text,line,begidx,endidx)
        # print()
        return[]
    def do_battle(self,line):
        'Finish the current battle'
        arg=parser_battle.parse_args(line.split())
        self.work=fgoCore.Battle()
        time.sleep(arg.sleep)
        self.do_continue('')
    def do_main(self,line):
        'Loop for battle until AP empty'
        arg=parser_main.parse_args(line.split())
        self.work=fgoCore.Main(arg.appleCount,['gold','silver','copper','quartz'].index(arg.appleKind),{'Battle':fgoCore.Battle,'UserScript':fgoCore.UserScript}[arg.battleClass])
        time.sleep(arg.sleep)
        self.do_continue('')
    def do_continue(self,line):
        'Continue last battle after abnormal break, use it as same as battle'
        arg=parser_battle.parse_args(line.split())
        time.sleep(arg.sleep)
        assert fgoCore.device.avaliable
        try:self.work()
        except fgoCore.ScriptTerminate as e:
            logger.critical(e)
            msg=str(e)
        except BaseException as e:
            logger.exception(e)
            msg=repr(e)
        else:msg='Done'
        finally:
            fgoCore.fuse.reset()
            fgoCore.control.reset()
            # todo: notify
            # if self.config['notifyEnable']:
            #     for i in self.config['notifyParam']:
            #         if not notify(**i,title='FGO-py',content=msg):logger.warning(f'Notify {self.config["notifyParam"]["provider"]} failed')
    def do_call(self,line):
        'Call a Additional feature'
        arg=parser_call.parse_args(line.split())
        assert fgoCore.device.avaliable
        time.sleep(arg.sleep)
        getattr(fgoCore,arg.func)()
    def do_config(self,line):
        'Edit config item if exists and forward to control'
        key,value=line.split()
        value=eval(value)
        if hasattr(fgoCore.control,key):getattr(fgoCore.control,key)(value)
        if key in self.config:self.config[key]=value
    def do_screenshot(self,line):
        'Take a screenshot'
        assert fgoCore.device.avaliable
        fgoCore.Check(0,blockFuse=True).save()
    def do_169(self,line):
        'Adapt none 16:9 screen'
        arg=parser_169.parse_args(line.split())
        assert fgoCore.device.avaliable
        getattr(fgoCore.device,f'{arg.action}169')()
    def do_press(self,line):
        'Map key press'
        arg=parser_press.parse_args(line.split())
        fgoCore.device.press(chr(eval(arg.button))if arg.code else arg.button)

ArgError=type('ArgError',(Exception,),{})
class ArgParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):raise ArgError(message)

parser_battle=ArgParser(prog='battle',description=Cmd.do_battle.__doc__)
parser_battle.add_argument('-s','--sleep',help='Sleep before run (default: %(default)s)',type=float,default=0)

parser_main=ArgParser(prog='main',description=Cmd.do_main.__doc__)
parser_main.add_argument('appleCount',help='Apple Count (default: %(default)s)',type=int,default=0,nargs='?')
parser_main.add_argument('appleKind',help='Apple Kind (default: %(default)s)',type=str.lower,choices=['gold','silver','copper','quartz'],default='gold',nargs='?')
parser_main.add_argument('battleClass',help='Battle Class (default: %(default)s)',choices=['Battle','UserScript'],default='Battle',nargs='?')
parser_main.add_argument('-s','--sleep',help='Sleep before run (default: %(default)s)',type=float,default=0)

parser_connect=ArgParser(prog='connect',description=Cmd.do_connect.__doc__)
parser_connect.add_argument('-l','--list',help='List all available devicess',action='store_true')
parser_connect.add_argument('name',help='Device name',default='',nargs='?')

parser_teamup=ArgParser(prog='teamup',description=Cmd.do_teamup.__doc__)
parser_teamup_=parser_teamup.add_subparsers(title='subcommands',required=True,dest='subcommand_0')
parser_teamup_load=parser_teamup_.add_parser('load',help='Load a team to surrent')
parser_teamup_load.add_argument('name',help='Teamup Name (default: %(default)s)',default='DEFAULT',nargs='?')
parser_teamup_save=parser_teamup_.add_parser('save',help='Save all teams')
parser_teamup_clear=parser_teamup_.add_parser('clear',help='Clear current team')
parser_teamup_reload=parser_teamup_.add_parser('reload',help='Reload fgoTeamup.ini')
parser_teamup_list=parser_teamup_.add_parser('list',help='List all Teams')
parser_teamup_show=parser_teamup_.add_parser('show',help='Show current team info')
parser_teamup_set=parser_teamup_.add_parser('set',help='Setup a filed in current team')
parser_teamup_set_=parser_teamup_set.add_subparsers(title='subcommands',required=True,dest='subcommand_1')
parser_teamup_set_servant=parser_teamup_set_.add_parser('servant',help='Setup servant skill & hougu info')
parser_teamup_set_servant.add_argument('pos',help='Servant # (1-6)',type=int,choices=range(1,7))
parser_teamup_set_servant.add_argument('value',help='Info value (e.g. 1007-xxxx-1007-2x, add hyphens(-) anywhere as they will be removed, x for no change)',type=str.upper)
parser_teamup_set_master=parser_teamup_set_.add_parser('master',help='Setup master skill info')
parser_teamup_set_master.add_argument('value',help='Info value (e.g. 1107-xxxx-21347, add hyphens(-) anywhere as they will be removed, x for no change)',type=str.upper)
parser_teamup_set_index=parser_teamup_set_.add_parser('index',help='Setup team index')
parser_teamup_set_index.add_argument('value',help='Team index (0-10)',type=int,choices=range(0,11))

parser_call=ArgParser(prog='call',description=Cmd.do_call.__doc__)
parser_call.add_argument('func',help='Additional feature name',choices=['gacha','jackpot','mailFiltering'])
parser_call.add_argument('-s','--sleep',help='Sleep before run (default: %(default)s)',type=float,default=0)

parser_169=ArgParser(prog='169',description=Cmd.do_169.__doc__)
parser_169.add_argument('action',help='Action',type=str.lower,choices=['invoke','revoke'])

parser_press=ArgParser(prog='press',description=Cmd.do_press.__doc__)
parser_press.add_argument('button',help='Button',type=str.upper)
parser_press.add_argument('-c','--code',help='Use virtual key code',action='store_true')

def main():Cmd().cmdloop()
