#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/11 14:14
# @Author: yangjian
# @File  : update.py

import os
import sys
import json
import urllib
import urllib2
import logging
from logging.handlers import TimedRotatingFileHandler

# 定义日志格式、路径
LOG_FILE = "/home/opvis/Agent/log/update.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(LOG_FILE, when='D', interval=1, backupCount=30)
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = '%(asctime)s %(levelname)s %(message)s '
formatter = logging.Formatter(format_str, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)

plugin_dir = "/home/opvis/Agent/plugin/"
dirs = os.listdir(plugin_dir)
data = sys.argv[1:]
logging.info("Received data from proxy:" + str(data))
#['{"hostid":3902,"plugid":1,"pluginfo":{"cycle":"","name":"net","status":3,"url":"http://10.124.5.163:18382/proxyDownLoad/net_v03.py","version":"03"}}']
data1 = data[0]
data2 = json.loads(data1)
dic = data2["pluginfo"]
url = dic.get("url")
name = dic.get("name")
cycle = dic.get("cycle")
status = int(dic.get("status"))
file_name = url.split("/")[-1]

# 如果插件存在，只是执行插件，就用这个路径
plugin_dir1 = os.path.join(plugin_dir, file_name)
tmp_url = dic.get('url')

# 增删改查的接口
requrl = "http://" + tmp_url.split("/")[2] + "/umsproxy/autoProxyPlugIn/agentType"
requrl = str(requrl)

# 安装插件
# 这里改成判断两个id是否为空，为空就手动设置一个值
def installPlugin():
  # get_hostid = data2.get('hostid')
  # get_plugid = data2.get('plugid')
  # logging.info(get_hostid)
  # logging.info(get_plugid)
  logging.info("When install plugin, get hostid and plugid" + str(data2.get('hostid') + " " + data2.get('plugid')))

  try:

    if (file_name not in dirs):
      try:
        urllib.urlretrieve(url, os.path.join(plugin_dir, file_name))
        html = urllib.urlopen(url)
        html1 = html.read()
        code = html.code
        with open(os.path.join(plugin_dir, file_name), "wb") as fp:
          fp.write(html1)
      except Exception, e:
        logging.info("Install plugin, plugin not exists and download plugin failed: " + str(e))
      if code == 200:
        req_data = {}
        hostid = data2.get('hostid')
        plugid = data2.get('plugid')
        if not hostid and plugid:
          req_data['hostId'] = data2.get('hostid')
          req_data['plugId'] = data2.get('plugid')
        else:
          req_data['hostId'] = "9999"
          req_data['plugId'] = "9999"
        temp = os.popen('sudo python %s' % plugin_dir1).readlines()
        logging.info("Install plugin, plugin not exists, download and excute plugin successfully: " + str(file_name))
        req_data["type"] = "11"
        req_data["cause"] = "success"
        try:
          req_data = urllib.urlencode(req_data)
          req = urllib2.Request(url=requrl, data=req_data)
          res = urllib2.urlopen(req)
          data = res.read()
          logging.info("Interface feedback plugin installed successfully: " + str(data))
        except Exception as e:
          logging.info("Interface feedback plugin install failed: " +str(e))

        # HostRelationship
        try:
          url_new = "http://" + tmp_url.split("/")[2] + "/umsproxy/hostExtract/uploadHostInformation"
          url_new = str(url_new)
          hostRelationship = {}
          hostRelationship["tabName"] = data2.get("tableName")
          hostRelationship["hostRelationship"] = temp
          hostRelationship = json.dumps(hostRelationship)
          header_dict = {"Content-Type": "application/json;charset=UTF-8"}
          req = urllib2.Request(url=url_new, data=hostRelationship, headers=header_dict)
          res = urllib2.urlopen(req)
          logging.info("Interface feedback upload hostinformation successfully: " + str(res.read()))
        except Exception as e:
          logging.info("Interface feedback upload hostinformation failed:" + str(e))

      elif code != 200:
        req_data = {}
        hostid = data2.get('hostid')
        plugid = data2.get('plugid')
        if not hostid and plugid:
          req_data['hostId'] = data2.get('hostid')
          req_data['plugId'] = data2.get('plugid')
        else:
          req_data['hostId'] = "9999"
          req_data['plugId'] = "9999"
        req_data['type'] = '10'
        req_data['cause'] = "下载文件失败"
        try:
          req_data = urllib.urlencode(req_data)
          req = urllib2.Request(url=requrl, data=req_data)
          res = urllib2.urlopen(req)
          data = res.read()
          logging.info("Interface feedback install plugin, plugin not exists and download plugin failed:" + str(data))
        except Exception as e:
          logging.info("Interface feedback install plugin, plugin not exists and download plugin failed: " + str(file_name))

    else:
      temp = os.popen('sudo python %s' % plugin_dir1).readlines()
      req_data = {}
      hostid = data2.get('hostid')
      plugid = data2.get('plugid')
      if not hostid and plugid:
        req_data['hostId'] = data2.get('hostid')
        req_data['plugId'] = data2.get('plugid')
      else:
        req_data['hostId'] = "9999"
        req_data['plugId'] = "9999"
      req_data['type'] = '11'
      req_data['cause'] = 'success'
      try:
        req_data = urllib.urlencode(req_data)
        req = urllib2.Request(url=requrl, data=req_data)
        res = urllib2.urlopen(req)
        logging.info("Interface feedback install plugin, plugin exists and execute successfully." + str(file_name))
      except Exception as e:
        logging.info("Interface feedback install plugin, plugin exists and execute failed: " + str(e))

        # hostRelationship
      try:
        url_new = "http://" + tmp_url.split("/")[2] + "/umsproxy/hostExtract/uploadHostInformation"
        url_new = str(url_new)
        hostRelationship = {}
        hostRelationship["tabName"] = data2.get("tableName")
        hostRelationship["hostRelationship"] = temp
        hostRelationship = json.dumps(hostRelationship)
        header_dict = {"Content-Type": "application/json;charset=UTF-8"}
        req = urllib2.Request(url=url_new, data=hostRelationship, headers=header_dict)
        res = urllib2.urlopen(req)
        logging.info("Interface feedback upload hostinformation successfully: " + str(res.read()))
      except Exception as e:
        logging.info("Interface feedback upload hostinformation failed: " + str(e))

  # 出现异常，直接上报异常
  except Exception, e:
    logging.info("When install plugin, error:" + str(e))
    req_data = {}
    hostid = data2.get('hostid')
    plugid = data2.get('plugid')
    if not hostid and plugid:
      req_data['hostId'] = data2.get('hostid')
      req_data['plugId'] = data2.get('plugid')
    else:
      req_data['hostId'] = "9999"
      req_data['plugId'] = "9999"
    req_data["type"] = "10"
    req_data["cause"] = "系统异常"
    try:
      req_data = urllib.urlencode(req_data)
      req = urllib2.Request(url=requrl, data=req_data)
      res = urllib2.urlopen(req)
      data = res.read()
      logging.info("Interface feedback system error successfully: " + str(data))
    except Exception as e:
      logging.info("Interface feedback system error failed: " + str(e))


