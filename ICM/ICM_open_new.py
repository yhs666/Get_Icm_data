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

#import win32api,win32con,win32gui,time
#from win32file import INVALID_HANDLE_VALUE 
import redis
import logging
import sys
import lxml.html
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
#import Crypto
#sys.modules['Crypto'] = crypto
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

ip ="172.31.4.119"
password = "wasu.com"
time_out = 60

FILE=os.getcwd()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename = os.path.join(FILE,'ICM_log.txt'),
                    filemode='w')
try:
    myredis = redis.Redis(host=ip,password=password,port = 6379)
    print "Connect Redis OK!"
    logging.info('Connect Redis OK!')

except:
    print "Redis connect issue!"
    logging.info('Redis connect issue!')
    sys.exit()

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
    '''
    driver.implicitly_wait(10)
    hands = driver.window_handles
    #mc_adfs()
    if len(hands) >1 :
        driver.switch_to_window(driver.window_handles[1])
        return driver.current_window_handle
        print "new_table:successfull change the windows hands"
    else:
        print "new_table:Please check Ie setting"
        return False 
    '''
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
        print icmazure_key
        print icmazure_value
        if len(icmazure_key) == len(icmazure_value):
            for i in range(0,len(icmazure_key)):
                
                icm_keyword[icmazure_key[i]]=icmazure_value[i].encode('utf-8','ignore')
            
            return icm_keyword
        else:
            print "ICM Azure port have issue or changed!"
            
            return False
    except Exception , e:
        print e
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
        print e
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
        print "ICM_login:  ISSUE blow!"
        print e 

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
                icmdet['updatetime']=time.ctime()
                icmdet['Created Date']=driver.find_element_by_id("ctl00_MainContent_CreatedDateLabel").text
                tm=driver.find_element_by_id("ctl00_MainContent_SeverityLabel").text
                icmdet['Ticket State']=tm.split('-')[1].strip()
                print icmNo,icmdet
                key= icmNo + ":detail"
                set_redis(key,icmdet)
                # write status
                key2 =icmNo + ":detail:status"
                myredis.set(key2,"ok")
            #click history

        except Exception, e:
            icmNo = driver.current_url[-8:]
            msg = icmNo + ' Get Details Have issue!!',e
            print  time.ctime(),msg 
            logging.info(msg)
            key2 =icmNo + ":detail:status"
            myredis.set(key2,"issue")
    for i in hands:
        if detailorhistory=='ALL' or detailorhistory=='history':
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
                icm_history_list.append(time.ctime())
                print icmNo,icm_history_list
                key= icmNo + ":history"
                myredis.set(key,json.dumps(icm_history_list,ensure_ascii=False))
                # write status
                key2 =icmNo + ":history:status"
                myredis.set(key2,"ok")
                
            except Exception, e:
                icmNo = driver.current_url[-8:]
                msg = icmNo + ' Get History Have issue!!',e
                print  time.ctime(),msg 
                logging.info(msg)
                key2 =icmNo + ":detail:status"
                myredis.set(key2,"issue")
    for i in hands:
        driver.switch_to_window(i)
        driver.close()           
            
def get_pwd():
    get_encry =myredis.get("cmepwd")
    pc = prpcrypt('wasuwasuwasuwasu') 
    return  pc.decrypt(get_encry)     


#define the icm tickets

s='''
19926026
20028018
20028285
20033373
20062962
20159435
20258195
20300654
20444529
20474496
20530894
20533922
'''  

s='''
20028285
20028018
20300654
'''
if __name__=='__main__':
    username = "cme\oe-yanghongsheng"
    password = get_pwd()
    global driver
    
    #bing fa number
    bing = 10
    
    url="https://icm.ad.msft.net/imp/IncidentSummary.aspx"
    iedriver = "C:\Users\yang.hongsheng\Desktop\IEDriverServer\IEDriverServer32.exe"
    os.environ["webdriver.ie.driver"] = iedriver
    
    driver = webdriver.Ie(iedriver)
    
    driver.get(url)
    login_icm_handle = icm_login(url, n=1)
    driver.implicitly_wait(30)
    cookie = driver.get_cookies()
    driver.add_cookie(cookie[0])
    
    q= s.split()
    #q = ['20170992','20224075']
    
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

    print "Run OK!"

    msg = ' Run over!!'
    print  time.ctime(),msg 
    logging.info(msg)
    

    #url == https://icm.ad.msft.net/imp/IncidentDetails.aspx?id=20088216
    #driver.close()
    driver.quit()
    
    
    #click history table
    
    