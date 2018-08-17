#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/4/28 8:59
# @Author: yangjian
# @File  : plug_v1.py
import ConfigParser
import logging
import os
import sys
import json
import urllib
import commands
import urllib2
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# log
LOG_FILE = "/home/opvis/opvis_agent/agent_service/log/update.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(LOG_FILE, when='D', interval=1, backupCount=30)
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = '%(asctime)s %(levelname)s %(message)s '
formatter = logging.Formatter(format_str, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)

def monitor():
    with open("/home/opvis/opvis_agent/agent_service/agent.lock", "r") as fd:
        jifangip = fd.read()
    url_base = "http://" + jifangip
    # 获取authorized——keys的md5值
    get_md5_url = url_base + "/hostPlugInOperation/getHostTrustRelationshipMD5"
    print(get_md5_url)
    # 上报返回结果
    upload_status_url = url_base + "/hostPlugInOperation/uploadOperationMD5Information"
    print(upload_status_url)
    headers = {"Content-Type": "application/json"}
    data = urllib.urlopen(get_md5_url).read()
    logging.info(data)
    md5_server = json.loads(data)["message"]
    logging.info(md5_server)

    ssh_path = "/root/.ssh"
    authorized_keys_path = "/root/.ssh/authorized_keys"
    ssh_path_mode = commands.getoutput('''ls -la /root|grep ".ssh"''').split(" ")[0]
    authorized_keys_mode = commands.getoutput("ls -l /root/.ssh/authorized_keys |awk '{print $1}'")
    authorized_keys_md5 = commands.getoutput("md5sum /root/.ssh/authorized_keys|awk '{print $1}'")

    requrl = url_base + "/hostPlugInOperation/uploadPlugLog"
    plug_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {}
    data["plug_name"] = sys.argv[0].split("/")[-1]
    data["plug_time"] = plug_time
    data["plug_status"] = "0"
    # 将dict转换成json格式
    data = json.dumps(data)
    headers = {"Content-Type": "application/json"}
    req = urllib2.Request(url=requrl, headers=headers, data=data.encode())
    response = urllib2.urlopen(req)
    result = response.read()
    logging.info("Interface feedback successfully: " + str(result))

    if not os.path.exists(ssh_path):
        logging.info("ssh目录不存在！")
        data={}
        data["plug_status"] = "1"
        data=json.dumps(data)
        req = urllib2.Request(url=upload_status_url, headers=headers, data=data.encode())
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("Interface feedback successfully: " + str(data))
        sys.exit(1)
    elif ssh_path_mode != "drwx------":
        logging.info("ssh目录的权限不是700！")
        data={}
        data["plug_status"] = "2"
        data=json.dumps(data)
        req = urllib2.Request(url=upload_status_url, headers=headers, data=data.encode())
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("Interface feedback successfully: " + str(data))
        sys.exit(1)
    elif not os.path.exists(authorized_keys_path):
        logging.info("authorized_keys文件不存在！")
        data={}
        data["plug_status"] = "3"
        data=json.dumps(data)
        req = urllib2.Request(url=upload_status_url, headers=headers, data=data.encode())
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("Interface feedback successfully: " + str(data))
        sys.exit(1)
    elif authorized_keys_mode != "-rw-------":
        logging.info("authorized_keys的权限不是600！")
        data={}
        data["plug_status"] = "4"
        data=json.dumps(data)
        req = urllib2.Request(url=upload_status_url, headers=headers, data=data.encode())
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("Interface feedback successfully: " + str(data))
        sys.exit(1)
    elif authorized_keys_md5 != md5_server:
        logging.info("authorized_keys的md5值和系统预设的不一致！")
        data={}
        data["plug_status"] = "5"
        data=json.dumps(data)
        req = urllib2.Request(url=upload_status_url, headers=headers, data=data.encode())
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("Interface feedback successfully: " + str(data))
        sys.exit(1)
    else:
        logging.info("一切正常！")
        data={}
        data["plug_status"] = "0"
        data=json.dumps(data)
        req = urllib2.Request(url=upload_status_url, headers=headers, data=data.encode())
        res = urllib2.urlopen(req)
        data = res.read()
        logging.info("Interface feedback successfully: " + str(data))
        sys.exit(1)

if __name__ == "__main__":
    try:
        monitor()
    except Exception as e:
        print(e)

