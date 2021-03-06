#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/5 10:26
# @Author: yangjian
# @File  : agentupdate.py

import os
import sys
import json
import urllib
import logging
from logging.handlers import TimedRotatingFileHandler

LOG_FILE = "/home/opvis/Agent/log/agent.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(LOG_FILE,when='D',interval=1,backupCount=30)
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = '%(asctime)s %(levelname)s %(message)s '
formatter = logging.Formatter(format_str, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)

data = sys.argv[1:]
logging.info("Get data from proxy: " + str(data))
dic = data[0]
dic = json.loads(dic)
url = dic.get("agentUrl")
logging.info("Download agent url: " + str(url))

try:
  if os.fork() > 0:
    sys.exit(0)
except OSError, error:
  logging.info("Agent update first fork failed!")
  sys.exit(1)

os.chdir('/')
os.setsid()
os.umask(0)

try:
  if os.fork() > 0:
    sys.exit(0)
except OSError,error:
  logging.info("Agent update second fork failed!")
  sys.exit(1)

urllib.urlretrieve(url, "/home/opvis/Agent/temp/agent.py")
logging.info("Download successfully!")
os.system("sh /home/opvis/Agent/update/agentupdate.sh")
logging.info("Update agent.py successfully!")