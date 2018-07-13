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
import urllib2
from logging.handlers import TimedRotatingFileHandler



# 定义日志格式、路径
LOG_FILE = "/data/Agent/log/update.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(LOG_FILE, when='D', interval=1, backupCount=30)
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = '%(asctime)s %(levelname)s %(message)s '
formatter = logging.Formatter(format_str, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)



plugin_dir = "/data/Agent/plugin/"
dirs = os.listdir(plugin_dir) # 【这里需要以.py取出名字部分，因为udpsocket接收到的name是没有.py的】
dic = sys.argv[1:]
url = dic.get("url")
name = dic.get("name") # 这里的name可能需要proxy那边改成pluginName
cycle = dic.get("cycle")
status = int(dic.get("status"))
file_name = url.split("/")[-1]

# 如果插件存在，只是执行插件，就用这个路径
plugin_dir1 = os.path.join(plugin_dir, file_name)
req_data = {}
req_data["hostId"] = dic.get("hostId")
req_data["plugId"] = dic.get("plugId")
tmp_url = dic.get('url')

# 增删改查的接口
requrl = "http://" + tmp_url.split("/")[2] + "/umsproxy/autoProxyPlugIn/agentType"

# 安装插件
def installPlugin():
  req_data = {}
  req_data["hostId"] = dic.get("hostId")
  req_data["plugId"] = dic.get("plugId")
  try:

    if (file_name not in dirs):
      urllib.urlretrieve(url, os.path.join(plugin_dir,file_name))
      html = urllib.urlopen(url)
      html1 = html.read()
      code = html.code
      try:
        with open(os.path.join(plugin_dir,file_name), "wb") as fp:
          fp.write(html1)
      except Exception, e:
        logging.info(e)
      if code == 200:
        logging.info("插件不存在，插件下载成功：" + str(file_name))
        temp = os.popen('sudo python %s' % plugin_dir1).readlines()
        logging.info("插件执行结果：" + str(temp))
        req_data["type"] = "11"
        req_data["cause"] = "success"
        req_data["url"] = requrl
        req_data = json.dumps(req_data)
        args_restful = urllib.urlencode(req_data)
        req = urllib2.Request(url=url, data=args_restful)
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("插件执行结果：" + str(data))

      elif code != 200:
        logging.info("插件不存在，并且插件下载失败：" + str(file_name))
        req_data['type'] = '10'
        req_data['cause'] = "下载文件失败"
        req_data["url"] = requrl
        req_data = json.dumps(req_data)
        args_restful = urllib.urlencode(req_data)
        req = urllib2.Request(url=url, data=args_restful)
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("插件执行结果：" + str(data))

    else:
      logging.info("插件存在，直接执行插件：" + str(file_name))
      temp = os.popen('sudo python %s' % plugin_dir1).readlines()
      logging.info("插件执行结果：" + str(temp))
      req_data['type'] = '11'
      req_data['cause'] = 'success'
      req_data["url"] = requrl
      req_data = json.dumps(req_data)
      args_restful = urllib.urlencode(req_data)
      req = urllib2.Request(url=url, data=args_restful)
      res = urllib2.urlopen(req)
      data = res.read()
      logging.info("插件执行结果：" + str(data))
      # post_msg.post_proxy(status, url_base1, req_data)
      # post_msg.post_proxy_status1(status, url_base1, temp)

  # 出现异常，直接上报异常
  except Exception, e:
    logging.info("安装插件出现异常：" + str(e))
    req_data['type'] = '10'
    req_data['cause'] = "系统异常"
    req_data["url"] = requrl
    req_data = json.dumps(req_data)
    args_restful = urllib.urlencode(req_data)
    req = urllib2.Request(url=url, data=args_restful)
    res = urllib2.urlopen(req)
    data = res.read()
    logging.info("插件执行结果：" + str(data))


