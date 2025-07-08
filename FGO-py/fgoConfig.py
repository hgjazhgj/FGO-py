import json,os
from fgoConst import CONFIG
from fgoLogging import getLogger
logger=getLogger('Config')

class ConfigItemList(list):
    def __init__(self,iterable):super().__init__(ConfigItem(i)for i in iterable)
    def __setitem__(self,key,value):super().__setitem__(key,ConfigItem(value))
    def __add__(self,other):return ConfigItemList(self).extend(other)
    def __radd__(self,other):return ConfigItemList(other).extend(self)
    def __iadd__(self,other):return self.extend(other)
    def __repr__(self):return f'{type(self).__name__}({", ".join(repr(i)for i in self)})'
    def copy(self):return ConfigItemList(self)
    def append(self,obj):
        super().append(ConfigItem(obj))
        return self
    def extend(self,iterable):
        super().extend(ConfigItemList(iterable))
        return self
    def insert(self,idx,obj):
        super().insert(idx,ConfigItem(obj))
        return self

class ConfigItem(dict):
    def __new__(cls,data=None):
        if isinstance(data,list):return ConfigItemList(data)
        if not isinstance(data,dict):return data
        return super().__new__(cls)
    def __init__(self,data=None):
        if data is None:data={}
        super().__init__((k,ConfigItem(v))for k,v in data.items())
    def __getitem__(self,key):
        result=self
        for k in key.split('.'):result=dict.__getitem__(result,k)if isinstance(result,dict)else result[int(k)]
        return result
    def __setitem__(self,key,value):
        target=self
        keys=key.split('.')
        for k in keys[:-1]:target=dict.__getitem__(target,k)if isinstance(target,dict)else target[int(k)]
        if isinstance(target,dict):target.__setattr__(keys[-1],value)
        else:target[int(keys[-1])]=value
  # def __missing__(self,key):return ConfigItem()
    def __getattr__(self,name):return super().__getitem__(name)
    def __setattr__(self,name,attr):
        if(t1:=type(origin:=super().__getitem__(name)))is(t2:=type(attr))or any(issubclass(t1,i)and issubclass(t2,i)for i in(list,dict)):
            super().__setitem__(name,ConfigItem(attr))
        else:logger.error(f'[{name}] Type Mismatch: ({t1.__name__}){origin} -> ({t2.__name__}){attr}')
    def __or__(self,other):return ConfigItem(self).update(other)
    def __ror__(self,other):return ConfigItem(other).update(self)
    def __ior__(self,other):return self.update(other)
    def __contains__(self,key):
        try:self[key]
        except(KeyError,IndexError):return False
        return True
    def __repr__(self):return f'{type(self).__name__}({", ".join(f"{k}={v!r}"for k,v in self.items())})'
    def update(self,other):
        for k,v in self.items():
            if(v2:=other.get(k))is None:continue
            if isinstance(v2,dict)and isinstance(v,dict):
                v.update(v2)
                continue
            self.__setattr__(k,v2)
        return self
    def copy(self):return ConfigItem(self)
    def todict(self):
        if isinstance(self,dict):return{k:ConfigItem.todict(v)for k,v in self.items()}
        if isinstance(self,list):return[ConfigItem.todict(i)for i in self]
        return self
    def flatten(self):
        if isinstance(self,dict):return{(k,*k2):v2 for k,v in self.items()for k2,v2 in ConfigItem.flatten(v).items()}
        if isinstance(self,list):return{(k,*k2):v2 for k,v in enumerate(self)for k2,v2 in ConfigItem.flatten(v).items()}
        return{():self}


class Config(ConfigItem):
    def __new__(cls,*args,**kwargs):return super().__new__(cls,CONFIG)
    def __init__(self,file='fgoConfig.json'):
        super().__init__(CONFIG)
        self.__dict__['file']=file
        if os.path.isfile(file):
            with open(file)as f:self.update(json.load(f))
    def save(self,file=None):
        logger.info('Save Config')
        with open(self.file if file is None else file,'w')as f:json.dump(self,f,ensure_ascii=False,indent=4)
