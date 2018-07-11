#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/11 10:33
# @Author: yangjian
# @File  : reportheart.py

import json
import logging
import urllib
import urllib2
from logging.handlers import TimedRotatingFileHandler

import allip

# 日志
LOG_FILE = "/data/Agent/log/reportheart.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(LOG_FILE,when='D',interval=1,backupCount=30)
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = '%(asctime)s %(levelname)s %(message)s '
formatter = logging.Formatter(format_str, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)

# 读文件，获得机房ip
with open("/tmp/agent.lock", "r") as fd:
  jifangip = fd.read()

ips = allip.get_all_ips()
# {'ip': ['10.124.2.46', '10.148.138.133']}
data = json.dumps(ips)
headers = {"Content-Type":"application/json"}
url_base1 = "http://" + jifangip + "/autoProxyPlugIn/sendIp"
# 添加日志
req = urllib2.Request(url=url_base1, headers=headers, data=data.encode())
res = urllib2.urlopen(req)
data = res.read()
logging.info(data)

