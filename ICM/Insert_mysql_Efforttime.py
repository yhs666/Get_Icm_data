#!/usr/bin/env python
#coding:utf-8
'''
Created on 2016/7/25

@author:yang.hongsheng 
'''

import redis
import json
import MySQLdb
from datetime import datetime
import os
import logging
import sys

ip ="172.31.4.119"
password = "wasu.com"

FILE=os.getcwd()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename = os.path.join(FILE,'inser_mysql_log.txt'),
                    filemode='w')
try:
    myredis = redis.Redis(host=ip,password=password,port = 6379)
    print "Connect Redis OK!"
    logging.info('Connect Redis OK!')

except:
    print "Redis connect issue!"
    logging.info('Redis connect issue!')
    sys.exit()
    
 
icm = ["20614528"]
#icm = q.split()

DATETIME_FMT = '%Y-%m-%d %H:%M:%S'
datetimenow=datetime.strftime(datetime.now(), DATETIME_FMT) 

try:
    conn=MySQLdb.connect(host='192.168.56.10',user='icm',passwd='wasu@1234',db='icm',port=3306,charset='utf8')
    cur=conn.cursor()
except Exception,e:
    print "Mysql connect issue",e
    logging.info(e)
    
inser_issue =[]  
# deal history, got the effort time
for h in icm:
    key =h +":history"
    key2 = h+ ":history:status"
    if myredis.get(key2) =="ok":
        history = json.loads(myredis.get(key))
        icm_effort_0=[]
        l=len(history)
        i=0
        try:
            while i < l:
                icm_effort_1=[]
                if isinstance(history[i][-1],(dict)) and "Azure/Ops Team Effort" in history[i][-1].keys():
                    icm_effort_1.append(h)
                    icm_effort_1.append( history[i][0])
                    icm_effort_1.append( history[i][1])
                    j=1
                    while i+j < l:
                        if isinstance(history[i+j][-1],(dict)) and "Azure/Ops Team Effort" in history[i+j][-1].keys():
                            effort = int(history[i][-1]["Azure/Ops Team Effort"]) - int(history[i+j][-1]["Azure/Ops Team Effort"])
                            i=i+j
                            break
                        else:
                            j=j+1
                    else:
                        effort = int(history[i][-1]["Azure/Ops Team Effort"])
                        i=i+1
                    
                    icm_effort_1.append( effort)
                    
                    icm_effort_1.append( history[-1])
                    #icm_effort_1.append(datetimenow)
                    
                    icm_effort_0.append(icm_effort_1)
                else:
                    i=i+1
        
            # deal History done
            
            #insert database
            
            print "---------------------------------------"
            try:
                sql = "delete from icm_effort where icm=" + h
                cur.execute(sql)
            except Exception,e: 
                msg = "delet %s : %s" %(h,e)
                print msg
                logging.info(msg)
            
            
            try:
                for i in icm_effort_0:
                    print i
                    logging.info(i)
                    cur.execute('''insert into icm_effort(icm,operationtime,username,effort,updatetime)  values(%s,%s,%s,%s,%s)''',i)
                conn.commit() 
            except Exception,e:
                msg = "Insert  %s : %s" %(h,e) 
                print msg
                logging.info(msg)
                inser_issue.append(h)
            
        except Exception,e:
            print history,e
            inser_issue.append(h)

cur.close()
conn.close() 
            
print "************************Done************************************"
print "Insert issue tickets:",inser_issue

if not inser_issue:
    print "Run OK!!"
else:
    print "Some tickets insert mysql have issue."
    
        
            
