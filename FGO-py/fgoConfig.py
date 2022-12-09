import json,os
from fgoConst import CONFIG
from fgoLogging import getLogger
logger=getLogger('Config')

class ConfigItemList(list):
    def __init__(self,iterable):super().__init__(ConfigItem(i)for i in iterable)
    def __setitem__(self,key,value):super().__setitem__(key,ConfigItem(value))
    def __add__(self,other):
        new=ConfigItemList(self)
        new.extend(other)
        return new
    def __radd__(self,other):return ConfigItemList(other)+self
    def __iadd__(self,other):
        self.extend(other)
        return self
    def __repr__(self):return f'{type(self).__name__}({", ".join(repr(i)for i in self)})'
    def append(self,obj):super().append(ConfigItem(obj))
    def copy(self):return ConfigItemList(self)
    def extend(self,iterable):super().extend(ConfigItemList(iterable))
    def insert(self,idx,obj):super().insert(idx,ConfigItem(obj))

class ConfigItem(dict):
    def __new__(cls,data=None):
        if isinstance(data,list):return ConfigItemList(data)
        if not isinstance(data,dict):return data
        return super().__new__(cls)
    def __init__(self,data=None):
        if data is None:return
        super().__init__((k,ConfigItem(v))for k,v in data.items())
        super().__setattr__('_callback',{})
    def __set(self,key,value):
        if(t1:=type(origin:=super().__getitem__(key)))is(t2:=type(value))or any(issubclass(t1,i)and issubclass(t2,i)for i in(list,dict)):
            super().__setitem__(key,ConfigItem(value))
            super().__getattribute__('_callback').get(key,lambda x:None)(value)
        else:logger.error(f'[{key}] Type Mismatch: ({t1.__name__}){origin} -> ({t2.__name__}){value}')
    def __getitem__(self,key):
        result=self
        for k in key.split('.'):result=dict.__getitem__(result,k)if isinstance(result,dict)else result[int(k)]
        return result
    def __setitem__(self,key,value):
        target=self
        keys=key.split('.')
        for k in keys[:-1]:target=dict.__getitem__(target,k)if isinstance(target,dict)else target[int(k)]
        if isinstance(target,dict):target.__set(keys[-1],value)
        else:target[int(keys[-1])]=value
  # def __missing__(self,key):return ConfigItem()
    def __getattr__(self,name):return super().__getitem__(name)
    def __setattr__(self,name,attr):self.__set(name,attr)
    def __or__(self,other):
        new=ConfigItem(self)
        new.update(other)
        return new
    def __ror__(self,other):return ConfigItem(other)|self
    def __ior__(self,other):
        self.update(other)
        return self
    def __contains__(self,key):
        try:self[key]
        except KeyError:return False
        return True
    def __repr__(self):return f'{type(self).__name__}({", ".join(f"{k}={v!r}"for k,v in self.items())})'
    def callback(self,key,callable):
        if'.'in key:return self[key[:key.rfind('.')]].callback(key[key.rfind('.')+1:],callable)
        super().__getattribute__('_callback')[key]=callable
    def update(self,other):
        for k,v in self.items():
            if k not in other:continue
            if isinstance(v2:=other[k],dict)and isinstance(v,dict):return v.update(v2)
            self.__set(k,v2)
    def copy(self):return ConfigItem(self)
    def todict(self):
        def todict(configItem):
            if isinstance(configItem,dict):return{k:todict(v)for k,v in configItem.items()}
            if isinstance(configItem,list):return[todict(i)for i in configItem]
            return configItem
        return todict(self)
    def flatten(self):
        def flatten(configItem):
            if isinstance(configItem,dict):return{f'{k}.{k2}':v2 for k,v in configItem.items()for k2,v2 in flatten(v).items()}
            if isinstance(configItem,list):return{f'{k}.{k2}':v2 for k,v in enumerate(configItem)for k2,v2 in flatten(v).items()}
            return{'':configItem}
        return[(k[:-1],v)for k,v in flatten(self).items()]

class Config(ConfigItem):
    def __new__(cls,file):return super().__new__(cls,CONFIG)
    def __init__(self,file='fgoConfig.json'):
        super().__init__(CONFIG)
        self.__dict__['file']=file
        if os.path.isfile(file):
            with open(file,encoding='utf-8')as f:self.update(json.load(f))
    def save(self,file=None):
        logger.info('Saving Config...')
        with open(self.file if file is None else file,'w',encoding='utf-8')as f:json.dump(self,f,ensure_ascii=False,indent=4)
