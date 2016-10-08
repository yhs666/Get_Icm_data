#!/usr/bin/env python
#coding:utf-8
'''
Created on Dec 16, 2015

@author: yang.hongsheng
'''
import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import redis
import logging
import sys
import lxml.html
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import MySQLdb
from Crypto.SelfTest.Hash.test_HMAC import hashlib_test_data
import hashlib

reload(sys)
sys.setdefaultencoding('utf8')

from datetime import datetime

ip ="172.31.4.119"
redispassword = "wasu.com"
time_out = 60

FILE=os.getcwd()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename = os.path.join(FILE,'Get_ICM_date_log.txt'),
                    filemode='w')
try:
    myredis = redis.Redis(host=ip,password=redispassword,port = 6379)
    print "Connect Redis OK!"
    logging.info('Connect Redis OK!')

except:
    print "Redis connect issue!"
    logging.info('Redis connect issue!')
    sys.exit()

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


DATETIME_FMT = '%Y-%m-%d %H:%M:%S'

datetimenow=datetime.strftime(datetime.now(), DATETIME_FMT)

def insert_mysql(q):
    try:
        conn=MySQLdb.connect(host='192.168.56.10',user='icm',passwd='wasu@1234',db='icm',port=3306,charset='utf8')
        cur=conn.cursor()
    except Exception,e:
        print "Mysql connect issue",e
        logging.info(e)
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
    
    return inser_issue,date_issue

class prpcrypt():
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC
     
    #解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')

def new_table(url):
    #main_window =driver.current_window_handle
    script_url= "window.open('%s','_blank');" % url
    driver.execute_script(script_url)
    driver.find_element_by_tag_name('body')

def get_icm_details(page_source):
    try:
        page_source=page_source.encode('utf-8','ignore')
        root = lxml.html.fromstring(page_source)
        icmdetail=[]
        icmazure=[]
        for row in root.xpath('.//table[@id="ctl00_MainContent_TabContainer_TabDetails_IncidentDetailsView"]//tr'):     
            icmdetail.append(row.xpath('.//td/text()'))
            icmazure.append(row.xpath('.//td/div//text()'))

        icmdetail_key=[2,3,4,5,6,7,8,9,13,14,15,16]
        icm_keyword={}
        for i in icmdetail_key:
            hang = icmdetail[i]
            if len(hang) % 2 != 0:
                hang.append('')
            j=0
            while j < len(hang)-1:
                hang_key = hang[j].strip()
                if hang_key == "" or ':' != hang_key[-1]:
                    j=j+1
                    continue      
                hang_value= hang[j+1].strip()
                if  hang_value != "" and  ':' == hang_value[-1]:
                    hang_value=''
                    j=j+1
                else:
                    j=j+2
                
                #print i,j,hang_key,hang_value
                icm_keyword[hang_key]=hang_value
        
        icm_keyword[icmdetail[17][0]] =icmdetail[17][2].strip()
        #print icm_keyword[icmdetail[17][0]]
        icmazure_key=[]
        icmazure_value=[]
        end =len(icmdetail)-1
        begin = end -7
        for i in range(begin,end):
            hang = icmdetail[i]
            for j in hang:
                if j.strip() != "":
                    icmazure_key.append(j.strip())
        for i in range(begin,end):
            hang = icmazure[i]
            if i == end -1 :
                icmazure_value.append(hang[0].strip())
            else:
                for j in range(0,len(hang),2):
                    icmazure_value.append(hang[j].strip())
        #print icmazure_key
        #print icmazure_value
        if len(icmazure_key) == len(icmazure_value):
            for i in range(0,len(icmazure_key)):
                
                icm_keyword[icmazure_key[i]]=icmazure_value[i].encode('utf-8','ignore')
            
            # tilte and summary not error code
            icm_keyword["Title:"]= driver.find_element_by_id("ctl00_MainContent_IncidentTitleHeader").text
            icm_keyword["Current Summary:"]= driver.find_elements_by_xpath("//*[@id='bigStringTextDiv']")[-1].text
            
            icm_keyword["Owning Team:"] =driver.find_element_by_xpath("/html/body/form/div[3]/div[2]/div[2]/div[2]/div[2]/div[1]/div/table/tbody/tr/td/table/tbody/tr[3]/td[4]").text
            icm_keyword["Impacted Services:"] =driver.find_element_by_xpath("/html/body/form/div[3]/div[2]/div[2]/div[2]/div[2]/div[1]/div/table/tbody/tr/td/table/tbody/tr[4]/td[2]").text
            icm_keyword["Impacted Teams:"] =driver.find_element_by_xpath("/html/body/form/div[3]/div[2]/div[2]/div[2]/div[2]/div[1]/div/table/tbody/tr/td/table/tbody/tr[4]/td[4]").text
            icm_keyword["Impacted Component:"] =driver.find_element_by_xpath("/html/body/form/div[3]/div[2]/div[2]/div[2]/div[2]/div[1]/div/table/tbody/tr/td/table/tbody/tr[4]/td[6]").text
            icm_keyword["Service Responsible:"] =driver.find_element_by_xpath("/html/body/form/div[3]/div[2]/div[2]/div[2]/div[2]/div[1]/div/table/tbody/tr/td/table/tbody/tr[5]/td[2]").text
            
            
            return icm_keyword
        else:
            print "ICM Azure part have issue or changed!"
            logging.info("ICM Azure part have issue or changed!")
            return False
    except Exception , e:
        msg = "get_icm_details: issue.  " + e
        print msg
        logging.info(msg)
        return False

