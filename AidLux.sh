apt install -y gcc g++ clang make git zlib* openssl libssl* adb
wget https://www.python.org/ftp/python/3.9.9/Python-3.9.9.tgz # http://npm.taobao.org/mirrors/python/3.9.9/Python-3.9.9.tgz
tar zxvf Python-3.9.9.tgz
cd Python-3.9.9
./configure --enable-optimizations
make -j8
make altinstall
# pip3.9 config set global.index-url https://mirrors.aliyun.com/pypi/simple/
# pip3.9 config set install.trusted-host mirrors.aliyun.com
pip3.9 install airtest
cp /usr/bin/adb /usr/local/lib/python3.9/site-packages/airtest/core/android/static/adb/linux/
git clone https://github.com/hgjazhgj/FGO-py.git # https://gitee.com/hgjazhgj/FGO-py.git
cd FGO-py/FGO-py
python3.9 fgo.py cli
