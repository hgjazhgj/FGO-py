from configparser import ConfigParser
IniParser=type('IniParser',(ConfigParser,),{'__init__':lambda self,file:(ConfigParser.__init__(self),self.read(file))[0],'optionxform':lambda self,optionstr:optionstr})
