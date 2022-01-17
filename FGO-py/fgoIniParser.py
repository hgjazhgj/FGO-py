from configparser import ConfigParser
IniParser=type('IniParser',(ConfigParser,),{'__init__':lambda self,file:(ConfigParser.__init__(self),self.read(file,'utf-8'))[0],'optionxform':lambda self,optionstr:optionstr})
