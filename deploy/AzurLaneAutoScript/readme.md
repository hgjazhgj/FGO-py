# AlasFpyBridge

> 在[AzurLaneAutoScript](https://github.com/LmeSzinc/AzurLaneAutoScript)中使用FGO-py!  

本readme所在目录用于存放launch和halt文件,此二文件独立于FGO-py存在,用于定义Alas会以何种方式启动与停止FGO-py,你需要根据你自己的环境创建这些文件  
**你需要保证这些文件在Windows下具有`PATHEXT`中的任一扩展名,在Linux下具有可执行权限**  

- `launch`是启动命令,必须,无参数  
- `halt`是停止命令,可选,如无`halt`则使用默认的os.kill FGO-py进程,接收一个参数:FGO-py自身提供的pid,这意味着无论套了多少壳,halt总会接收到FGO-py最终的pid,即使FGO-py实际在另一台计算机上  

example目录下提供了些许示例,大致对应以下使用场景:  
plain - 基本的在linux机器上部署的Alas和FGO-py  
portable - 多数用户使用的portable installer安装的Alas和FGO-py  
docker - 在docker中运行FGO-py,而Alas在主机中  

## Windows下本机使用：(推荐使用docker方式！)

### portable方式：不推荐
portable.launch.bat 改名为 launch.bat,放到AzurLaneAutoScript目录下。

执行时报错：from .onnxruntime_pybind11_state import *: ImportError: DLL load failed while importing onnxruntime_pybind11_state: 动态链接库(DLL)初始化例程失败。  
解决：主要是因为onnxruntime版本问题，我本地是onnxruntime 1.22.1，改为1.17即可。  
pip uninstall onnxruntime   
pip install onnxruntime==1.17  

报错：SyntaxError: invalid syntax  
原因：ALAS用到python是3.7.6(AzurLaneAutoScript\toolkit)，不支持最新的match语法。故暂时不建议使用此方式。  

### docker方式：推荐
(1)将docker.launch改为launch.bat, docker.half改名为half.bat 放到AzurLaneAutoScript目录下。  
(2)修改launch.bat文件：  
docker run -v F:/develop/gameScriptTool/FGO-py-win/FGO-py/FGO-py:/FGO-py --name fgo-py -e NO_COLOR=1 -i --rm hgjazhgj/fgo-py   
主要是把-v 的宿主机路径改为你自己本地路径即可, 然后删掉#!/bin/bash，另外windows需要在系统-开发者选项中启用sudo才能使用sudo，否则删除sudo即可。   
(3)构建hgjazhgj/fgo-py镜像(cd到 deploy/Docker目录下)：  
docker build -t hgjazhgj/fgo-py .  

启动alas后，填写模拟器 Serial： 
即配置模拟器的 ip 和 端口： 192.168.31.128:5557  
PS： ip查询 执行ipconfig即可。  
模拟器端口 执行adb devices 。 
emulator-5556，我这里端口是+1后的5557，具体可执行此命令查看：netstat -ano | findstr :555  


## linux下使用
本人将Alas和FGO-py分别部署在两个docker容器中,那么,以下是本人实际使用的launch与halt:  

```bash
# launch
#!/bin/bash
ssh hgjazhgj@raspberrypi -o StrictHostKeyChecking=no "sudo docker run -v ~/hgjazhgj/FGO-py/FGO-py:/FGO-py --name fgo-py -e NO_COLOR=1 -i --rm hgjazhgj/fgo-py"

# halt
#!/bin/bash
ssh hgjazhgj@raspberrypi -o StrictHostKeyChecking=no "sudo docker stop fgo-py"
```

此外,你可以把本readme所在目录拷贝至其他位置方便分布式部署  
如果你像我一样在不同的机器上部署Alas和FGO-py,那么你需要在Alas可访问的位置创建包含launch(和halt)的目录并将其填入Alas中  
