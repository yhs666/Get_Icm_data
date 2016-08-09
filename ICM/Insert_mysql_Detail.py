#!/usr/bin/env python
#coding:utf-8
'''
Created on 2016年7月12日

@author:yang.hongsheng 
'''

import MySQLdb
import redis
import logging
import sys
import json
import os

keyword=[
        'IncidentSeverity',
        'Title',
        'Effort Time',
        'SubType',
        'EscalationOccured',
        'Trigger',
        'Azure Source',
        'Created Date',
        'Mitigated Date',
        'Resolved Date',
        'Ticket State',
        'Sub Status',
        'Owning Service',
        'Owning Team',
        'Impacted Services',
        'Impacted Teams',
        'Impacted Component',
        'Service Responsible',
        'Keywords',
        'Current Summary',
        'updatetime',
         ]
redis_key=[
        'Severity:',
        'Title:',
        'Ops Team Effort:',
        'Azure SubType:',
        'Escalation Status:',
        'Trigger Field:',
        'Azure Source:',
        'Created Date',
        'Time Mitigated (CST):',
        'Time Resolved (CST):',
        'Ticket State',
        'Sub Status:',
        'Owning Service:',
        'Owning Team:',
        'Impacted Services:',
        'Impacted Teams:',
        'Impacted Component:',
        'Service Responsible:',
        'Keywords:',
        'Current Summary:',
        'updatetime'
           ]



ip ="172.31.4.119"
password = "wasu.com"
time_out = 60

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
    
q = ['20170992','20224075']

q = '''
20590098
20588370
20588080
20533922
20530894
20528851
20528557
20526036
20525446
20523094
20521607
20520989
20520749
20501570
20495772
20494204
20492977
20480162
20475927
20474496
20444529
20439166
20439053
20438204
20436200
20435552
20430382
20429775
20390260
20383804
20380592
20379681
20343769
20342305
20338398
20331611
20328860
20328039
20305033
20300654
20294446
20271358
20267311
20264775
20264431
20264135
20262687
20261419
20259016
20258195
20255579
20245212
20224075
20213746
20213203
20208044
20176391
20171814
20170992
20167689
20166505
20166041
20165851
20159435
20159400
20137621
20134091
20133641
20133010
20131549
20111604
20104370
20099742
20097333
20095811
20094430
20091871
20088216
20087966
20087924
20086646
20085986
20068023
20066401
20063433
20062962
20062960
20062935
20061975
20061911
20059697
20059448
20048132
20042611
20041747
20035673
20033373
20028285
20028018
20025158
19973143
19968684
19967591
19966768
19939250
19938141
19936190
19934071
19928324
19926783
19926026
19922683
19914104
'''

#q="20652662"
try:
    conn=MySQLdb.connect(host='192.168.56.10',user='icm',passwd='wasu@1234',db='icm',port=3306,charset='utf8')
    cur=conn.cursor()
except Exception,e:
    print "Mysql connect issue",e
    logging.info(e)

    
q=q.split()

q = ['20652662']

inser_issue=[]
date_issue=[]
for i in q:
    key = i +":detail:status"
    
    if myredis.get(key) == "ok" :
        key = i +":detail"
        icm_detail= json.loads(myredis.get(key))
        insert_db=[]
        insert_db.append(i)
        for j in range(0,len(keyword)):
            insert_db.append(icm_detail[redis_key[j]].encode('utf-8'))
            
        print i,insert_db   
        msg = i + "  " + " ".join(insert_db)   
        logging.info(msg )
        print "---------------------------------------------------------------------------------"
        try:
            sql = "delete from icm_detail where ID=" + i
            cur.execute(sql)
        except Exception,e:
            
            msg = "delet %s : %s" %(i,e)
            print msg
            logging.info(msg)
        try:
            cur.execute('''insert into icm_detail  values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', insert_db)
            conn.commit() 
        except Exception,e:
            msg = "add  %s : %s" %(i,e) 
            print msg
            logging.info(msg)
            inser_issue.append(i)
    else:
        
        print i, "Get Date have issue! Please get this tickets again!!"
        date_issue.append(i)

#show the issue icm number
print "ICM tcikets insert database have issue",inser_issue
print "ICM tcikets Date have issue",date_issue

# close mysql connect
cur.close()
conn.close()