def get_icm_history(page_source):
    try:
        icmhistory=[] 
        page_source=page_source.encode('utf-8','ignore')   
        root = lxml.html.fromstring(page_source)
        for row in root.xpath('.//table[@id="HistoryDisplayGrid"]//tr'):
            icmhistory.append(row.xpath('.//td/text()'))
            
        icm_history=[]
        
        for i in icmhistory:
            temp=[]
            t={}
            if i ==[]:
                continue
            for j in range(0,len(i)):
                if j <3:
                    temp.append(i[j])
                else:
                    k = i[j].split('[')
                    l = i[j].split(':')
                    if len(l) !=2 and len(k) ==1:
                        t[i[j]] =""
                    elif len(k)==2:
                        h_key =k[0].split("'")[1]
                        h_val = k[1].split("]")[0]
                        t[h_key]=h_val
                    elif len(l) ==2:
                        h_key =l[0].replace("'","")
                        h_val = l[1]
                        t[h_key]=h_val                
                    else:
                        h_key =k[1].split("]")[0]
                        h_val = k[2].split("]")[0]
                        t[h_key]=h_val
            temp.append(t)
            icm_history.append(temp)
        
        return icm_history
    except Exception , e:
        print "get_icm_history",e
        return False 
def login():    
#def login(username,password):
    try:
        elem = driver.find_element_by_id("userNameInput")
        elem.clear()
        elem.send_keys(username)
        elem = driver.find_element_by_id("passwordInput")
        elem.clear()
        elem.send_keys(password)
        time.sleep(1)
        elem = driver.find_element_by_id("submitButton")
        elem.click()
        return True 
    except Exception, e:
        print "login: Not found login!",e
        return False
    
def icm_login(url,n= None):
    try:
        if n == 1:
            #login(username, password)
            login() 
            print "ICM_login:  OK!"
            return driver.current_window_handle
        else:
            return new_table(url)
            print "ICM_login: new table"
    except Exception, e:
        return False
        print "ICM_login:  ISSUE !",e

def set_redis(key,vaule):
    try:
        myredis.set(key,json.dumps(vaule))
    except Exception, e:
        print e
        myredis.set(key,json.dumps(vaule,ensure_ascii=False))
        
