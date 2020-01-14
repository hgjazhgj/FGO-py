from fgo_py import *

#setSkillInfo('rider')
#main()
#main(0,2,danger=(0,1,2))
#main(battleFunc=otk)
#otk()

#setSkillInfo('lancer')
##oneBattle((0,0,1))
#main(danger=(0,0,1))

try:
    setSkillInfo('lancer')
    #oneBattle((0,2,1))
    main(150,0,danger=(0,2,1))
finally:
    playSound()

