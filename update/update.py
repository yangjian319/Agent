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
logging.info("接收到的udp信息")
#['{"hostid":3902,"plugid":1,"pluginfo":{"cycle":"","name":"net","status":3,"url":"http://10.124.5.163:18382/proxyDownLoad/net_v03.py","version":"03"}}']
logging.info(data)
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
  get_hostid = data2.get('hostid')
  get_plugid = data2.get('plugid')
  logging.info("安装的时候获取两个id")
  logging.info(get_hostid)
  logging.info(get_plugid)
  try:

    if (file_name not in dirs):
      urllib.urlretrieve(url, os.path.join(plugin_dir, file_name))
      html = urllib.urlopen(url)
      html1 = html.read()
      code = html.code
      try:
        with open(os.path.join(plugin_dir, file_name), "wb") as fp:
          fp.write(html1)
          logging.info("插件下载成功")
      except Exception, e:
        logging.info(e)
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
        logging.info("下载安装插件")
        logging.info(req_data)
        logging.info("插件不存在，插件下载成功：" + str(file_name))
        temp = os.popen('sudo python %s' % plugin_dir1).readlines()
        req_data["type"] = "11"
        req_data["cause"] = "success"
        req_data = urllib.urlencode(req_data)
        logging.info(req_data)
        req = urllib2.Request(url=requrl, data=req_data)
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("插件安装成功200")
        logging.info("安装插件执行结果：" + str(data))
        # hostRelationship
        url_new = "http://" + tmp_url.split("/")[2] + "/umsproxy/hostExtract/uploadHostInformation"
        url_new = str(url_new)
        hostRelationship = {}
        hostRelationship["hostRelationship"] = temp
        hostRelationship = json.dumps(hostRelationship)
        header_dict = {"Content-Type": "application/json;charset=UTF-8"}
        req = urllib2.Request(url=url_new, data=hostRelationship, headers=header_dict)
        res = urllib2.urlopen(req)
        logging.info("主机关系")
        logging.info(res.read())


      elif code != 200:
        logging.info("插件不存在，并且插件下载失败：" + str(file_name))
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
        req_data = urllib.urlencode(req_data)
        req = urllib2.Request(url=requrl, data=req_data)
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("安装插件执行结果：" + str(data))

    else:
      logging.info("插件存在，直接执行插件：" + str(file_name))
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
      req_data = urllib.urlencode(req_data)
      req = urllib2.Request(url=requrl, data=req_data)
      res = urllib2.urlopen(req)
      if res:
        logging.info("安装插件执行结果：成功")
      # hostRelationship
      url_new = "http://" + tmp_url.split("/")[2] + "/umsproxy/hostExtract/uploadHostInformation"
      url_new = str(url_new)
      hostRelationship = {}
      hostRelationship["hostRelationship"] = temp
      hostRelationship = json.dumps(hostRelationship)
      header_dict = {"Content-Type": "application/json;charset=UTF-8"}
      req = urllib2.Request(url=url_new, data=hostRelationship, headers=header_dict)
      res = urllib2.urlopen(req)
      logging.info(res.read())


  # 出现异常，直接上报异常
  except Exception, e:
    logging.info("安装插件出现异常：" + str(e))
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
    req_data = urllib.urlencode(req_data)
    req = urllib2.Request(url=requrl, data=req_data)
    res = urllib2.urlopen(req)
    data = res.read()
    logging.info("安装插件执行结果：" + str(data))


