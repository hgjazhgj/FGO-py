# AlasFpyBridge

> 在[AzurLaneAutoScript](https://github.com/LmeSzinc/AzurLaneAutoScript)中使用FGO-py!  

此处定义了Alas会以何种方式启动与停止FGO-py  
`launch`是启动命令,Windows下具有`.bat`扩展名,Linux下具有`.sh`扩展名与可执行权限  
`halt`是停止命令,接收一个参数:FGO-py自身提供的pid,这意味着无论套了多少层壳,halt总会接收到FGO-py最终的pid,即使FGO-py实际在另一台计算机上  
`halt`是可选的,如无`halt`则使用默认的os.kill FGO-py进程  

example目录下提供了些许示例,大致对应以下使用场景:  
plain - 基本的在linux机器上部署的Alas和FGO-py  
portable - 多数用户使用的portable installer安装的Alas和FGO-py  
docker - 在docker中运行FGO-py,而Alas在主机中  

本人将Alas和FGO-py分别部署在两个docker容器中,那么,以下是本人实际使用的launch与halt:  

```bash
# launch
#!/bin/bash
ssh hgjazhgj@raspberrypi -o StrictHostKeyChecking=no "sudo docker run -v ~/hgjazhgj/FGO-py/FGO-py:/FGO-py --name fgo-py -e NO_COLOR=1 -i --rm hgjazhgj/fgo-py"

# halt
#!/bin/bash
ssh hgjazhgj@raspberrypi -o StrictHostKeyChecking=no "sudo docker stop fgo-py"
```

你需要在Alas的配置文件中指定这个这个deploy/Alas目录的位置  
如果你像我一样在不同的机器上部署Alas和FGO-py,那么你需要将这个deploy/Alas目录拷贝到Alas可访问的位置  
