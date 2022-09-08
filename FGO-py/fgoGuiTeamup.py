import platform
from PyQt6.QtWidgets import QDialog
import fgoKernel
from fgoTeamupParser import IniParser
from fgoTeamupDialog import Ui_Teamup
logger=fgoKernel.getLogger('Teamup')

class Teamup(QDialog, Ui_Teamup):
    def __init__(self,parent=None,team='DEFAULT'):
        super().__init__(parent)
        self.setupUi(self)
        if platform.system()=='Darwin':self.setStyleSheet("QWidget{font-family:\"PingFang SC\";font-size:15px}")
        self.teamup=IniParser('fgoTeamup.ini')
        self.CBX_TEAM.addItems(self.teamup.sections())
        self.CBX_TEAM.setCurrentIndex(-1)
        self.reset()
    def load(self,team):
        (lambda skillInfo:[getattr(self,f'TXT_SKILL_{i}_{j}_{k}').setValue(skillInfo[i][j][k])for i in range(6)for j in range(3)for k in range(4)])(eval(self.teamup[team]['skillInfo']))
        (lambda houguInfo:[getattr(self,f'TXT_HOUGU_{i}_{j}').setValue(houguInfo[i][j])for i in range(6)for j in range(2)])(eval(self.teamup[team]['houguInfo']))
        (lambda masterSkill:[getattr(self,f'TXT_MASTER_{i}_{j}').setValue(masterSkill[i][j])for i in range(3)for j in range(4+(i==2))])(eval(self.teamup[team]['masterSkill']))
    def save(self):
        if not self.CBX_TEAM.currentText():return
        self.teamup[self.CBX_TEAM.currentText()]={
            'skillInfo':str([[[getattr(self,f'TXT_SKILL_{i}_{j}_{k}').value()for k in range(4)]for j in range(3)]for i in range(6)]).replace(' ',''),
            'houguInfo':str([[getattr(self,f'TXT_HOUGU_{i}_{j}').value()for j in range(2)]for i in range(6)]).replace(' ',''),
            'masterSkill':str([[getattr(self,f'TXT_MASTER_{i}_{j}').value()for j in range(4+(i==2))]for i in range(3)]).replace(' ','')}
        with open('fgoTeamup.ini','w')as f:self.teamup.write(f)
    def reset(self):self.load('DEFAULT')
    def accept(self):
        fgoKernel.ClassicTurn.skillInfo=[[[getattr(self,f'TXT_SKILL_{i}_{j}_{k}').value()for k in range(4)]for j in range(3)]for i in range(6)]
        fgoKernel.ClassicTurn.houguInfo=[[getattr(self,f'TXT_HOUGU_{i}_{j}').value()for j in range(2)]for i in range(6)]
        fgoKernel.ClassicTurn.masterSkill=[[getattr(self,f'TXT_MASTER_{i}_{j}').value()for j in range(4+(i==2))]for i in range(3)]
        return super().accept()
