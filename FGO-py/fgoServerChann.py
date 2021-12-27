from requests import post
class ServerChann:
    def __init__(self,scKey):
        self.scKey=scKey
    def __call__(self,msg):
        try:return post(f'https://sctapi.ftqq.com/{self.scKey}.send',data={
            'title':'FGO-py',
            'desp':msg
        }).ok
        except:return False