# 调用插件
def doPlugin():
  try:
    if (file_name not in dirs):
      try:
        urllib.urlretrieve(url, os.path.join(plugin_dir, file_name))
        html = urllib.urlopen(url)
        html1 = html.read()
        code = html.code
        with open(os.path.join(plugin_dir, file_name), "wb") as fp:
          fp.write(html1)
      except Exception, e:
        logging.info("Download plugin error: " + str(e))
      if code == 200:
        try:
          logging.info("Plugin not exists, download plugin successfully: " + str(file_name))
          logging.info("Period excute plugin: " + str(file_name) + str(cycle))
          cron_dir = "/home/opvis/Agent/cron/" + str(file_name.split(".")[0])
          f = open(cron_dir, "w")
          f.write("%s python %s\n" % (cycle, plugin_dir1))
          f.close()
          cron_cmd = "crontab" + " " + cron_dir
          cron_ret = os.system(cron_cmd)
          if cron_ret == 0:
            os.remove(cron_dir)
          req_data = {}
          req_data['hostId'] = data2.get('hostid')
          req_data['plugId'] = data2.get('plugid')
          req_data['type'] = '21'
          req_data['cause'] = 'success'
          req_data = urllib.urlencode(req_data)
          req = urllib2.Request(url=requrl, data=req_data)
          res = urllib2.urlopen(req)
          data = res.read()
          logging.info("Interface feedback doPlugin successfully: " + str(data))
        except Exception as e:
          logging.info("Plugin not exists, download plugin error: " + str(e))

      elif code != 200:
        logging.info("Plugin not exists, download plugin failed: " + str(file_name))
        try:
          req_data = {}
          req_data['hostId'] = data2.get('hostid')
          req_data['plugId'] = data2.get('plugid')
          req_data['type'] = '20'
          req_data['cause'] = "下载文件失败"
          req_data = urllib.urlencode(req_data)
          req = urllib2.Request(url=requrl, data=req_data)
          res = urllib2.urlopen(req)
          data = res.read()
          logging.info("Interface feedback successfully: " + str(data))
        except Exception as e:
          logging.info("Interface feedback plugin not exists, download plugin failed, error" + str(e))
    else:
      logging.info("Plugin not exists and doplugin: " + str(file_name))
      try:
        cron_dir = "/home/opvis/Agent/cron/" + str(file_name.split(".")[0])
        f = open(cron_dir, "w")
        f.write("%s python %s\n" % (cycle, plugin_dir1))
        f.close()
        cron_cmd = "crontab" + " " + cron_dir
        cron_ret = os.system(cron_cmd)
        if cron_ret == 0:
          os.remove(cron_dir)
        req_data = {}
        req_data['hostId'] = data2.get('hostid')
        req_data['plugId'] = data2.get('plugid')
        req_data['type'] = '21'
        req_data['cause'] = 'success'
        req_data = urllib.urlencode(req_data)
        req = urllib2.Request(url=requrl, data=req_data)
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("Interface feedback successfully: " + str(data))
      except Exception as e:
        logging.info("Interface feedback plugin not exists and doplugin, error: " + str(e))

  except Exception, e:
    logging.info("doPlugin error：" + str(e))
    try:
      req_data = {}
      req_data['hostId'] = data2.get('hostid')
      req_data['plugId'] = data2.get('plugid')
      req_data['type'] = '20'
      req_data['cause'] = str(e)
      req_data = urllib.urlencode(req_data)
      req = urllib2.Request(url=requrl, data=req_data)
      res = urllib2.urlopen(req)
      data = res.read()
      logging.info("Interface feedback successfully: " + str(data))
    except Exception as e:
      logging.info("Interface feedback doPlugin error: " + str(e))


