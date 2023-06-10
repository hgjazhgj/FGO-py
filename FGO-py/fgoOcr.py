from paddleocr import PaddleOCR
from fgoLogging import getLogger,logMeta
logger=getLogger('Ocr')
class Ocr(PaddleOCR,metaclass=logMeta(logger)):
    def __init__(self,lang):super().__init__(lang={'EN':'en','ZH':'ch','JA':'japan'}[lang])
    def ocr(self,img):return super().ocr(img,det=False,cls=False)[0][0][0]