# 调用插件
def doPlugin():
  try:
    if (file_name not in dirs):
      urllib.urlretrieve(url, os.path.join(plugin_dir, file_name))
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
        logging.info("周期执行插件：" + str(file_name) + str(cycle))
        cron_dir = "/home/opvis/Agent/cron/" + str(file_name.split(".")[0])
        f = open(cron_dir, "w")
        f.write("%s root python %s" % (cycle, plugin_dir1))
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
        logging.info("调用插件执行结果：" + str(data))

      elif code != 200:
        logging.info("插件不存在，并且插件下载失败：" + str(file_name))
        req_data = {}
        req_data['hostId'] = data2.get('hostid')
        req_data['plugId'] = data2.get('plugid')
        req_data['type'] = '20'
        req_data['cause'] = "下载文件失败"
        req_data = urllib.urlencode(req_data)
        req = urllib2.Request(url=requrl, data=req_data)
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("调用插件执行结果：" + str(data))

    else:
      logging.info("插件存在，直接执行插件：" + str(file_name))
      cron_dir = "/home/opvis/Agent/cron/" + str(file_name.split(".")[0])
      f = open(cron_dir, "w")
      # f = open("/etc/crontab", "a+")  # type:file
      f.write("%s root python %s" % (cycle, plugin_dir1))
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
      logging.info("插件执行结果：" + str(data))

  except Exception, e:
    logging.info("安装插件出现异常：" + str(e))
    req_data = {}
    req_data['hostId'] = data2.get('hostid')
    req_data['plugId'] = data2.get('plugid')
    req_data['type'] = '20'
    req_data['cause'] = str(e)
    req_data = urllib.urlencode(req_data)
    req = urllib2.Request(url=requrl, data=req_data)
    res = urllib2.urlopen(req)
    data = res.read()
    logging.info("插件执行结果：" + str(data))


# 更新插件
def updatePlugin():
  try:
    file_name = url.split("/")[-1]
    logging.info(file_name)
    logging.info(dirs)
    # for file_name in dirs:
    #  logging.info(plugin_dir + file_name)
    #  os.remove(plugin_dir + file_name)
    #  break
    # 下载新插件
    urllib.urlretrieve(url, os.path.join(plugin_dir, file_name))
    html = urllib.urlopen(url)
    html1 = html.read()
    code = html.code
    try:
      with open(os.path.join(plugin_dir, file_name), "wb") as fp:
        fp.write(html1)
        logging.info("下载插件完成")
    except Exception, e:
      logging.info(e)
    if code == 200:
      logging.info("更新插件成功")
      req_data = {}
      req_data['hostId'] = data2.get('hostid')
      req_data['plugId'] = data2.get('plugid')
      req_data['type'] = '31'
      req_data['cause'] = 'success'
      logging.info("更新的时候的req_data")
      logging.info(req_data)
      req_data = urllib.urlencode(req_data)
      req = urllib2.Request(url=requrl, data=req_data)
      res = urllib2.urlopen(req)
      data = res.read()
      logging.info("更新插件执行结果：" + str(data))

  except Exception, e:
    req_data = {}
    req_data['hostId'] = data2.get('hostid')
    req_data['plugId'] = data2.get('plugid')
    req_data['type'] = '30'
    req_data['cause'] = str(e)
    req_data = urllib.urlencode(req_data)
    req = urllib2.Request(url=requrl, data=req_data)
    res = urllib2.urlopen(req)
    data = res.read()
    logging.info("更新插件执行结果：" + str(data))


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
        logging.info("插件不存在，插件下载成功：" + str(file_name))
        req_data = {}
        req_data['hostId'] = data2.get('hostid')
        req_data['plugId'] = data2.get('plugid')
        req_data['type'] = '41'
        req_data['cause'] = 'success'
        req_data = urllib.urlencode(req_data)
        req = urllib2.Request(url=requrl, data=req_data)
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("插件执行结果：" + str(data))
    except Exception, e:
      req_data = {}
      req_data['hostId'] = data2.get('hostid')
      req_data['plugId'] = data2.get('plugid')
      req_data['type'] = '40'
      req_data['cause'] = str(e)
      req_data = urllib.urlencode(req_data)
      req = urllib2.Request(url=requrl, data=req_data)
      res = urllib2.urlopen(req)
      data = res.read()
      logging.info("保存插件执行结果：" + str(data))


# 删除插件
def deletePlugin():
  for d in dirs:
    if d == file_name:
      os.remove(plugin_dir + d)

      req_data = {}
      req_data['hostId'] = data2.get('hostid')
      req_data['plugId'] = data2.get('plugid')
      req_data['type'] = '51'
      req_data['cause'] = 'success'
      logging.info("删除插件")
      logging.info(req_data)
      req_data = urllib.urlencode(req_data)
      req = urllib2.Request(url=requrl, data=req_data)
      res = urllib2.urlopen(req)
      data = res.read()
      logging.info("删除插件执行结果：" + str(data))

logging.info("获取到的status：")
logging.info(status)
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