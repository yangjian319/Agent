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

import os
import sys
import time
import json
import socket
import urllib
import urllib2
import logging
import commands
import threading
from plugin import allip
from logging.handlers import TimedRotatingFileHandler


VERSION = 1

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
    logging.info("Determine which area the machine belongs to error: " + str(e))

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
  udpsocket.bind(address)
except Exception as e:
  logging.info("Udp connection error: " + str(e))

# 创建守护进程
try:
  if os.fork() > 0:
    sys.exit(0)
except OSError, error:
  logging.info("agent.py first fork failed!")
  sys.exit(1)

os.chdir("/")
os.setsid()
os.umask(0)

try:
  if os.fork() > 0:
    sys.exit(0)
except OSError, error:
  logging.info("agent.py second fork failed!")
  sys.exit(1)


# 安装agent的时候就上传一次md5值入库
def post_md5():
  (status, md5) = commands.getstatusoutput("sudo md5sum /root/.ssh/authorized_keys|awk '{print $1}'")
  requrl = "http://" + jifangip + "/umsproxy/autoProxyPlugIn/uploadMD5"
  req_data = {}
  req_data['md5'] = md5
  try:
    args_restful = urllib.urlencode(req_data)
    req = urllib2.Request(url=requrl, data=args_restful)
    res = urllib2.urlopen(req)
    data = res.read()
  except Exception as e:
    logging.info("Upload the native MD5 value to the proxy error: " + str(e))
  logging.info("Upload the native MD5 value to the proxy successfully: " + str(data))

try:
  post_md5()
except Exception as e:
  logging.info("Upload the native MD5 value to the proxy error: " + str(e))


def file_name(plugin_dir):
  list = []
  for root, dirs, files in os.walk(plugin_dir):
    for file in files:
      if os.path.splitext(file)[1] == '.py':
        list.append(file)
  return list


# 上报已安装的插件（后期把update相关的插件单独放到一个update的文件夹？）
def sendFileName():
  try:
    while True:
      requrl = "http://" + jifangip + "/umsproxy/autoProxyPlugIn/sendFileName"
      filenames = file_name(plugin_dir)
      #logging.info(filenames)
      name = {}
      allips = allip.get_all_ips()
      for item in allips:
        hip = allip.re_format_ip(item)
        out = allip.read_ip(hip)
        out.replace("\n", "")
        out.replace("\r", "")
        if out == "127.0.0.1":
          continue
        name = {"names":filenames}
        name["ip"] = out
        name = urllib.urlencode(name)
        logging.info("Upload ip and pluginName: " + str(name))
        try:
          req = urllib2.Request(url=requrl, data=name)
          res = urllib2.urlopen(req)
          data = res.read()
          agentrequrl = "http://" + jifangip + "/umsproxy/autoProxyPlugIn/checkAgentVersion"
          data = ""
          req = urllib2.Request(url=agentrequrl, data=data)
          res = urllib2.urlopen(req)
          result = res.read()
          logging.info("升级agent的时候获得的消息：" + str(result))
          # {"agentName":"agent.py","agentUrl":"/proxyDownLoad/agent.py","agentVersion":1,"name":"updateAgent"}
          NEW_VERSION = result["agentVersion"]
          if NEW_VERSION > VERSION:
            send_to_server = result
            udpsocket.sendto(send_to_server, address)
          udpsocket.close()
          logging.info("自升级给自己发送消息并关闭连接")
        except Exception as e:
          logging.info("Upload the machine IP and installed plugins to the proxy error: " + str(e))
        logging.info("Upload the machine IP and installed plugins to the proxy success: " + str(data))
      time.sleep(float(240))
  except Exception as e:
    logging.info("Upload the machine IP and installed plugins to the proxy error: " + str(e))
try:
  sendfilename = threading.Thread(target=sendFileName, args=())
  sendfilename.start()
except Exception as e:
  logging.info("Upload the machine IP and installed plugins to the proxy, thread error: " + str(e))


# 心跳，定期检查agent.lock存在否
def reportheart():
  try:
    while True:
      # 读文件，获得机房ip
      if os.path.exists("/home/opvis/Agent/agent.lock"):
        with open("/home/opvis/Agent/agent.lock", "r") as fd:
          jifangip = fd.read()
      else:
        logging.info("agent.lock not found!")
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
      try:
        req = urllib2.Request(url=requrl, data=ip)
        res = urllib2.urlopen(req)
        data = res.read()
      except Exception as e:
        logging.info("Report heart to proxy error: " + str(e))
      logging.info("Report heart to proxy success: " + str(data))
      # 在这里写检查agent主程序是否有更新，通过urllib去检查一个地址是否能连通，能，就自己给自己发一个udp消息，内容为agentupdate
      # agentupdate.py里面需要读取agent.lock文件重新拼接agent.py下载url
      # agentrequrl = "http://" + jifangip + "/umsproxy/autoProxyPlugIn/checkAgentVersion"
      # data = ""
      # req = urllib2.Request(url=agentrequrl, data=data)
      # res = urllib2.urlopen(req)
      # result = res.read()
      # logging.info("升级agent的时候获得的消息：" + str(result))
      # # {"agentName":"agent.py","agentUrl":"/proxyDownLoad/agent.py","agentVersion":1,"name":"updateAgent"}
      # NEW_VERSION = result["agentVersion"]
      # if NEW_VERSION > VERSION:
      #   send_to_server = result
      #   udpsocket.sendto(send_to_server, address)
      # udpsocket.close()
      time.sleep(float(240))
  except Exception as e:
    logging.info("Report heart to proxy error: " + str(e))
try:
  t = threading.Thread(target=reportheart, args=())
  t.daemon = True
  t.start()
except Exception as e:
  logging.info("Report heart to proxy error: " + str(e))


# 接收controller消息
def callplugin():
  cmd = "python /home/opvis/Agent/update/update.py" + " " + data2
  os.system(cmd)
while True:
  data, addr = udpsocket.recvfrom(2018)
  time_second = time.time()
  logging.info("Time of data received: " + str(time_second))
  logging.info("Receive data from proxy: " + str(data))
  # {"pluginfo":{"name":"topologic","status":1,"url":"http://10.124.5.163:18382/proxyDownLoad/topologic_v03.py","version":"03"},"tableName":"ZZ_HOST_RELATION20180808103501"}
  data1 = "{0}".format(data)
  lstr = "'''"
  rstr = "'''"
  data2 = lstr + data1 + rstr
  dic = json.loads(data)
  logging.info("Change data to dict: " + str(dic))
#{u'pluginfo': {u'status': 3, u'url': u'http://10.124.5.163:18382/proxyDownLoad/net_v03.py', u'version': u'03', u'name': u'net', u'cycle': u''}, u'hostid': 3902, u'plugid': 1}
  # {"agentName":"agent.py","agentUrl":"/proxyDownLoad/agent.py","agentVersion":1,"name":"updateAgent"}
  name = dic.get("name")
  if name == "updateAgent":
    break
  else:
    # 调用插件
    try:
      t = threading.Thread(target=callplugin, args=())
      t.daemon = True
      t.start()
    except Exception, e:
      logging.info("Call the plugin error: " + str(e))

# 自升级
udpsocket.close()
try:
  cmd = "python /home/opvis/Agent/update/agentupdate.py" + " " + data2
  ret = os.system(cmd)
except Exception as e:
  logging.info("Upgrade agent error: " + str(e))