export fgo_python=/usr/local/python-3.9.10/bin/python3.9
export adb=/usr/local/adb/bin/adb
# 在aidlux下fgo.py的文件位置
export FGO="/home/FGO-py/FGO-py/fgo.py"
export DEVICE=localhost:5555
# 去fgoConst.py查你的游戏包名替换
export FGO_PACKAGE_NAME="com.aniplex.fategrandorder.en"
# ACTIVITY_NAME应该是通用的，我个人测试台服跟美服都是jp.delightworks.Fgo.player.AndroidPlugin
export FGO_ACTIVITY_NAME="jp.delightworks.Fgo.player.AndroidPlugin"
# 第一个输入为模式，默认模式为battle，使用方式为 /path/to/this_file battle
if [ -z "$1" ]; then
    export MODE=battle
else
    export MODE=$1
fi
$adb connect $DEVICE
# 启动fgo
$adb -s "$DEVICE" shell am start -n $FGO_PACKAGE_NAME/$FGO_ACTIVITY_NAME
# 下列指令为连接运行设备进行萤幕比例调整然后运行剧情推进模式，如有需求自行替换
echo -e "connect $DEVICE \n 169 invoke \n $MODE" | $fgo_python $FGO cli
# 运行中断或结束后还原
echo -e "connect $DEVICE \n 169 revoke" | $fgo_python $FGO cli