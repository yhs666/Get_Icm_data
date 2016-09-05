#!/usr/bin/env python
#coding:utf-8
'''
Created on 2016��8��25��

@author:yang.hongsheng 
'''



#!/usr/bin/env python
#coding:utf-8
'''
Created on 2016��1��9��

@author:yang.hongsheng 
'''

import cPickle 
import redis
import time
import win32con
import win32clipboard as w
import logging
import sys,os
import hashlib
import threading
import datetime
import codecs
import json
from pytz import timezone
from multiprocessing import Queue


dnsservers='''
61.178.0.93
61.166.150.123
61.153.81.75
61.153.177.196
61.147.37.1
61.139.2.69
61.134.1.4
61.132.163.68
61.128.192.68
61.128.128.68
60.191.244.5
59.51.78.211
223.6.6.6
223.5.5.5
222.88.88.88
222.85.85.85
222.74.39.50
222.246.129.80
222.172.200.68
221.7.92.98
221.6.4.67
221.6.4.66
221.5.88.88
221.5.203.98
221.131.143.69
221.12.33.227
221.12.1.227
221.11.1.68
221.11.1.67
219.150.32.132
219.148.162.31
219.147.198.242
219.147.198.230
219.147.1.66
219.146.1.66
219.146.0.132
219.141.140.10
219.141.136.10
218.85.157.99
218.85.152.99
218.6.200.139
218.4.4.4
218.30.19.40
218.30.118.6
218.201.96.130
218.2.2.2
218.2.135.1
211.138.180.3
211.138.180.2
211.137.191.26
210.22.84.3
210.22.70.3
210.21.196.6
210.2.4.8
208.67.222.222
208.67.220.220
203.195.182.150
202.99.96.68
202.99.224.8
202.99.224.68
202.99.192.68
202.99.192.66
202.99.166.4
202.99.160.68
202.99.104.68
202.98.5.68
202.98.198.167
202.98.192.67
202.98.0.68
202.97.224.69
202.97.224.68
202.96.69.38
202.96.64.68
202.96.209.5
202.96.209.133
202.96.134.33
202.96.128.86
202.96.128.68
202.96.128.166
202.106.46.151
202.106.196.115
202.106.195.68
202.106.0.20
202.103.24.68
202.103.225.68
202.103.224.68
202.103.0.68
202.102.227.68
202.102.224.68
202.102.213.68
202.102.154.3
202.102.152.3
202.102.134.68
202.102.128.68
202.101.226.68
202.101.224.69
202.101.172.35
202.100.64.68
199.91.73.222
182.254.116.116
180.76.76.76
180.153.225.136
178.79.131.110
140.207.198.6
124.161.87.155
123.125.81.6
119.6.6.6
119.29.29.29
118.244.224.124
116.228.111.118
115.29.189.118
114.215.126.16
114.114.115.115
114.114.114.114
112.4.0.55
112.124.47.27
108.168.255.118
101.226.4.6
1.2.4.8
'''

import sys
import socket
import os
import re

def reply_to_iplist(data):
    assert isinstance(data, basestring)
    iplist = ['.'.join(str(ord(x)) for x in s) for s in re.findall('\xc0.\x00\x01\x00\x01.{6}(.{4})', data) if all(ord(x) <= 255 for x in s)]
    print iplist
    return iplist

def domain_to_ip(dnsserver,domain):
    dnsserver = dnsserver
    seqid = os.urandom(2)
    host = ''.join(chr(len(x))+x for x in domain.split('.'))
    data = '%s\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00%s\x00\x00\x01\x00\x01' % (seqid, host)
    sock = socket.socket(socket.AF_INET,type=socket.SOCK_DGRAM)
    sock.settimeout(None)
    sock.sendto(data, (dnsserver, 53))
    data = sock.recv(512)
    print reply_to_iplist(data)
    return reply_to_iplist(data)
'''
dnsServer = "8.8.8.8"
sina = domain_to_ip(dnsServer,"sina.com")
google = domain_to_ip(dnsServer,"google.com")
youbube = domain_to_ip(dnsServer,"youtube.com")
print("sina:",sina)
print("google:",google)
print("youbube:",youbube)   
'''

domain="maxtm.trafficmanager.cn"
i=0
while 1<100:
    threads=[]
    for dnsserver in dnsservers.split():
        t = threading.Thread(target=domain_to_ip,args=(dnsserver,domain,))
        threads.append(t)
    for t in threads:
        t.setDaemon(True)
        t.start()
        
    t.join()
    print i
    i=i+1
    time.sleep(30)
    
print "done"
