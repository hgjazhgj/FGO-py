class HorizontalAlignment:
    AlignFixed=0
    AlignLeft=1
    AlignCenter=2
    AlignRight=3
# class VerticalAlignment:
#     AlignFixed=0
#     AlignTop=1
#     AlignMiddle=2
#     AlignBottom=3
class CoordinateTransformer:
    def __init__(self,toSize,fromSize=(1920,1080),newUi=False):
        self.fromSize=fromSize
        self.toSize=toSize
        self.newUi=newUi
    def __call__(self,pos,align):
        x,y=pos
        if self.newUi:raise NotImplementedError
        else:
            if align[0]==HorizontalAlignment.AlignCenter:
                pass
            elif align[0]==HorizontalAlignment.AlignRight:
                pass
            elif align[0]==HorizontalAlignment.AlignLeft:
                pass
            # if align[1]==VerticalAlignment.AlignMiddle:
            #     pass
            # elif align[1]==VerticalAlignment.AlignBottom:
            #     pass
            # elif align[1]==VerticalAlignment.AlignTop:
            #     pass
            return x,y
