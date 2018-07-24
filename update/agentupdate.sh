#!/bin/bash
date=`date +%Y%m%d`
mv /data/Agent/agent.py /data/Agent/agent.py+$date
cp /data/Agent/temp/agent.py /data/Agent/
ps aux|grep agent.py|grep -v grep|awk '{print $2}'|xargs kill -9
python /data/Agent/agent.py