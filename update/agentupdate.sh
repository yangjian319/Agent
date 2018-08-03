#!/bin/bash
date=`date +%Y%m%d`
mv /home/opvis/Agent/agent.py /home/opvis/Agent/agent.py.$date
cp /home/opvis/Agent/temp/agent.py /home/opvis/Agent/
ps aux|grep agent.py|grep -v grep|awk '{print $2}'|xargs kill -9
python /home/opvis/Agent/agent.py