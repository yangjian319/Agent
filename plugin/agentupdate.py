#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/5 10:26
# @Author: yangjian
# @File  : agentupdate.py
import logging
import os
import sys
import time
import urllib
from logging.handlers import TimedRotatingFileHandler

# 日志
LOG_FILE = "/data/Agent/log/agent.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(LOG_FILE,when='D',interval=1,backupCount=30)
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = '%(asctime)s %(levelname)s %(message)s '
formatter = logging.Formatter(format_str, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)


dic = sys.argv[1:]
tmp_url = dic.get('url')
# 自升级的url需要确定一下
url = "http://" + tmp_url.split("/")[2] + "agent文件路径需要确定"  # 待修改


try:
  if os.fork() > 0:
    sys.exit(0)
except OSError, error:
  msg = "agentupdate first fork failed!"
  logging.info(msg)
  sys.exit(1)

os.chdir('/')
os.setsid()
os.umask(0)

try:
  if os.fork() > 0:
    sys.exit(0)
except OSError,error:
  msg = "agentupdate second fork failed!"
  logging.info(msg)
  sys.exit(1)


# 下载新的agent
urllib.urlretrieve(url, "/data/Agent/temp/agent.py")
os.system("sh /data/Agent/temp/agentupdate.sh")