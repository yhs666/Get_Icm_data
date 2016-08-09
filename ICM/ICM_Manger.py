#!/usr/bin/env python
#coding:utf-8
'''
Created on 2016年7月28日

@author:yang.hongsheng 
'''
import redis
import json
#import MySQLdb
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
    
DATETIME_FMT = '%Y-%m-%d %H:%M:%S'
datetimenow=datetime.strftime(datetime.now(), DATETIME_FMT) 

'''
quence0 =["active_quence","tickets_quence","new_quence","resolved_quence","tmp_quence"]
myredis.set("quence",json.dumps(quence0))
for i in quence0:
    myredis.lpush(i,'')
'''    
quence = json.loads(myredis.get("quence"))

q = ["20614528","ddddddd"]


for i in q:
    
    myredis.lpush("active_quence", i)
    #myredis.lpush
    pass


#print myredis.lpop("active_quence")

myredis.lrem("active_quence","20614528",num=0)
print myredis.llen("active_quence")
print myredis.lrange("active_quence",0,-1)

'''
for i in quence:
    print myredis.llen(i)
    print myredis.lpop(i)

print quence
#删除name对应的list中的指定值
r.lrem("list_name","SS",num=0)
redis中的List在在内存中按照一个name对应一个List来存储 

lpush(name,values)

# 在name对应的list中添加元素，每个新的元素都添加到列表的最左边
r.lpush("list_name",2)
r.lpush("list_name",3,4,5)#保存在列表中的顺序为5，4，3，2
rpush(name,values)

#同lpush，但每个新的元素都添加到列表的最右边
lpushx(name,value)

#在name对应的list中添加元素，只有name已经存在时，值添加到列表的最左边
rpushx(name,value)

#在name对应的list中添加元素，只有name已经存在时，值添加到列表的最右边
llen(name)

# name对应的list元素的个数
print(r.llen("list_name"))
linsert(name, where, refvalue, value))

复制代码
# 在name对应的列表的某一个值前或后插入一个新值
r.linsert("list_name","BEFORE","2","SS")#在列表内找到第一个元素2，在它前面插入SS

参数：
     name: redis的name
     where: BEFORE（前）或AFTER（后）
     refvalue: 列表内的值
     value: 要插入的数据

复制代码
r.lset(name, index, value)

#对list中的某一个索引位置重新赋值
r.lset("list_name",0,"bbb")
r.lrem(name, value, num)

复制代码
#删除name对应的list中的指定值
r.lrem("list_name","SS",num=0)

 参数：
    name:  redis的name
    value: 要删除的值
    num:   num=0 删除列表中所有的指定值；
           num=2 从前到后，删除2个；
           num=-2 从后向前，删除2个
复制代码
lpop(name)

#移除列表的左侧第一个元素，返回值则是第一个元素
print(r.lpop("list_name"))
lindex(name, index)

#根据索引获取列表内元素
print(r.lindex("list_name",1))
lrange(name, start, end)

#分片获取元素
print(r.lrange("list_name",0,-1))
ltrim(name, start, end)

#移除列表内没有在该索引之内的值
r.ltrim("list_name",0,2)
rpoplpush(src, dst)

# 从一个列表取出最右边的元素，同时将其添加至另一个列表的最左边
#src 要取数据的列表
#dst 要添加数据的列表
brpoplpush(src, dst, timeout=0)

#同rpoplpush，多了个timeout, timeout：取数据的列表没元素后的阻塞时间，0为一直阻塞
r.brpoplpush("list_name","list_name1",timeout=0)
blpop(keys, timeout)

复制代码
#将多个列表排列,按照从左到右去移除各个列表内的元素
r.lpush("list_name",3,4,5)
r.lpush("list_name1",3,4,5)

while True:
    print(r.blpop(["list_name","list_name1"],timeout=0))
    print(r.lrange("list_name",0,-1),r.lrange("list_name1",0,-1))

keys: redis的name的集合
   timeout: 超时时间，获取完所有列表的元素之后，阻塞等待列表内有数据的时间（秒）, 0 表示永远阻塞
复制代码
r.brpop(keys, timeout)

#同blpop，将多个列表排列,按照从右像左去移除各个列表内的元素
'''