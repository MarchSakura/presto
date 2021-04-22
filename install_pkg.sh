#!/usr/bin/bash

yum install -y glib2-devel
yum install -y libX11 libX11-devel
yum install -y xorg-x11-drivers.x86_64
yum install -y python-devel
yum install -y tkinter
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple numpy==1.16.0
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple Matplotlib==2.2.5
