VERSION='v10.4.2'
CONFIG={
'runOnce':'',
'device':'',
'package':'com.bilibili.fatego',
'teamIndex':0,
'farming':False,
'stopOnDefeated':True,
'stopOnKizunaReisou':True,
'stayOnTop':False,
'closeToTray':False,
'notifyEnable':False,
'notifyParam':[]
}
# F1-F10        选取编队
# 12345         选卡,234指向技能的目标,银苹果
# 678           宝具卡,选取剧情选项,8选取第一个关卡
# QWER          御主技能,W剧情选项/金苹果
# TYUIOP        换人礼装
# <BackSpace>   跳过/商店
# =             无响应区域
# ASDFGHJKL     从者技能,F取消,K确认/铜苹果
# ;             刷新助战列表
# \\            下一个无限池
# Z             确认换人
# X             对战结束时不发送好友申请
# C             战败撤退
# N             补充体力
# M             再次进行十连召唤
# <Space>       选卡/下一步/菜单
# NUM4-9        选取敌人,NUM7返回/关闭
KEYMAP={
'\x70':(527,47),'\x71':(552,49),'\x72':(577,49),'\x73':(602,49),'\x74':(627,49),'\x75':(652,49),'\x76':(677,49),'\x77':(702,49),'\x78':(727,49),'\x79':(752,49), # VK_F1..10
'1':(185,427),'2':(399,427),'3':(649,427),'4':(875,427),'5':(1101,427),'6':(431,203),'7':(651,203),'8':(845,203),'\xBB':(876,46),'\x08':(1253,46), # = VK_OEM_PLUS VK_BACK
'Q':(1200,317),'W':(907,317),'E':(995,317),'R':(1084,317),'T':(140,360),'Y':(340,360),'U':(540,360),'I':(740,360),'O':(940,360),'P':(1140,360),'\xDC':(1213,245), # \ VK_OEM_5
'A':(73,573),'S':(163,573),'D':(257,573),'F':(388,573),'G':(483,573),'H':(574,573),'J':(704,573),'K':(801,573),'L':(891,573),'\xBA':(927,131), # ; VK_OEM_1
'Z':(640,629),'X':(173,621),'C':(330,320),'N':(165,694),'M':(800,667),
'\x1B':(40,40),' ':(1231,687), # VK_ESCAPE
'\x64':(45,142),'\x65':(295,142),'\x66':(545,142),'\x67':(142,40),'\x68':(342,40),'\x69':(542,40) # VK_NUMPAD4..9
}
I18N={
'ProofOfHero':'英雄之证',
'EvilBone':'凶骨',
'DragonFang':'龙之牙',
'VoidsDust':'虚影之尘',
'FoolsChain':'愚者之锁',
'DeadlyPoisonousNeedle':'万死的毒针',
'MysticSpinalFluid':'魔术髓液',
'StakeOfWailingNight':'宵泣之铁桩',
'MysticGunpowder':'振荡火药',
'SmallBellOfAbsolution':'赦免的小钟',
'SeedOfYggdrassil':'世界树之种',
'GhostLantern':'鬼魂提灯',
'OctupletCrystals':'八连双晶',
'SerpentJewel':'蛇之宝玉',
'PhoenixFeather':'凤凰羽毛',
'EternalGear':'无间齿轮',
'ForbiddenPage':'禁断书页',
'HomunculusBaby':'人工生命体幼体',
'MeteorHorseshoe':'陨蹄铁',
'GreatKnightMedal':'大骑士勋章',
'ShellOfReminiscence':'追忆的贝壳',
'RefinedMagatama':'枯淡勾玉',
'EternalIce':'永远结冰',
'GiantsRing':'巨人的戒指',
'AuroraSteel':'极光之钢',
'SoundlessBell':'闲古铃',
'ArrowheadOfMalice':'祸罪之箭头',
'CrownOfSilveryLight':'光银之冠',
'DivineSpiritron':'神脉灵子',
'BallOfRainbowThread':'虹之线球',
'ScalesOfFantasy':'梦幻的鳞粉',
'ClawOfChaos':'混沌之爪',
'HeartOfTheForeignGod':'蛮神心脏',
'DragonsReverseScale':'龙之逆鳞',
'SpiritRoot':'精灵根',
'WarhorsesYoungHorn':'战马的幼角',
'TearstoneOfBlood':'血之泪石',
'BlackBeastGrease':'黑兽脂',
'LampOfEvilSealing':'封魔之灯',
'ScarabOfWisdom':'智慧之圣甲虫像',
'PrimordialLanugo':'起源的胎毛',
'CursedBeastGallstone':'咒兽胆石',
'MysteriousDivineWine':'奇奇神酒',
'ReactorCoreOfDawn':'晓光炉心',
'TsukumoMirror':'九十九镜',
'EggOfTruth':'真理之卵',
'FragmentOfATwinklingStar':'煌星碎片',
'FruitOfEternity':'悠久果实',
'FlamingOniLanternPlant':'鬼炎鬼灯'
}
