#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/24 20:19
# @Author: yangjian
# @File  : client.py

import socket

'''
客户端使用UDP时，首先仍然创建基于UDP的Socket，然后，不需要调用connect()，直接通过sendto()给服务器发数据：
'''
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for data in ['a', 'b', 'c']:
  # 发送数据:
  s.sendto(data, ('127.0.0.1', 9999))
  # 接收数据:
  print s.recv(1024)
s.close()