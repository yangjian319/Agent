#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/4 9:25
# @Author: yangjian
# @File  : agent.py

'''
1、上报心跳，采用threading方式
2、守护进程
3、自升级，自动升级agent.py
'''
import json
import logging
import socket
import threading
import urllib2
import time
import os
import sys
from logging.handlers import TimedRotatingFileHandler


# 心跳接口
import datetime

hearturl = "http://47.106.106.220:5000/register"

# 创建日志文件目录
logdir = "/data/Agent/log"
if not os.path.exists(logdir):
    os.makedirs(logdir)

# 建立UDP
address = ("0.0.0.0", 9998)
udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpsocket.bind(address)


# 日志
'''
定义日志格式，以及轮转周期为天
'''
LOG_FILE = "/data/Agent/log/agent.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(LOG_FILE,when='D',interval=1,backupCount=30)
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = '%(asctime)s %(levelname)s %(message)s '
#formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
formatter = logging.Formatter(format_str, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)

'''
删除7天前的日志，写成定时任务
'''
def del_log(logdir):
  for parent, dirnames, filenames in os.walk(logdir):
          for filename in filenames:
            fullname = parent + "/" + filename #文件全称
            createTime = int(os.path.getctime(fullname)) #文件创建时间
            nDayAgo = (datetime.datetime.now() - datetime.timedelta(days = 7)) #当前时间的n天前的时间
            timeStamp = int(time.mktime(nDayAgo.timetuple()))
            if createTime < timeStamp: #创建时间在n天前的文件删除
              os.remove(os.path.join(parent,filename))

#del_log(logdir)

# 创建守护进程

try:
  if os.fork() > 0:
    sys.exit(0)
except OSError, error:
  msg = "agent.py first fork failed!"
  logging.info(msg)
  sys.exit(1)

os.chdir("/")
os.setsid()
os.umask(0)

try:
  if os.fork() > 0:
    sys.exit(0)
except OSError, error:
  msg = "agent.py second fork failed!"
  logging.info(msg)
  sys.exit(1)


# 心跳部分
# 暂时只上传了一个hostname
def func(username):
  while True:
    data = json.dumps(username)
    req = urllib2.Request(url=hearturl, data=data)
    heartreport = urllib2.urlopen(req)
    print(heartreport.read())
    time.sleep(10)

gethostname = socket.gethostname()
hostname = {}
hostname["username"] = gethostname
t = threading.Thread(target=func, args=(hostname,))
t.daemon = True
t.start()

while True:
  data = udpsocket.recv(1024)
  rec_data = str(data)
  msg = rec_data.rstrip("\n")
  logging.info(msg)
  print(os.getpid())
  print(os.getppid())
  if rec_data.startswith("agentupdate.py"):
    break
  else:
    # 调用插件的时候执行
    print("这是else部分")
# 自升级的时候执行
udpsocket.close()
print("开始升级")
ret = os.popen("python /data/Agent/plugin/" + str(data).rstrip('\n')).read()
print(ret)
sys.exit(0)
print("开始升级123")
