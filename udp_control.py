#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2018/7/4 13:43
# @Author: yangjian
# @File  : udp_control.py

import socket

address = ('127.0.0.1', 9998)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
  msg = raw_input()
  if not msg:
    break
  s.sendto(msg, address)
s.close()


