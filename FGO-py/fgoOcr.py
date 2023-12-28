from pponnxcr import TextSystem
from fgoLogging import getLogger,logit
logger=getLogger('Ocr')
class Ocr(TextSystem):
    @logit(logger)
    def __call__(self,img):return super().ocr_single_line(img)[0]
    def ocrInt(self,img):return int('0'+''.join(i for i in self(img)if i.isdigit()))
    def ocrText(self,img):return self(img)
    def ocrArea(self,img):return[i.text for i in self.detect_and_ocr(img)]
