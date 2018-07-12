#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/10 9:39
# @Author: yangjian
# @File  : hostTrustRelationshipMD5.py

import ConfigParser
import os
import sys
import json
import urllib
import commands
import urllib2

# proxyAddress=http://10.124.5.163:18382/umsproxy

def monitor():
  # 获取authorized_keys的md5值
  get_md5_url = "http://10.124.5.163:18382/umsproxy/hostPlugInOperation/getHostTrustRelationshipMD5"
  # 上报返回结果
  upload_status_url = "http://10.124.5.163:18382/umsproxy/hostPlugInOperation/uploadOperationMD5Information"
  headers = {"Content-Type": "application/json"}
  data = urllib.urlopen(get_md5_url).read()
  md5_server = json.loads(data)["md5"]
  print(md5_server)

  ssh_path = "/root/.ssh"
  authorized_keys_path = "/root/.ssh/authorized_keys"
  ssh_path_mode = commands.getoutput('''ls -la /root|grep ".ssh"''').split(" ")[0]
  authorized_keys_mode = commands.getoutput("ls -l /root/.ssh/authorized_keys |awk '{print $1}'")
  authorized_keys_md5 = commands.getoutput("md5sum /root/.ssh/authorized_keys|awk '{print $1}'")

  if not os.path.exists(ssh_path):
      print("ssh目录不存在！")
      plug_status = "1"
      plug_status = urllib.urlencode(plug_status)
      req = urllib2.Request(url=upload_status_url, headers=headers, data=plug_status)
      res = urllib2.urlopen(req)
      data = res.read()
      print(data)
      sys.exit(1)
  elif ssh_path_mode != "drwx------":
      print("ssh目录的权限不是700！")
      plug_status = "2"
      plug_status = urllib.urlencode(plug_status)
      req = urllib2.Request(url=upload_status_url, headers=headers, data=plug_status)
      res = urllib2.urlopen(req)
      data = res.read()
      print(data)
      sys.exit(1)
  elif not os.path.exists(authorized_keys_path):
      print("authorized_keys文件不存在！")
      plug_status = "3"
      plug_status = urllib.urlencode(plug_status)
      req = urllib2.Request(url=upload_status_url, headers=headers, data=plug_status)
      res = urllib2.urlopen(req)
      data = res.read()
      print(data)
      sys.exit(1)
  elif authorized_keys_mode != "-rw-------":
      print("authorized_keys的权限不是600！")
      plug_status = "4"
      plug_status = urllib.urlencode(plug_status)
      req = urllib2.Request(url=upload_status_url, headers=headers, data=plug_status)
      res = urllib2.urlopen(req)
      data = res.read()
      print(data)
      sys.exit(1)
  elif authorized_keys_md5 != md5_server:
      print("authorized_keys的md5值和系统预设的不一致！")
      plug_status = "5"
      plug_status = urllib.urlencode(plug_status)
      req = urllib2.Request(url=upload_status_url, headers=headers, data=plug_status)
      res = urllib2.urlopen(req)
      data = res.read()
      print(data)
      sys.exit(1)
  else:
      print("一切正常！")
      plug_status = "0"
      plug_status = urllib.urlencode(plug_status)
      req = urllib2.Request(url=upload_status_url, headers=headers, data=plug_status)
      res = urllib2.urlopen(req)
      data = res.read()
      print(data)
      sys.exit(1)

if __name__ == "__main__":
  try:
    monitor()
  except Exception as e:
    print(e)
