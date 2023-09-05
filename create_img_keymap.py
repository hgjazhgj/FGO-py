import cv2

target = cv2.imread("skillpos.png")
KEYMAP={
'\\x70':(527,47),'\\x71':(552,49),'\\x72':(577,49),'\\x73':(602,49),'\\x74':(627,49),'\\x75':(652,49),'\\x76':(677,49),'\\x77':(702,49),'\\x78':(727,49),'\\x79':(752,49), # VK_F1..10
'1':(185,440),'2':(399,440),'3':(649,440),'4':(875,440),'5':(1101,440),'6':(431,203),'7':(651,203),'8':(845,203),'\\xBB':(876,46),'\\x08':(1253,46), # = VK_OEM_PLUS VK_BACK
'Q':(1200,317),'W':(907,317),'E':(995,317),'R':(1084,317),'T':(140,360),'Y':(340,360),'U':(540,360),'I':(740,360),'O':(940,360),'P':(1140,360),'\\xDC':(1213,245), # \ VK_OEM_5
'A':(73,573),'S':(163,573),'D':(257,573),'F':(388,573),'G':(483,573),'H':(574,573),'J':(704,573),'K':(801,573),'L':(891,573),'\\xBA':(927,131), # ; VK_OEM_1
'Z':(640,629),'X':(173,621),'C':(330,320),'V':(1014,500),'N':(165,694),'M':(800,667),'\\xBC':(45,360),'\\xBE':(1235,360), # , VK_OEM_COMMA . VK_OEM_PERIOD
'\\x1B':(40,40),'space':(1231,687), # VK_ESCAPE
'\\x64':(45,142),'\\x65':(295,142),'\\x66':(545,142),'\\x67':(142,40),'\\x68':(342,40),'\\x69':(542,40), # VK_NUMPAD4..9
}

padding = (-40,0)
for text,i in KEYMAP.items():
    target = cv2.circle(target,i,5, (0,255,0), -1)
    target = cv2.putText(target,text,(i[0]+padding[0],i[1]+padding[1]),cv2.FONT_HERSHEY_SIMPLEX,0.75,color=(0,0,255),thickness=2)

for i in range(3):
    for j in range(3):
        skillpos = (35+318*i+88*j,598-55,55+318*i+88*j+55,618)
        center = (round(skillpos[0]/2+skillpos[2]/2),round(skillpos[1]/2+skillpos[3]/2))
        # target = cv2.circle(target,center,5, (0,255,255), -1)
        target = cv2.rectangle(target,(skillpos[0],skillpos[1]),(skillpos[2],skillpos[3]),color=(0,255,255))
        target = cv2.putText(target,f"s{i}{j}",(center[0]+padding[0],center[0]+padding[1]),cv2.FONT_HERSHEY_SIMPLEX,0.75,color=(255,0,255),thickness=2)

cv2.imwrite("keymaps.png",target)