#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/9 9:13
# @Author: yangjian
# @File  : deleteLog.py

'''
删除7天前的日志，写成定时任务
'''
import os
import time
import datetime

def del_log(logdir):
  for parent, dirnames, filenames in os.walk(logdir):
          for filename in filenames:
            fullname = parent + "/" + filename #文件全称
            createTime = int(os.path.getctime(fullname)) #文件创建时间
            nDayAgo = (datetime.datetime.now() - datetime.timedelta(days = 7)) #当前时间的n天前的时间
            timeStamp = int(time.mktime(nDayAgo.timetuple()))
            if createTime < timeStamp: #创建时间在n天前的文件删除
              os.remove(os.path.join(parent,filename))

#del_log(logdir)