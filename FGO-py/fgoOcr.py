from paddleocr import PaddleOCR
from fgoLogging import getLogger,logit
logger=getLogger('Ocr')
class Ocr(PaddleOCR):
    def __init__(self,lang):super().__init__(lang={'EN':'en','ZH':'ch','JA':'japan'}[lang])
    @logit(logger)
    def __call__(self,img):return super().ocr(img,det=False,cls=False)[0][0][0]
    def ocrInt(self,img):return int('0'+''.join(i for i in self(img)if i.isdigit()))
    def ocrText(self,img):return self(img)
    def ocrArea(self,img):...
