#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/4 9:25
# @Author: yangjian
# @File  : agent.py


'''
1、上报心跳，采用threading方式
2、守护进程
3、自升级，自动升级agent.py
4、日志，agent调用插件
'''
import commands
import json
import logging
import socket
import threading
import urllib
import urllib2
import time
import os
import sys
from plugin import allip
from logging.handlers import TimedRotatingFileHandler

# 日志
LOG_FILE = "/home/opvis/Agent/log/agent.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(LOG_FILE, when='D', interval=1, backupCount=30)
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = '%(asctime)s %(levelname)s %(message)s '
formatter = logging.Formatter(format_str, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)

# 判断本机属于哪个机房，并把机房ip写入本地文件中供插件上报使用，这个过程需要12s左右
iplist = ["172.30.130.137:18382", "172.30.130.126:18382", "10.124.5.163:18382", "10.144.2.248:18382",
          "10.123.30.177:18382", "172.30.194.121:18382", "172.16.5.20:18382", "10.181.1.0:18382"]
for ip in iplist:
  try:
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    so.settimeout(2)
    so.connect((ip.split(":")[0], 18382))
    currentip = ip
    with open("/home/opvis/Agent/agent.lock", "wb") as fd:
      fd.write(currentip)
    so.close()
  except Exception as e:
    logging.info(e)

# 机房ip
jifangip = currentip
plugin_dir = "/home/opvis/Agent/plugin/"

# 创建日志文件目录，这个其实都不用，它在安装agent的时候不是要下发一个tar.gz包吗，目录直接在里面建好？
logdir = "/home/opvis/Agent/log"
if not os.path.exists(logdir):
  os.makedirs(logdir)

# 建立UDP
try:
  address = ("0.0.0.0", 9997)
  udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udpsocket.b
except Exception as e:
  logging.info(e)

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


# 安装agent的时候就上传一次md5值入库
def post_md5():
  (status, md5) = commands.getstatusoutput("sudo md5sum /root/.ssh/authorized_keys|awk '{print $1}'")
  requrl = "http://" + jifangip + "/umsproxy/autoProxyPlugIn/uploadMD5"
  req_data = {}
  req_data['md5'] = md5
  args_restful = urllib.urlencode(req_data)
  req = urllib2.Request(url=requrl, data=args_restful)
  res = urllib2.urlopen(req)
  data = res.read()
  logging.info("上传md5值到proxy：" + data)

try:
  post_md5()
except Exception as e:
  logging.info(e)


def file_name(plugin_dir):
  list = []
  for root, dirs, files in os.walk(plugin_dir):
    for file in files:
      if os.path.splitext(file)[1] == '.py':
        list.append(file)
  return list


# 上报已安装的插件（后期把update相关的插件单独放到一个update的文件夹？）
def sendFileName():
  while True:
    requrl = "http://" + jifangip + "/umsproxy/autoProxyPlugIn/sendFileName"
    filenames = file_name(plugin_dir)
    #name = {}
    name = {"names": filenames}
    name = urllib.urlencode(name)
    req = urllib2.Request(url=requrl, data=name)
    res = urllib2.urlopen(req)
    data = res.read()
    logging.info("上报已安装插件到proxy：" + data)
    time.sleep(float(60))
try:
  sendfilename = threading.Thread(target=sendFileName, args=())
  sendfilename.start()
except Exception as e:
  logging.info(e)


# 心跳，定期检查agent.lock存在否，
def reportheart():
  while True:
    # 读文件，获得机房ip
    if os.path.exists("/home/opvis/Agent/agent.lock"):
      with open("/home/opvis/Agent/agent.lock", "r") as fd:
        jifangip = fd.read()
    else:
      logging.info("机房ip地址文件不存在")
      sys.exit(1)

    ips = []
    ip = {}
    allips = allip.get_all_ips()

    for item in allips:
      hip = allip.re_format_ip(item)
      out = allip.read_ip(hip)
      out.replace("\n", "")
      out.replace("\r", "")
      if out == "127.0.0.1":
        continue
      ips.append(out)
      ip["ip"] = ",".join(ips)
    logging.info(ip)
    ip = urllib.urlencode(ip)
    requrl = "http://" + jifangip + "/umsproxy/autoProxyPlugIn/sendIp"
    req = urllib2.Request(url=requrl, data=ip)
    res = urllib2.urlopen(req)
    data = res.read()
    logging.info("上报心跳到proxy：" + data)
    time.sleep(float(30))
try:
  t = threading.Thread(target=reportheart, args=())
  t.daemon = True
  t.start()
except Exception as e:
  logging.info(e)

# 接收controller消息
while True:
  data, addr = udpsocket.recvfrom(2018)
  data1 = "{0}".format(data)
  lstr = "'''"
  rstr = "'''"
  data2 = lstr + data1 + rstr
  dic = json.loads(data)  # str
  # data = json.dumps(data)
  logging.info(dic)
  name = dic.get("name")
  if name == "agentupdate":
    break
  else:
    # 调用插件
    def callplugin():
      cmd = "python /home/opvis/Agent/plugin/update.py" + " " + data2
      ret = os.system(cmd)
    try:
      t = threading.Thread(target=callplugin, args=())
      t.daemon = True
      t.start()
    except Exception, e:
      logging.info(e)

# 自升级
udpsocket.close()
try:
  cmd = "python /home/opvis/Agent/plugin/agentupdate.py" + " " + data2
  ret = os.system(cmd)
except Exception as e:
  logging.info(e)
sys.exit(0)