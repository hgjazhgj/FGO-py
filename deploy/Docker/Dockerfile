# docker build -t hgjazhgj/fgo-py:latest .
# docker run -v $PWD/FGO-py:/FGO-py -p 5000:5000 --name fgo-py -it --rm hgjazhgj/fgo-py

FROM python:3.9-slim
WORKDIR /FGO-py
#&& python3.9 -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
#&& python3.9 -m pip config set install.trusted-host mirrors.aliyun.com \
#&& apt update \
#&& apt install -y adb \
#&& rm /usr/local/lib/python3.9/site-packages/airtest/core/android/static/adb/linux/adb \
#&& ln -s /usr/bin/adb /usr/local/lib/python3.9/site-packages/airtest/core/android/static/adb/linux/adb \
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
 && echo 'Asia/Shanghai' > /etc/timezone \
 && pip install airtest flask paddlepaddle paddleocr \
 && pip uninstall -y opencv-contrib-python \
 && pip install opencv-contrib-python-headless \
 && rm -r ~/.cache/pip
CMD ["python", "fgo.py", "cli"]
