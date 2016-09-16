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
22341425
22335919
22333739
22332687
22296997
22287661
22287114
22285355
22282549
22279748
22279143
22278733
22276885
22249621
22247195
22246359
22243370
22242000
22241076
22232029
22229325
22228507
22226265
22225948
22220858
22199988
22198695
22192651
22137897
22136994
22135763
22128522
22125573
22124926
22124339
22123764
22123289
22123145
22120093
22095809
22093453
22093301
22092784
22089635
22088328
22087794
22087231
22053051
22045738
22045141
22045031
22044999
22043888
22023161
22012691
22006438
22001662
21936022
21921310
21917837
21915984
21914016
21911768
21905284
21889527
21886673
21843471
21785530
21779153
21774478
21768688
21767326
21759751
21714843
21708022
21698639
21690467
21671198
21661474
21660710
21659936
21657442
21654550
21651164
21633435
21629093
21628926
21627861
21621557
21621556
21615035
21614630
21614560
21612608
21583065
21578897
21575173
21574822
21571639
21571238
21570998
21569397
21566516
21537259
21529879
21512301
21477152
21469684
21467559
21467271
21467232
21466712
21464797
21463071
21462680
21455050
21415534
21413857
21412094
21405795
21404850
21402387
21402178
21402055
21372794
21369193
21364462
21340153
21335472
21325877
21300720
21297539
21297174
21287558
21269387
21264837
21237032
21232489
21224224
21212308
21210244
21209400
21209359
21205971
21200172
21174611
21171008
21169973
21166642
21165751
21165532
21162113
21161006
21147432
21139168
21138163
21135262
21133654
21131856
21126672
21123691
21122486
21109890
21103658
21102268
21101989
21099981
21098394
21097511
21097274
21094077
21092340
21092329
21067820
21065116
21061893
21057621
21056819
21056086
21054032
'''

import sys
reload(sys)
sys.setdefaultencoding('utf8')

#q="20652662"
try:
    conn=MySQLdb.connect(host='192.168.56.10',user='icm',passwd='wasu@1234',db='icm',port=3306,charset='utf8')
    cur=conn.cursor()
except Exception,e:
    print "Mysql connect issue",e
    logging.info(e)

    
q=q.split()

#q = ['20652662']

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