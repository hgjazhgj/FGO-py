> I got Muzashi Hougu+1 in new year bag, and 55 gachas for Nero(Caster)   
> I want Illya and Miyu!  

# "Intelligent combat without interruption, not relying on etiquette without turning" FGO fully automatic script  
**This script is for FGO simplified Chinese version, to use it on other vertions, you should change the pictures in /asserts**
This document does not contain all the information in its Chinese version and may not be updated in time.  
Some part of this file is translated by software. I jusk check it for some nomenclature just like change 'vow Yi Liya US tour' to 'I want Illya and Miyu'.  
The current version is v2.10.9  
GitHub project Address: [https://github.com/hgjazhgj/FGO-py/](https://github.com/hgjazhgj/FGO-py/)  
Jump to: [Version Logs](#Version-Logs)  
The current version is updated very quickly, so it is **not recommended to fork**  
You can star for future access  

# Warning
**This script may not be allowed by the law of your location. I will not be responsible for the loss caused by the use of this script, including but not limited to the above items. By downloading and using this script, you are aware of the possible risks and willing to bear the possible consequences.**  
***  
# Instruction   
The script can run in the background, not affect you to do other things until error occurs. The simulator window can lose focus, be blocked but not hidden or minimized. The system logout will not interfere with the script operation  
To use it on a real smart phone, see [here](#using-on-a-real-smart-phone)  
The Android resolution and the resolution actually displayed on the screen should preferably be 1920 width or 1080 height. Other resolutions can also be used  
You need an ADB tool on your computer  
You have to know a little bit of python3  
The following libraries are used:  
`time` `os` `numpy` `opencv-python` `pywin32` <del>`PyQt5`</del>  
You can use `pip install ...`if any one is missing    
Remember to turn on USB debugging mode  

Add code directly after `fgo\_py.py`, or use it as a module after importing.  
It is recommended to 'import fgo_py' in cmd then execute interactively to avoid repeatedly initializing resources  
The examples is in example.py  
**Please confirm the hougu and skill infomation before each operation**

+ At the interface that 'when you tap on the first item then you should select a friend' and start the `main` function to clear your AP. The function has at least three parameters: the number of apples to eat (default 0), the type of apples (0 gold, 1 silver, 2 copper, 3 color, default 0), and the battle function (default `onebattle`). Then there are the parameters to be passed to the battle function. The battle function should be responsible FROM where the card has not been selected after entering the battle TO the interface where the settlement of fetters or the prompt of team extinction appears, and return whether the battle is success or not  
+ Start the 'onebattle' function in the interface where the card has not been selected after entering the battle to complete the battle. If a `list` with three `int` is passed in, the enemies numbered from 1 from the left will be attacked preferentially in each stage  
+ If you want to pass a checkpoint in 3 turns, please write a battle function yourself  

This script will automatically play skills ([can be set](), no skills by default), auto play tools ([can be set](# you can modify the houguinfo array), auto use hougu when they are charged by default), and auto select cards (three color chain is preferred, otherwise red card is preferred).  

My email: huguangjing0411@geektip.cc  
Any technical problems or bug feedback or any problems in this readme, including but not limited to wrong words, syntax errors, description errors, please contact us, if you think it is helpful, please help me star
My foreign language level is really poor, so I can only answer some questions that I can express clearly
## changing slnPath,adbPath and hWnd  
`slnPath` Where fgo_py folder are  
`adbpath` How to connect to your android device  
`hWnd` Handle for the window that display your fgo game 
## change skillInfo and houguInfo  
You can rewrite `setInfo` function, to 'quickly change'     
`skillInfo[No.i servant]['s No.j skill]=['s minimum using stage,the minimum using turn in the stage,target(if no target,let it be 0)]`  
It means that, if you don't want to use a skill, let `skillInfo[i][j][0]=4`  
`houguInfo[No.i servant]=['s minimum using stage of its Hougu,the minimum using turn in the stage,priority(the smaller, the prior)]`  
## Friends  
You need to capture the friend you want to choose as some .png files in asserts/friend, just like the examples in asserts/friend/unused.  
If there's no file in asserts/friend, then the first one on your friend list will be choosen  
**the area on your image captured should can be tapped to chose this friend**, in fact, the center of your picture will be tapped  
If you a using a simulator, please use `screenShot` function or `Check().save()` instead the button on your simulator to capture, DON'T use <kbd>prtSc</kbd> key or other tools, It may takes error  
If you a use a smart phone, these function will also helps you  
`screenShot` is not used any more, you should remove '#' mark before it  
When using `Check().save()`function, It is strongly recommended that you should adjust the simulator window and android settings to 1080p to avoid zooms  
When using `screenShot`function, please make an 'adbtemp' folder in '/storge/emulated/0/' dir  
If there's a '\_' in filename, and it's 'km,ml,cba' before '\_', it means your friend gives ZhugeLiang, Merlin, Scáthach≒Skaði, It will take influence on using skill, have a look on `chooseFriend` function  
## using on a real smart phone  
The best way is using a software to copy the screen on your phone to your PC.
Try to edit `tap` and `swipe`
Try to add `Fuse.__max`
# Caution  
Simulator window cannot be minimized, try to turn off the 'Boss Key'  
It will not stop if one battle is failed  
`sound/default.wav` is <<final phase\>>, the opening song for <<Toaru Kagaku no Railgun T>>  
Sometime, especially on yuor servant looks almost the same, There will be mistakes on servant recognizing. Also, when there's less then 3 servent, the skill that has a target may cast incorrectly. So if you want to sleep, don't use alternate servants' skills, don't use the skills that has a target.  
If your game window is too small or not integral multiple scaled, there may be some incorrect recognization.  
# Version Logs  
## 2020/01/30 v2.10.9  
add English readme