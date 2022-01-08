import cmd,os,traceback

import fgoFunc
from fgoConst import version

class Cmd(cmd.Cmd):
    intro=f'''
FGO-py {version}, type help or ? for a list of commands.
'''
    prompt='FGO-py> '
    def emptyline(self):return
    def do_execute(self,line):
        try:exec(line)
        except Exception:traceback.print_exc()
    def do_shell(self,line):os.system(line)
    def do_exit(self,line):
        'Exit FGO-py'
        exit(0)
    def do_connect(self,line):
        'Connect'
        fgoFunc.device=fgoFunc.Device(line)
    def do_battle(self,line):
        'Battle'
        self.work=fgoFunc.Battle()
    def do_main(self,line):
        'Main'
        self.work=fgoFunc.Main(*[int(i)for i in line.split()])
        self.do_continue()
    def do_continue(self,line):
        try:self.work()
        except Exception:traceback.print_exc()

def main():Cmd().cmdloop()
