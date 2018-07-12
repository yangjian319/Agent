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



# 判断本机属于哪个机房，并把机房ip写入本地文件中供插件上报使用
# 这个过程需要12s左右

iplist = ["172.30.130.137:18382", "172.30.130.126:18382", "10.124.5.163:18382", "10.144.2.248:18382", "10.123.30.177:18382", "172.30.194.121:18382", "172.16.5.20:18382", "10.181.1.0:18382"]
for ip in iplist:
  try:
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    so.settimeout(2)
    so.connect((ip.split(":")[0], 18382))
    currentip = ip
    with open("/tmp/agent.lock", "wb") as fd:
      fd.write(ip)
    so.close()
  except Exception:
    pass

# 机房ip
jifangip = currentip
hearturl = "http://47.106.106.220:5000/register"
plugin_dir = "/data/Agent/plugin/"

# 创建日志文件目录
logdir = "/data/Agent/log"
if not os.path.exists(logdir):
    os.makedirs(logdir)

# 建立UDP
address = ("0.0.0.0", 9998)
udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpsocket.bind(address)


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

# 安装好agent的时候就上传一次md5值入库
def post_md5():
  (status, md5) = commands.getstatusoutput("sudo md5sum /root/.ssh/authorized_keys|awk '{print $1}'")
  req_data = {}
  req_data['md5'] = md5
  args_restful = urllib.urlencode(req_data)
  req = urllib2.Request(url="http://" + jifangip + "/autoProxyPlugIn/uploadMD5", data=args_restful)
  res = urllib2.urlopen(req)
  data = res.read()
  #print(data)
post_md5()


def file_name(plugin_dir):
  L = []
  for root, dirs, files in os.walk(plugin_dir):
    for file in files:
      if os.path.splitext(file)[1] == '.py':
        L.append(file)
  return L

def sendFileName():
  while True:
    requrl = "http://" + jifangip + "/autoProxyPlugIn/sendFileName"
    names = file_name(plugin_dir)
    name = {"names": names}
    name = urllib.urlencode(name)
    req = urllib2.Request(url=requrl, data=name)
    res = urllib2.urlopen(req)
    data = res.read()
    print(data)
    time.sleep(float(240))
sendfilename = threading.Thread(target=sendFileName, args=())
sendfilename.start()

# 心跳部分
# 上传主机的ip
# 定期检查agent.lock是否存在【未写】
def func():
  while True:
    # 读文件，获得机房ip
    with open("/tmp/agent.lock", "r") as fd:
      jifangip = fd.read()

    ips = allip.get_all_ips()
    # {'ip': ['10.124.2.46', '10.148.138.133']}
    data = json.dumps(ips)
    headers = {"Content-Type": "application/json"}
    url_base1 = "http://" + jifangip + "/autoProxyPlugIn/sendIp"
    # 添加日志
    req = urllib2.Request(url=url_base1, headers=headers, data=data.encode())
    res = urllib2.urlopen(req)
    data = res.read()
    logging.info(data)
    time.sleep(float(240))
t = threading.Thread(target=func, args=())
t.daemon = True
try:
  t.start()
except Exception, e:
  logging.info(e)


# 接收controller消息
'''
{u'status': 5, u'hostId': 3902, u'name': u'net', u'url': u'http://10.124.5.163:18382/proxyDownLoad/net_v03.py', u'plugId': 1, u'version': u'03', u'cycle': u''}
'''
while True:
  data, addr = udpsocket.recvfrom(2018)
  dic = json.loads(data)
  logging.info(dic)
  name = dic.get("name") # 这里的name需要proxy那边改成pluginName更好看
  if name == "agentupdate":
    break
  else:
    # 调用插件
    # 插件的增删改查统一由update.py去处理，update.py接收多个参数
    def func():
      cmd = "python /data/Agent/plugin/update.py" + " " + dic
      ret = os.system(cmd)
    t = threading.Thread(target=func, args=())
    t.daemon = True
    try:
      t.start()
    except Exception, e:
      logging.info(e)

# 自升级
udpsocket.close()
ret = os.system("python /data/Agent/plugin/agentupdate.py")
sys.exit(0)