def deal_icm(hands,detailorhistory='ALL'):
    '''
    detail or histroy ==[detail,history,ALl]
    '''
    #get icm details
    for i in hands:
        
        try:
            driver.switch_to_window(i)
            driver.implicitly_wait(60)
            if detailorhistory =='detail' or detailorhistory=='ALL':
                icmNo = driver.current_url[-8:]
                icmdet = get_icm_details(driver.page_source)
                icmdet['updatetime']= datetime.strftime(datetime.now(), DATETIME_FMT)
                icmdet['Created Date']=driver.find_element_by_id("ctl00_MainContent_CreatedDateLabel").text
                tm=driver.find_element_by_id("ctl00_MainContent_SeverityLabel").text
                icmdet['Ticket State']=tm.split('-')[1].strip()
                print icmNo,icmdet
                key= icmNo + ":detail"
                set_redis(key,icmdet)
                # write status
                key2 =icmNo + ":detail:status"
                myredis.set(key2,"ok")
                #msg = icmNo +" :Details: " + icmdet
                #logging.info(msg)
            #click history

        except Exception, e:
            icmNo = driver.current_url[-8:]
            msg = icmNo + ' Get Details Have issue!!',e
            print  time.ctime(),msg 
            logging.info(msg)
            key2 =icmNo + ":detail:status"
            myredis.set(key2,"issue")
            
    if detailorhistory=='ALL' or detailorhistory=='history':
        for i in hands:
            driver.switch_to_window(i)
            driver.implicitly_wait(5)
            history =driver.find_element_by_id("__tab_ctl00_MainContent_TabContainer_TabHistory")
            history.click()
    #deal history
    if detailorhistory=='ALL'  or detailorhistory=='history':
        for i in hands:
            try: 
                driver.switch_to_window(i)
                element = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "HistoryDisplayGrid")))
                driver.implicitly_wait(60)
                icmNo = driver.current_url[-8:]
                icm_history_list = get_icm_history(driver.page_source)
                icm_history_list.append(datetime.strftime(datetime.now(), DATETIME_FMT))
                #print icmNo,icm_history_list
                key= icmNo + ":history"
                myredis.set(key,json.dumps(icm_history_list,ensure_ascii=False))
                # write status
                key2 =icmNo + ":history:status"
                myredis.set(key2,"ok")
                
                #msg = icmNo +":history:" +icm_history_list
                #logging.info(msg)
                
            except Exception, e:
                icmNo = driver.current_url[-8:]
                msg = icmNo + ' Get History Have issue!!',e
                print  time.ctime(),msg 
                logging.info(msg)
                key2 =icmNo + " :detail :status"
                myredis.set(key2,"issue")
    for i in hands:
        driver.switch_to_window(i)
        driver.close()           
            
def get_pwd():
    get_encry =myredis.get("cmepwd")
    pc = prpcrypt('wasuwasuwasuwasu') 
    return  pc.decrypt(get_encry)     

# insert history:
def insert_icm_history(icm):
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
                print icm_effort_0
                #insert database
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
                logging.info(e)
    
    cur.close()
    conn.close() 
    
    return inser_issue
            

#define the icm tickets

s='''
21785530
''' 
# 初始化ICM 
def init_icm():
    try:
        global username
        username = "cme\oe-yanghongsheng"
        global password 
        password = get_pwd()
        
        global driver
        # define ENV
        url="https://icm.ad.msft.net/imp/v3/incidents/search/basic"
        iedriver = "C:\Users\yang.hongsheng\Desktop\IEDriverServer\IEDriverServer32.exe"
        os.environ["webdriver.ie.driver"] = iedriver
        driver = webdriver.Ie(iedriver) 
        #login icm
        driver.get(url)
        #login_icm_handle = icm_login(url, n=1)
        login()
        global login_icm_handle
        login_icm_handle=driver.current_window_handle
        driver.implicitly_wait(30)
        cookie = driver.get_cookies()
        driver.add_cookie(cookie[0]) 
        
           
    except Exception,e:
        print "icm init err: ",str(e)
        logging.info("icm init error! exit.") 
        sys.exit()

def get_icm_data(tickets_list,get_type):
    # default ALL, select detail or history
    #并发数
    bing = 10
    #get icm detail or history
    q= tickets_list
    for i in range(0,len(q),bing):
        end=len(q)-i  
        if end > bing:
            end=bing
        for  j in range(0,end):
            url = "https://icm.ad.msft.net/imp/IncidentDetails.aspx?id=" + q[j+i]
            new_table(url)
            time.sleep(2)
    
        hands = driver.window_handles
        hands.remove(login_icm_handle)
        # default ALL, select details or history
        deal_icm(hands,get_type)
        driver.switch_to_window(login_icm_handle)    
        #get icm date over.
    print "************************Get icm data  Done************************************"
    msg = ' Get ICM Date  Run over!!'
    print  time.ctime(),msg 
    logging.info(msg)
    
    if get_type =="ALL" or get_type =="detail":
        #insert icm details in  mysql
        insert_issue,date_issue = insert_mysql(q)
        print "************************Insert Detail  Done************************************" 
        if not insert_issue:
            print "Insert icm detail OK!!"
        else:
            print "Insert icm detail  issue tickets:", insert_issue," data have issue tickets: ",date_issue
        
        msg = "Insert icm detail issue tickets:" + " ".join(insert_issue) + " data have issue tickets: " + " ".join(date_issue)
        logging.info(msg)
        
    if get_type =="ALL" or get_type =="history":
        #Insert icm history
        history_issue=insert_icm_history(q)
        print "************************Insert history  Done************************************"
        if not history_issue:
            print "Insert icm history OK!!"
        else:
            print "Insert history issue tickets:",history_issue
        
        msg = "Insert history issue tickets:" + " ".join(history_issue) 
        logging.info(msg)
    
