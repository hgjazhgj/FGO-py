#!/bin/bash
aid install python-3.11.7
apt install -y git adb
# pip3.11 config set global.index-url https://mirrors.aliyun.com/pypi/simple/
# pip3.11 config set install.trusted-host mirrors.aliyun.com
pip3.11 install airtest tqdm pponnxcr
git clone https://github.com/hgjazhgj/FGO-py.git # https://gitee.com/hgjazhgj/FGO-py.git
cd FGO-py/FGO-py
python3.11 fgo.py cli
