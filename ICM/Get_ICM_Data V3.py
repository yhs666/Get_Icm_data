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

ip ="172.31.4.119"
password = "wasu.com"
time_out = 60

FILE=os.getcwd()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename = os.path.join(FILE,'Get_ICM_date_log.txt'),
                    filemode='w')
try:
    myredis = redis.Redis(host=ip,password=password,port = 6379)
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
from datetime import datetime
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
    
def login(username,password):
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
        print "login: Not found login!"
        return False
    
def icm_login(url,n= None):
    try:
        if n == 1:
            login(username, password) 
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
19504254
19914104
19922683
19926026
19926783
19928324
19934071
19936190
19938141
19939250
19966768
19967591
19968684
19973143
20025158
20028018
20028285
20033373
20035673
20041747
20042611
20048132
20059448
20059697
20061911
20061975
20062935
20062960
20062962
20063433
20066401
20068023
20085986
20086646
20087924
20087966
20088216
20091871
20094430
20095811
20097333
20099742
20104370
20111604
20131549
20133010
20133641
20134091
20137621
20159400
20159435
20165851
20166041
20166505
20167689
20170992
20171814
20176391
20208044
20213203
20213746
20224075
20245212
20255579
20258195
20259016
20262687
20264135
20264431
20264775
20267311
20271358
20294446
20300654
20305033
20328039
20328860
20331611
20338398
20342305
20343769
20379681
20380592
20383804
20390260
20429775
20430382
20435552
20436200
20438204
20439053
20439166
20444529
20474496
20475927
20480162
20492977
20494204
20495772
20501570
20520749
20520989
20521607
20523094
20525446
20526036
20528557
20528851
20530894
20533482
20533922
20588080
20588370
20590098
20608225
20614528
20616307
20618436
20625231
20652662
20655211
20655591
20657777
20661792
20665843
20682283
20688940
20693895
20705547
20724856
20727221
20727352
20730587
20768658
20770492
20771012
20771091
20775552
20784039
20787560
20789776
20809963
20812029
20812811
20814102
20815779
20822501
20870315
20872161
20879844
20880377
20887697
20915754
20916001
20916232
20916274
20916698
20917682
20923534
20924366
20925415
20935384
20935478
20940272
20968863
20972036
20972906
20975359
20977263
20978245
20987714
20988997
21021629
21021865
21038650
21041658
'''  



if __name__=='__main__':
    username = "cme\oe-yanghongsheng"
    password = get_pwd()
    global driver
    #并发数
    bing = 10

    # define ENV
    url="https://icm.ad.msft.net/imp/v3/incidents/search/basic"
    iedriver = "C:\Users\yang.hongsheng\Desktop\IEDriverServer\IEDriverServer32.exe"
    os.environ["webdriver.ie.driver"] = iedriver
    driver = webdriver.Ie(iedriver)
    
    #login icm
    driver.get(url)
    login_icm_handle = icm_login(url, n=1)
    driver.implicitly_wait(30)
    cookie = driver.get_cookies()
    driver.add_cookie(cookie[0])
    
    #get icm list
    q= s.split()
    #q = ['20614528']
    
    #get icm detail or history
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
        deal_icm(hands)
        driver.switch_to_window(login_icm_handle)

  
    #get icm date over.
    print "************************Get icm data  Done************************************"
    msg = ' Get ICM Date  Run over!!'
    print  time.ctime(),msg 
    logging.info(msg)
    
    #insert icm details in  mysql
    insert_issue,date_issue = insert_mysql(q)
    print "************************Insert Detail  Done************************************" 
    if not insert_issue:
        print "Insert icm detail OK!!"
    else:
        print "Insert icm detail  issue tickets:",insert_issue," data have issue tickets: ",date_issue
    
    msg = "Insert icm detail issue tickets:" + " ".join(insert_issue) + " data have issue tickets: " + " ".join(date_issue)
    logging.info(msg)
    
    #Insert icm history
    history_issue=insert_icm_history(q)
    print "************************Insert history  Done************************************"
    
    
    if not history_issue:
        print "Insert icm history OK!!"
    else:
        print "Insert history issue tickets:",history_issue
    
    msg = "Insert history issue tickets:" + " ".join(history_issue) 
    logging.info(msg)
    driver.quit()
    print "Done!!!!!!!!!"
    sys.exit()
    
    
    #click history table
    
    