def run_temp_list():
    # get icm month report
    while 1:
        key = myredis.lpop("temp_list")
        print time.asctime(),"run temp_list key: ", key
        if key:
            key2= key + ":status"
            q = json.loads(myredis.get(key))
            
            if myredis.get(key2) =="submit":
                
                msg = "run temp_list: key: %s  tickets: %s " % (key," ".join(q))
                print msg
                #get_icm_data(q,"detail")
                myredis.set(key2,"running")
                get_icm_data(q,"ALL")
                myredis.set(key2,"done")
                logging.info(msg)
            else:
                s = " ".join(q)
                msg = "run temp_list had done.: key: %s  tickets: %s " % (key,s)
                print msg
                logging.info(msg)
                continue
        else:
            
            break
    
def new_icm_tickets(team):
    #New icm tickets comming
    # team =['wasu','wash']
    try:
        for i in team:
            key = i + ":new_icm"
            while 1:
                tickets = myredis.rpop(key)
                
                key2 = i + ":active_icm"
                if tickets :
                    print tickets
                    myredis.sadd(key2,tickets)
                    print "Add redis set"
                else:
                    print time.asctime(),key ,"No new icm tickets."
                    break  
    except Exception,e:
        print "new_icm_tickets Error: ",str(e)
        logging.info("new_icm_tickets error!") 


        ''' 
        print myredis.smembers("active_icm")
        
        myredis.srem("active_icm","None")  #del value
        
        s = list(myredis.smembers("active_icm"))
        s.sort()
        print s
        #tickets update
        print json.loads(myredis.get("21900755:detail"))["updatetime"]
        #2016-08-29 13:20:01
        '''
def active_icm_tickets(team):
    try:
        for i in team:
            key = i + ":active_icm"
            key2= key + ":status"
            if myredis.get(key2) =="submit":
                q= list(myredis.smembers(key))
                q.sort()
                get_icm_data(q,"ALL")
            else:
                print time.asctime(),key2 ,"Not submit"
    except Exception,e:
        print "active_icm_tickets Error: ",str(e)
        logging.info("active_icm_tickets error!") 

def close_temp_tickets(team):
    try:
        for i in team:
            key = i + ":close_temp"
            key2= key + ":status"
            if myredis.get(key2) =="submit":
                q= list(myredis.smembers(key))
                q.sort()
                get_icm_data(q,"ALL")
            else:
                print time.asctime(),key2 ,"Not submit"
    except Exception,e:
        print "close_temp_tickets Error: ",str(e)
        logging.info("close_temp_tickets error!")    

def date_computer(s,seconds_or_day):
    #string like  ""2016-08-29 13:20:01""
    #string ["second","day","hour","minute"]
    starttime = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    endtime = datetime.now()
    seconds =(endtime - starttime).seconds
    days = (endtime - starttime).days

    if seconds_or_day =="second":
        return seconds
    elif seconds_or_day =="day":
        return days
    elif seconds_or_day =="hour":
        hours = days * 24 + seconds // 3600
        return hours
    elif seconds_or_day =="minute":
        minutes =days * 24 * 60 +  seconds  // 60
        return minutes
    else:
        return False
def get_page_hash():
    driver.switch_to_window(login_icm_handle)
    m_page = hashlib.md5()
    m_page.update(driver.page_source)
    main_hash = m_page.hexdigest()
    return main_hash
def check_login():
    try:
        driver.implicitly_wait(3)
        WebDriverWait(driver, 3).until(lambda x : x.find_element_by_id("submitButton"))
        #driver.find_element_by_id("submitButton")
        #driver.switch_to_window(login_icm_handle)
        driver.implicitly_wait(30)
        login()
        msg = "Check icm login Need re login!"
        print msg
        logging.info(msg) 
    except Exception,e:
        driver.implicitly_wait(30)
        msg = "Check icm login didn't Need re login!"
        print msg
        logging.info(msg) 
    
    
if __name__=='__main__':

    # init icm
    init_icm()
    #team
    
    team = ["wasu","wash"]
    #get user submit tickets data
    n=0
    while 1:
        n=n+1
        if n >= 10:
            n=0
            check_login()
            
        new_icm_tickets(team)
        active_icm_tickets(team)
        close_temp_tickets(team)
        run_temp_list()
        time.sleep(1)


    driver.quit()
    print "Done!!!!!!!!!"
    sys.exit()

    