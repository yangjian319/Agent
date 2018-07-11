#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/11 14:14
# @Author: yangjian
# @File  : update.py
import json
import logging
import os
import sys
import urllib
from logging.handlers import TimedRotatingFileHandler

# 日志

LOG_FILE = "/data/Agent/log/update.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(LOG_FILE,when='D',interval=1,backupCount=30)
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = '%(asctime)s %(levelname)s %(message)s '
formatter = logging.Formatter(format_str, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)


plugin_dir = "/data/Agent/plugin/"
dirs = os.listdir(plugin_dir)
dic = sys.argv[1:]
# {u'status': 5, u'hostId': 3902, u'name': u'net', u'url': u'http://10.124.5.163:18382/proxyDownLoad/net_v03.py', u'plugId': 1, u'version': u'03', u'cycle': u''}
name = dic.get("name") # 这里的name需要proxy那边改成pluginName
status = int(dic.get("status"))
url = dic.get("url")
cycle = dic.get("cycle")
dirs = os.listdir(plugin_dir)
req_data = {}
req_data["hostId"] = dic.get("hostId")
req_data["plugId"] = dic.get("plugId")
tmp_url = dic.get('url')

if tmp_url is None:
  pass
url_base = 'http://' + tmp_url.split("/")[2]
# 增删改查的接口
url_install = "http://" + tmp_url.split("/")[2] + "/umsproxy/autoProxyPlugIn/agentType"
# url_base1 = http://10.124.5.163:18382

if status == 1 and url:
  file_name = url.split("/")[-1]
  print(file_name)
  plugin_dir = "%s%s" % (plugin_dir, file_name)

  try:

    if (file_name not in dirs):
      urllib.urlretrieve(url, os.path.join(plugin_dir,file_name))  # 直接覆盖？
      html = urllib.urlopen(url)
      html1 = html.read()
      code = html.code
      with open(os.path.join(plugin_dir,file_name), "wb") as fp:
        fp.write(html1)
      # logging.info("下载脚本文件状态：" + str(sta))
      if code == 200:
        # logging.info("执行脚本文件:" + plugin_dir)
        temp = os.popen('sudo python %s' % plugin_dir).readlines()
        # print temp
        req_data["type"] = "11"
        req_data["cause"] = "success"
        req_data["url"] = url_install
        req_data = json.dumps(req_data)
        cmd = "python /data/Agent/plugin/installplugin.py" + " " + req_data
        os.system(cmd)

      # elif code != 200:
      #   print "in sta != 0 branch"
      #   req_data['type'] = '10'
      #   req_data['cause'] = "下载文件失败"
#         post_msg.post_proxy(status, url_base1, req_data)
#
#     else:
#       # logging.info("执行脚本文件:" + plugin_dir)
#       temp = os.popen('sudo python %s' % plugin_dir).readlines()
#       # print temp
#       req_data['type'] = '11'
#       req_data['cause'] = 'success'
#       post_msg.post_proxy(status, url_base1, req_data)
#       post_msg.post_proxy_status1(status, url_base1, temp)
#
  except Exception, e:
    print "in exception branch"
#     req_data['type'] = '10'
#     print e
#     req_data['cause'] = "系统异常"
#     post_msg.post_proxy(status, url_base1, req_data)
#
# elif status == 2 and url and cycle:
#   # 周期性执行
#   file_name = url.split("/")[-1]
#   print file_name
#   plugin_dir = "%s%s" % (agent_home_dic, file_name)
#
#   try:
#
#     if (file_name not in dirs):
#       sta = os.system('wget %s -O %s' % (url, plugin_dir))
#       # logging.info("下载脚本文件状态：" + str(sta))
#       if sta == 0:
#         # logging.info("执行脚本文件:" + plugin_dir)
#         f = open("/etc/crontab", "a+")  # type:file
#         f.write("%s root python %s >> /home/opvis/opvis_agent/agent_service/out.log" % (
#           cycle, plugin_dir))
#         f.close()
#         req_data['type'] = '21'
#         req_data['cause'] = 'success'
#         post_msg.post_proxy(status, url_base1, req_data)
#       else:
#         req_data['type'] = '20'
#         req_data['cause'] = '下载文件失败'
#         post_msg.post_proxy(status, url_base1, req_data)
#     else:
#       # logging.info("执行脚本文件:" + plugin_dir)
#       f = open("/etc/crontab", "a+")  # type:file
#       f.write("%s root python %s" % (cycle, plugin_dir))
#       f.close()
#       req_data['type'] = '21'
#       req_data['cause'] = 'success'
#       post_msg.post_proxy(status, url_base1, req_data)
#
#   except Exception, e:
#     req_data['type'] = '20'
#     req_data['cause'] = str(e)
#     post_msg.post_proxy(status, url_base1, req_data)
#
# elif status == 3 and url:
#   # 更新脚本  已经验证可行
#   # url = "http://172.30.130.244:8380/download/net_v07.py"
#   file_name = url.split("/")[-1]  # type:str
#   print file_name
#   print url
#   li = file_name.split("_")  # type:list
#   # rint str(dics)
#   print li
#   try:
#     for fi in dirs:
#       if li[0] in fi:
#         os.remove(agent_home_dic + fi)
#         break
#     plugin_dir = "%s%s" % (agent_home_dic, file_name)
#     print plugin_dir
#     sta = os.system('wget %s -O %s' % (url, plugin_dir))
#     # logging.info("更新插件的状态：%s" % sta)
#     print sta
#     req_data['type'] = '31'
#     req_data['cause'] = 'success'
#     post_msg.post_proxy(status, url_base1, req_data)
#
#   except Exception, e:
#     req_data['type'] = '30'
#     req_data['cause'] = str(e)
#     post_msg.post_proxy(status, url_base1, req_data)
#
#
# elif status == 4 and url:  # 保存插件
#   file_name = url.split("/")[-1]  # type:str
#   print file_name
#   if (file_name not in dirs):
#     try:
#       plugin_dir = "%s%s" % (agent_home_dic, file_name)
#       sta = os.system('wget %s -O %s' % (url, plugin_dir))
#       req_data['type'] = '41'
#       req_data['cause'] = 'success'
#       post_msg.post_proxy(status, url_base1, req_data)
#     except Exception, e:
#       req_data['type'] = '40'
#       req_data['cause'] = str(e)
#       post_msg.post_proxy(status, url_base1, req_data)
#     # logging.info("保存插件的状态：%s" % sta)
# elif status == 5 and url:
#   # 删除插件
#   file_name = url.split("/")[-1]
#   print file_name
#   for d in dirs:
#     if d == file_name:
#       os.remove(agent_home_dic + d)
#       req_data['type'] = '51'
#       req_data['cause'] = 'success'
#       post_msg.post_proxy(status, url_base1, req_data)