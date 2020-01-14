from fgo_py import *

#setSkillInfo('rider')
#oneBattle((0,1,2))
#main()
#main(0,2,danger=(0,1,2))
#main(battleFunc=otk)
#otk()

#setSkillInfo('lancer')
##oneBattle((0,0,1))
#main(danger=(0,0,1))

try:
    setSkillInfo('lancer')
    main(160,0,danger=(0,2,1))
finally:
    playSound()

