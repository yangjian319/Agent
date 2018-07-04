#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/4 9:25
# @Author: yangjian
# @File  : agent.py

'''
1、上报心跳，采用threading方式
2、守护进程
'''
import json
import socket
import threading
import urllib2
import time
import os
import sys


# 创建日志文件目录
logdir = "/data/Agent/log"
if not os.path.exists(logdir):
    os.makedirs(logdir)

# 建立UDP
address = ("0.0.0.0", 9997)
udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpsocket.bind(address)
#udpsocket.listen()

# 创建守护进程
try:
  if os.fork() > 0:
    sys.exit(0)
except OSError, error:
  os.system("echo " + time.ctime() + "' agent.py first fork failed!' >> /data/Agent/log/agent.log")
  sys.exit(1)

os.chdir("/")
os.setsid()
os.umask(0)

try:
  if os.fork() > 0:
    sys.exit(0)
except OSError, error:
  os.system("echo " + time.ctime() + "' agent.py second fork failed!' >> /data/agent/log/agent.log")
  sys.exit(1)


# 心跳部分
# 暂时只上传了一个hostname
class task(threading.Thread):
  def __init__(self,username=None):
    threading.Thread.__init__(self)
    self.username = username
  def run(self):
    hearturl = "http://47.106.106.220:5000/register"
    while True:
      data = json.dumps(self.username)
      req = urllib2.Request(url=hearturl, data=data)
      heartreport = urllib2.urlopen(req)
      print(heartreport.read())
      time.sleep(300)

gethostname = socket.gethostname()
hostname = {}
hostname["username"] = gethostname
heartbeat = task(hostname)
heartbeat.start()
