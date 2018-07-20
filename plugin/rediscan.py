#!/usr/bin/env python
import sys,os,socket,urllib,urllib2,random,time
taskid = sys.argv[1].rstrip('\n')
hostname = socket.gethostname()
os.system("/usr/bin/sudo /bin/sh /data/SQAgent/plugin/redis.sh > /data/SQAgent/data/" + taskid + " 2>>/data/SQAgent/log/jboscan-error.log")
ran = random.randint(0,10)
time.sleep(ran)
input = open("/data/SQAgent/data/" + taskid)
url = 'http://172.25.108.254/api/redispost'
headers = {'Host' : 'o.lenovomm.com'}
value = {'scan' : input.read(),'taskid' : taskid, 'host' : hostname.rstrip('\n')}
data = urllib.urlencode(value)
req = urllib2.Request(url, data, headers)
response = urllib2.urlopen(req)
print response.read()