# 更新插件
def updatePlugin():
  try:
    file_name = url.split("/")[-1]
    # logging.info(file_name)
    # logging.info(dirs)
    # for file_name in dirs:
    #  logging.info(plugin_dir + file_name)
    #  os.remove(plugin_dir + file_name)
    #  break
    # 下载新插件
    try:
      urllib.urlretrieve(url, os.path.join(plugin_dir, file_name))
      html = urllib.urlopen(url)
      html1 = html.read()
      code = html.code
      with open(os.path.join(plugin_dir, file_name), "wb") as fp:
        fp.write(html1)
        logging.info("UpdatePlugin, download plugin successfully.")
    except Exception, e:
      logging.info("UpdatePlugin, download plugin failed: " + str(e))
    if code == 200:
      logging.info("UpdatePlugin, successfully.")
      try:
        req_data = {}
        req_data['hostId'] = data2.get('hostid')
        req_data['plugId'] = data2.get('plugid')
        req_data['type'] = '31'
        req_data['cause'] = 'success'
        logging.info(req_data)
        req_data = urllib.urlencode(req_data)
        req = urllib2.Request(url=requrl, data=req_data)
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("Interface feedback, updatePlugin successfully: " + str(data))
      except Exception as e:
        logging.info("UpdatePlugin, failed: " + str(e))

  except Exception, e:
    try:
      req_data = {}
      req_data['hostId'] = data2.get('hostid')
      req_data['plugId'] = data2.get('plugid')
      req_data['type'] = '30'
      req_data['cause'] = str(e)
      req_data = urllib.urlencode(req_data)
      req = urllib2.Request(url=requrl, data=req_data)
      res = urllib2.urlopen(req)
      data = res.read()
      logging.info("Interface feedback, updatePlugin successfully: " + str(data))
    except Exception as e:
      logging.info("UpdatePlugin error: " + str(e))


# 保存插件
def savePlugin():
  file_name = url.split("/")[-1]
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
        logging.info("Saveplugin, plugin not exists, download plugin successfully: " + str(file_name))
        req_data = {}
        req_data['hostId'] = data2.get('hostid')
        req_data['plugId'] = data2.get('plugid')
        req_data['type'] = '41'
        req_data['cause'] = 'success'
        req_data = urllib.urlencode(req_data)
        req = urllib2.Request(url=requrl, data=req_data)
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("Interface feedback successfully: " + str(data))
    except Exception, e:
      try:
        req_data = {}
        req_data['hostId'] = data2.get('hostid')
        req_data['plugId'] = data2.get('plugid')
        req_data['type'] = '40'
        req_data['cause'] = str(e)
        req_data = urllib.urlencode(req_data)
        req = urllib2.Request(url=requrl, data=req_data)
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("Interface feedback successfully: " + str(data))
      except Exception as e:
        logging.info("Saveplugin error: " + str(e))


# 删除插件
def deletePlugin():
  for d in dirs:
    # logging.info("d和dirs的值")
    # logging.info(d)
    # logging.info(dirs)
    # logging.info(file_name)
    if d == file_name:
      os.remove(plugin_dir + d)
      req_data = {}
      req_data['hostId'] = data2.get('hostid')
      req_data['plugId'] = data2.get('plugid')
      req_data['type'] = '51'
      req_data['cause'] = 'success'
      try:
        req_data = urllib.urlencode(req_data)
        req = urllib2.Request(url=requrl, data=req_data)
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("Interface feedback successfully, deleteplugin: " + str(data))
      except Exception as e:
        logging.info("Deleteplugin error: " + str(e))

logging.info("Received status: " + str(status))

# 安装插件并执行一次
if status == 1 and url:
  try:
    installPlugin()
  except Exception as e:
    logging.info(e)

# 周期性执行插件
elif status == 2 and url and cycle:
  try:
    doPlugin()
  except Exception as e:
    logging.info(e)

# 更新插件
elif status == 3 and url:
  try:
    updatePlugin()
  except Exception as e:
    logging.info(e)

# 保存插件
elif status == 4 and url:
  try:
    savePlugin()
  except Exception as e:
    logging.info(e)

# 删除插件
elif status == 5 and url:
  try:
    deletePlugin()
  except Exception as e:
    logging.info(e)