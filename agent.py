#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/4 9:25
# @Author: yangjian
# @File  : agent.py

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
import json
import logging
import socket
import threading
import urllib
import urllib2
import time
import os
import sys
from logging.handlers import TimedRotatingFileHandler


# 判断本机属于哪个机房，并把机房ip写入本地文件中供插件上报使用
# 这个过程需要15s左右，至少需要8s
iplist = ["172.30.130.137:18382", "172.30.130.126:18382", "10.124.5.163:18382", "10.144.2.248:18382", "10.123.30.177:18382", "172.30.194.121:18382", "172.16.5.20:18382", "10.181.1.0:18382"]

for ip in iplist:
  cmd = "curl -m 2 -s -o /dev/null" + " " + ip
  is_ok = os.system(cmd)
  if is_ok == 0:
    currentip = ip
    with open("/tmp/agent.lock","wb") as fd:  # 【具体写到哪个目录待确定】
      fd.write(ip)

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


# 心跳部分
# 上传主机的ip
# 定期检查agent.lock是否存在【未写】
def func():
  while True:
    cmd = "python /data/Agent/plugin/reportheart.py"
    os.system(cmd)
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
  #url_base1 = 'http://' + tmp_url.split("/")[2]
  # url_base1 = http://10.124.5.163:18382
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

