# docker build -t hgjazhgj/fgo-py:latest .
# docker run -v $PWD/FGO-py:/FGO-py --name fgo-py -it hgjazhgj/fgo-py

FROM ubuntu
ARG TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive
#&& python3.9 -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
#&& python3.9 -m pip config set install.trusted-host mirrors.aliyun.com \
RUN apt update \
 && apt install -y gnupg \
 && echo deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu focal main > /etc/apt/sources.list.d/deadsnakes-ubuntu-ppa-focal.list \
 && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys BA6932366A755776 \
 && apt update \
 && apt install -y curl git python3.9 python3.9-distutils \
 && ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime \
 && echo ${TZ} > /etc/timezone \
 && dpkg-reconfigure -f noninteractive tzdata \
 && curl https://bootstrap.pypa.io/get-pip.py | python3.9 \
 && python3.9 -m pip install airtest \
 && python3.9 -m pip uninstall -y opencv-contrib-python \
 && python3.9 -m pip install opencv-contrib-python-headless
CMD cd FGO-py && python3.9 fgo.py cli
