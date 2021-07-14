# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 14:05:27 2020

@author: yakupcatalkaya
"""

from selenium import webdriver
import time
import webbrowser as web
from selenium.webdriver.firefox.options import Options
from keyboard import press
import os

def get_code(source):
    htmlx = source.page_source
    for line in htmlx.split("$"):
        if "#LoginForm-p" in line:
            code=str(line.split(".")[0].split("-")[-1].split("'")[0])
            break
    return code

def login_srs(id_num,id_password):
    global driver,options
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(executable_path=r'geckodriver.exe',options=options)
    driver.get("https://stars.bilkent.edu.tr/srs")
    username = driver.find_element_by_name("LoginForm[username]")
    username.send_keys(str(id_num))
    code=get_code(driver)
    password = driver.find_element_by_name("LoginForm["+str(code)+"]")
    password.send_keys(str(id_password))
    username.submit()

def sms_or_mail(email,password):
    girdi=input("Press M for mail, S for sms. Default is mail. Choice: ")
    time.sleep(10)
    if girdi.upper()=="S":
        redirect_sms_verify()
    else:
        redirect_email_verify(email,password)
    
def redirect_email_verify(email,password):
    time.sleep(1)
    driver.get("https://stars.bilkent.edu.tr/accounts/site/switchVerification?type=P")
    verify_code=get_mail_code(email,password)
    mail = driver.find_element_by_name("EmailVerifyForm[verifyCode]")
    mail.send_keys(str(verify_code))
    mail.submit()
    
def redirect_sms_verify():
    smscode = driver.find_element_by_name("SmsVerifyForm[verifyCode]")
    girdi=input("Enter sms code: ")
    smscode.send_keys(str(girdi))
    smscode.submit()
    
def login_mail(email,password):
    global browser
    browser = webdriver.Firefox(executable_path= os.getcwd()+"\\geckodriver.exe",options=options)
    # browser = webdriver.Firefox(executable_path=r'C:\Users\yakupcatalkaya\Downloads\geckodriver.exe',options=options)
    browser.get("https://webmail.bilkent.edu.tr/")
    mail_id = browser.find_element_by_name("_user")
    mail_id.send_keys(str(email))
    code=get_code(browser)
    mail_psswd = browser.find_element_by_name("LoginForm["+str(code)+"]")
    mail_psswd.send_keys(str(password))
    mail_id.submit()

def get_mail_code(email, password):
    login_mail(email, password)
    time.sleep(5)
    browser.get("https://webmail.bilkent.edu.tr/?_task=mail&_action=list&_refresh=1&_layout=widescreen&_mbox=INBOX&_remote=1&_unlock=loading1600602526707&_=1600602525979")
    htmlxxx=browser.page_source
    anum=htmlxxx.split("this.add_message_row(")[1].split(",")[0]
    browser.get("https://webmail.bilkent.edu.tr/?_task=mail&_mbox=INBOX./?_task=mail&_mbox=INBOX&_uid="+str(anum)+"&_action=show")
    htmlxx = browser.page_source
    for line in htmlxx.split(">"):
        if "Verification Code:" in line:
            code=str(line.split(":")[1].split()[0])
            break
    time.sleep(2)
    browser.close()
    return code

def get_zoom_links(urlist):
    zoomlink=[]
    time.sleep(2)
    for url in urlist:
        newhtml=""
        templist=[]
        driver.get(url)
        day,month=url.split("/")[-1].split(".")[:-1]
        times=str(day)+"/"+str(month)
        html=driver.page_source
        if "Invalid date given" in html:
            continue
        for line in html.split("<tr>"):
            if "background-color" in line:
                newhtml+=line
        for line in newhtml.split("<td"):
            if "bold text-center bg-warning" in line:
                hour=line.split(">")[1].split("<")[0]
                templist.append(hour)
        for line in newhtml.split("<div"):
            if "pull-left" in line:
                if "zoom" in line:
                    for xline in line.split('href="'):
                        if "zoom" in xline:
                            link=str(xline.split('"')[0])                            
                            templist.append(link)                            
                        elif "<br>" in xline:
                            course_name=xline.split("<br>")[0].split(">")[1]
                            templist.append(course_name)
                                        
                if "Zoom button since classroom is not defined" in line:
                    templist.append(link)
        templist.append(times)
        zoomlink.append(templist)
    return zoomlink

def editor(list1):    #[[day,[hour,course,link]],[day2,[hour,course,link]]]
    final_list=[]
    for alist in list1:
        newlist=[]
        day=alist[-1]
        dayless_list=alist[:-1]
        seperator=len(dayless_list)//3
        timelist=dayless_list[:seperator]  
        count=0
        rest_list=dayless_list[seperator:]
        for item in rest_list:
            if count%2==0:
                item2=item
                count+=1
            else:
                item3=item    
                newlist.append([timelist[count//2],item2,item3])
                count+=1
        final_list.append([day,newlist])
    return final_list
    
def program_send_via_whstpp(phone_num,list1):
    text=""
    for alist in list1[0][1:][0]:
        text+=str(alist[0])+" saatleri arasındaki "
        text+=str(alist[1])+"dersine katılmak icin "+str(alist[2])
        text+="  linkine tıklayınız."
        text+="%0A"
        text+="-"*50
        text+="%0A"
    web.open_new('https://web.whatsapp.com/send?phone='+phone_num+'&text='+text)
    time.sleep(15)
    press('enter')

def get_input():
    a=input("Where can the program get your info (file/typing): ").lower()
    if a=="typing":
        srs_id=input("Student number: ")
        srs_psswd=input("SRS password: ")
        email_id=input("Student mail: ")
        email_psswd=input("Mail password: ")
        phone_num=input("Phone number: ")
    else:
        alist=[]
        txt=open("your_info.txt",'r')
        for line in txt:
            if "\n" in line: 
                alist.append(line[:-1])
            else:
                alist.append(line)         
        srs_id,srs_psswd,email_id,email_psswd,phone_num=alist
    print("\n\n"+"_"*93+"\n\n")
    print("Initializing program...")
    return srs_id,srs_psswd,email_id,email_psswd,phone_num

def program():
    srs_id,srs_psswd,email_id,email_psswd,phone_num=get_input()
    login_srs(srs_id,srs_psswd)
    redirect_email_verify(email_id,email_psswd)
    time.sleep(2)
    driver.get("https://stars.bilkent.edu.tr/srs-v2/schedule/index/daily")
    year,month,day=time.strftime("%Y %m %d").split()
    aurl="https://stars.bilkent.edu.tr/srs-v2/schedule/index/daily/date/"+str(day)+"."+str(month)+"."+str(year)
    url=[aurl]
    alist=get_zoom_links(url)
    driver.close()
    ultimate_list=editor(alist)
    program_send_via_whstpp(phone_num,ultimate_list)
    
def main():
    print("\n\n\n______________________________________ SRS LOGIN ____________________________________________")
    print("                                                                       | CREATED BY MRJACOB |") 
    program()
    print("Log file has been deleted...")
    print("Program has finished. Aborting...")
    time.sleep(3)
    return 0

main()


