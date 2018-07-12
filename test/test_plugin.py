#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/9 16:37
# @Author: yangjian
# @File  : test_plugin.py

import os
import json
import urllib



'''
{u'status': 5, u'hostId': 3902, u'name': u'net', u'url': u'http://10.124.5.163:18382/proxyDownLoad/net_v03.py', u'plugId': 1, u'version': u'03', u'cycle': u''}

'''
import datetime

import sys

requrl = "http://47.106.106.220/agent.py"
html = urllib.urlopen(url)
html1 = html.read()
code = html.code
with open("download.py","wb") as fp:
  fp.write(html1)


# -*- coding:utf-8 -*-
import socket

iplist = ["172.30.130.137:18382", "172.30.130.126:18382", "10.124.5.163:18382", "10.144.2.248:18382", "10.123.30.177:18382", "172.30.194.121:18382", "172.16.5.20:18382", "10.181.1.0:18382"]
for ip in iplist:
  try:
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    so.settimeout(2)
    so.connect((ip.split(":")[0], 18382))
    with open("/tmp/agent.lock", "wb") as fd:
      fd.write(ip)
    so.close()
  except Exception:
    pass



#!/usr/bin/python
# -*- coding:utf-8 -*-
import socket
so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
so.settimeout(2)
try:
  so.connect(("172.30.130.137", 21))
  print("ok")
except Exception:
  print("wrong")
so.close()


import socket
sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sk.settimeout(1)
try:
    sk.connect(('10.144.2.248',21))
    print 'Server port 21 OK!'
except Exception:
    print 'Server port 21 not connect!'
sk.close()

import socket
so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
so.settimeout(2)
try:
    sk.connect(('10.123.30.177',18382))
    print 'Server port 21 OK!'
except Exception:
    print 'Server port 21 not connect!'
sk.close()


