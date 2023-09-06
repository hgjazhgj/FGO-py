#/bin/sh
export fgo_python=/usr/local/python-3.9.10/bin/python3.9
export adb=/usr/local/adb/bin/adb
# 在aidlux下fgo.py的文件位置
export FGO="/home/FGO-py/FGO-py/fgo.py"
# 取第一个输入参数为设备名,如果你的adb只有连接一个设备没输入也行
export PORT=5555
export DEVICE=localhost:$PORT
if [ -z "$1" ]; then
    export MODE=$1
else
    export MODE=battle
fi
# 去fgoConst.py查你的游戏包名替换
export FGO_PACKAGE_NAME="com.aniplex.fategrandorder.en"
# ACTIVITY_NAME应该是通用的，我个人测试台服跟美服都是jp.delightworks.Fgo.player.AndroidPlugin
export FGO_ACTIVITY_NAME="jp.delightworks.Fgo.player.AndroidPlugin"
$adb connect $DEVICE
$adb tcpip PORT
# 启动fgo
$adb -s "$DEVICE" shell am start -n $FGO_PACKAGE_NAME/$FGO_ACTIVITY_NAME
# 下列指令为连接运行设备进行萤幕比例调整然后运行推主线模式，如有需求自行替换
echo -e "connect $DEVICE \n 169 invoke \n $MODE" | $fgo_python $FGO cli
# 运行中断或结束后还原
echo -e "connect $DEVICE \n 169 revoke" | $fgo_python $FGO cli