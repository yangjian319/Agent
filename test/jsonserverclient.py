#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/13 9:24
# @Author: yangjian
# @File  : jsonserverclient.py

import os
import json
import urllib
import urllib2


requrl = "http://127.0.0.1"

req_data = {}
ips = {'ip': ['10.124.2.46', '10.148.138.133']}
#req_data['md5'] = "16asfas1f6a1faawg"
req_data = json.dumps(ips)
headers = {"Content-Type": "application/json"}
req = urllib2.Request(url=requrl, headers=headers, data=req_data.encode())
res = urllib2.urlopen(req)
data = res.read()
print(data)