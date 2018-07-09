#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/9 16:37
# @Author: yangjian
# @File  : test_plugin.py

import os
import json
import urllib2

import datetime

import sys

p = os.getpid()

requrl = "http://47.106.106.220:5000/register"
plug_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
data = {}
data["plug_name"] = sys.argv[0].split("/")[-1]
data["plug_time"] = plug_time
data["plug_status"] = "0"
data["result"] = p
print(data)
# 将dict转换成json格式
data = json.dumps(data)
headers = {"Content-Type": "application/json"}
req = urllib2.Request(url=requrl, headers=headers, data=data.encode())
response = urllib2.urlopen(req)
print(response.read())