# 调用插件
def doPlugin():
  req_data = {}
  req_data["hostId"] = dic.get("hostId")
  req_data["plugId"] = dic.get("plugId")
  try:
    if (file_name not in dirs):
      urllib.urlretrieve(url, os.path.join(plugin_dir,file_name))  # 直接覆盖？
      html = urllib.urlopen(url)
      html1 = html.read()
      code = html.code
      try:
        with open(os.path.join(plugin_dir,file_name), "wb") as fp:
          fp.write(html1)
      except Exception, e:
        logging.info(e)
      if code == 200:
        logging.info("插件不存在，插件下载成功：" + str(file_name))
        logging.info("周期执行插件：" + str(file_name) + str(cycle))
        f = open("/etc/crontab", "a+")  # type:file
        f.write("%s root python %s" % (cycle, plugin_dir1))
        f.close()
        req_data['type'] = '21'
        req_data['cause'] = 'success'
        req_data["url"] = requrl
        req_data = json.dumps(req_data)
        args_restful = urllib.urlencode(req_data)
        req = urllib2.Request(url=url, data=args_restful)
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("插件执行结果：" + str(data))

      elif code != 200:
        logging.info("插件不存在，并且插件下载失败：" + str(file_name))
        req_data['type'] = '20'
        req_data['cause'] = "下载文件失败"
        req_data["url"] = requrl
        req_data = json.dumps(req_data)
        args_restful = urllib.urlencode(req_data)
        req = urllib2.Request(url=url, data=args_restful)
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("插件执行结果：" + str(data))

    else:
      logging.info("插件存在，直接执行插件：" + str(file_name))
      f = open("/etc/crontab", "a+")
      f.write("%s root python %s" % (cycle, plugin_dir1))
      f.close()
      req_data['type'] = '21'
      req_data['cause'] = 'success'
      req_data["url"] = requrl
      req_data = json.dumps(req_data)
      args_restful = urllib.urlencode(req_data)
      req = urllib2.Request(url=url, data=args_restful)
      res = urllib2.urlopen(req)
      data = res.read()
      logging.info("插件执行结果：" + str(data))

  except Exception, e:
    logging.info("安装插件出现异常：" + str(e))
    req_data['type'] = '20'
    req_data['cause'] = str(e)
    req_data["url"] = requrl
    req_data = json.dumps(req_data)
    args_restful = urllib.urlencode(req_data)
    req = urllib2.Request(url=url, data=args_restful)
    res = urllib2.urlopen(req)
    data = res.read()
    logging.info("插件执行结果：" + str(data))


# 更新插件
def updatePlugin():
  # 需要统一一下插件名格式
  # url = "http://172.30.130.244:8380/download/net_v07.py"
  req_data = {}
  req_data["hostId"] = dic.get("hostId")
  req_data["plugId"] = dic.get("plugId")
  try:
    for file_name in dirs:
      os.remove(plugin_dir + file_name)
      break
    # 下载新插件
    urllib.urlretrieve(url, os.path.join(plugin_dir, file_name))  # 直接覆盖？
    html = urllib.urlopen(url)
    html1 = html.read()
    code = html.code
    try:
      with open(os.path.join(plugin_dir, file_name), "wb") as fp:
        fp.write(html1)
    except Exception, e:
      logging.info(e)
    if code == 200:
      logging.info("更新插件成功")
      req_data['type'] = '31'
      req_data['cause'] = 'success'
      req_data["url"] = requrl
      req_data = json.dumps(req_data)
      args_restful = urllib.urlencode(req_data)
      req = urllib2.Request(url=url, data=args_restful)
      res = urllib2.urlopen(req)
      data = res.read()
      logging.info("插件执行结果：" + str(data))

  except Exception, e:
    req_data['type'] = '30'
    req_data['cause'] = str(e)
    req_data["url"] = requrl
    req_data = json.dumps(req_data)
    args_restful = urllib.urlencode(req_data)
    req = urllib2.Request(url=url, data=args_restful)
    res = urllib2.urlopen(req)
    data = res.read()
    logging.info("插件执行结果：" + str(data))

# 保存插件
def savePlugin():
  req_data = {}
  req_data["hostId"] = dic.get("hostId")
  req_data["plugId"] = dic.get("plugId")
  if (file_name not in dirs):
    try:
      urllib.urlretrieve(url, os.path.join(plugin_dir, file_name))  # 直接覆盖？
      html = urllib.urlopen(url)
      html1 = html.read()
      code = html.code
      try:
        with open(os.path.join(plugin_dir, file_name), "wb") as fp:
          fp.write(html1)
      except Exception, e:
        logging.info(e)
      if code == 200:
        logging.info("插件不存在，插件下载成功：" + str(file_name))
        req_data['type'] = '41'
        req_data['cause'] = 'success'
        req_data["url"] = requrl
        req_data = json.dumps(req_data)
        args_restful = urllib.urlencode(req_data)
        req = urllib2.Request(url=url, data=args_restful)
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("插件执行结果：" + str(data))
    except Exception, e:
      req_data['type'] = '40'
      req_data['cause'] = str(e)
      req_data["url"] = requrl
      req_data = json.dumps(req_data)
      args_restful = urllib.urlencode(req_data)
      req = urllib2.Request(url=url, data=args_restful)
      res = urllib2.urlopen(req)
      data = res.read()
      logging.info("插件执行结果：" + str(data))

# 删除插件
def deletePlugin():
  for d in dirs:
    if d == file_name:
      os.remove(plugin_dir + d)
      req_data['type'] = '51'
      req_data['cause'] = 'success'
      req_data["url"] = requrl
      req_data = json.dumps(req_data)
      args_restful = urllib.urlencode(req_data)
      req = urllib2.Request(url=url, data=args_restful)
      res = urllib2.urlopen(req)
      data = res.read()
      logging.info("插件执行结果：" + str(data))



# 安装插件并执行一次
if status == 1 and url:
  installPlugin()

# 周期性执行插件
elif status == 2 and url and cycle:
  doPlugin()

# 更新插件
elif status == 3 and url:
  updatePlugin()

# 保存插件
elif status == 4 and url:
  savePlugin()

# 删除插件
elif status == 5 and url:
  deletePlugin()


