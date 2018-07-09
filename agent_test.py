#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/4 9:25
# @Author: yangjian
# @File  : agent.py

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
    # get_threadname = threading.current_thread().name
    # get_threadcount = threading.activeCount()
    # print(get_threadname)
    # print(get_threadcount)
    time.sleep(10)

gethostname = socket.gethostname()
hostname = {}
hostname["username"] = gethostname
#t = threading.Thread(target=func, args=(hostname,), name="Thread_A")
t = threading.Thread(target=func, args=(hostname,))
t.daemon = True
t.start()

while True:
  data = udpsocket.recv(1024)
  rec_data = str(data)
  msg = rec_data.rstrip("\n")
  logging.info(msg)
  if rec_data.startswith("agentupdate.py"):
    break
  else:
    # 调用插件
    def func():
      ret = os.system("python /data/Agent/plugin/" + str(data).rstrip('\n'))
    #   get_threadname = threading.current_thread().name
    #   print(get_threadname)
    # t = threading.Thread(target=func, args=(), name="Thread_B")
    t = threading.Thread(target=func, args=())
    t.daemon = True
    t.start()
    print("执行get_pid.py")

# 自升级的时候执行
udpsocket.close()
print("开始升级")
ret = os.system("python /data/Agent/plugin/" + str(data).rstrip('\n'))
sys.exit(0)

