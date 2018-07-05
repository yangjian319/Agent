#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/5 10:26
# @Author: yangjian
# @File  : agentupdate.py
import os
import sys
import time
import urllib

url = "http://47.106.106.220/agent.py"

try:
  if os.fork() > 0:
    sys.exit(0)
except OSError, error:
  os.system("echo " + time.ctime() + "' update.py 1st fork failed!' >> /data/Agent/log/agent.log")
  sys.exit(1)

os.chdir('/')
os.setsid()
os.umask(0)

try:
  if os.fork() > 0:
    sys.exit(0)
except OSError,error:
  os.system("echo " + time.ctime() + "' update.py 2nd fork failed!' >> /data/Agent/log/agent.log")
  sys.exit(1)


# 下载新的agent
urllib.urlretrieve(url, "/data/Agent/temp/agent.py")

os.system("sh /data/Agent/temp/agentupdate.sh")