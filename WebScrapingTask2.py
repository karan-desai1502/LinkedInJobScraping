# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 17:25:43 2022

@author: Karan Desai
"""

import requests
import bs4
import lxml
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import codecs
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="De$ai6915",
  database="JobScraperDB"
)

mycursor = mydb.cursor()

"""
Part 1: Scraping Careers from carrerguide.com in the form subcategory->job
        it is saved in 2 text files, 
        JobCat.txt - contains the category->job
        JobTitles.txt - contains the job titles used for Part 2
"""
res=requests.get("https://www.careerguide.com/career-options")
soup=bs4.BeautifulSoup(res.text,"lxml") #soup object

file=open("JobCat.txt",'w', encoding="utf-8")
file2=open("JobTitles.txt",'w', encoding='utf-8')

cquery="insert into jobcat(Categories) values(%s)"
cats=""
squery="insert into jobsubcat(Subcategories,JobCat_Categories) values(%s,%s)"
titles=""

for j in soup.select('div.col-md-4 h2'):
    cats+=j.getText()+"\n"
    cval=(j.getText(),)
    try:
        mycursor.execute(cquery,cval)
    except:
        pass
    mydb.commit()
    for i in j.next_sibling.children:
        #print(j.getText()+"->"+i.findAll('a')[0].getText())
        titles+=i.findAll('a')[0].getText()+"\n"
        sval=(i.findAll('a')[0].getText(),j.getText())
        try:
            mycursor.execute(squery,sval)
        except:
            pass
        mydb.commit()
#print(cats)
mycursor.execute(squery,('Software Engineer','Engineering & Technology'))
mydb.commit()
file.write(cats)
file2.write(titles)
file.close()
file2.close()

'''
Part 2: Searching for jobs on LinkedIn using the JobTitles.txt
        and scraping Job Title, Company Name and Location
'''

#file=open("JobTitles.txt",'r',encoding="utf-8")
#title=str(file.read())
#title=title.split('\n')
#file.close()

#Instead of fetching the titles from files, I make use of the DB.

mycursor.execute("select subcategories from jobsubcat")
myres=mycursor.fetchall()
ls=myres

driver = webdriver.Firefox() #initialize Selenium webdriver

'''for i in ls:
        searchterm=i[0]   
        //This is how one would iterate over all the rows returned by the SQL Query.
        //I will demonstrate for only one so as to not get my IP blocked.                    
'''
searchterm=ls[0][0] #obtain the job title to search for, can be iterated for all titles
searchterm="Software Engineer"

driver.get(f"https://in.linkedin.com/jobs/search?keywords={searchterm}&location=Bengaluru%2C%20Karnataka%2C%20India&geoId=105214831&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0")

page_source=driver.page_source #obtaining the page source

lsoup = BeautifulSoup(page_source,features="html.parser")
lquery="insert into states(state) values(%s)"
cquery="insert into company(name,states_state,link) values(%s,%s,%s)"
jquery="insert into jobs(jobpos,company_name,company_states_state) values(%s,%s,%s)"
csquery="insert into company_has_jobsubcat(JobSubCat_Subcategories,Company_Name) values(%s,%s)"
text_titles=""
text_companies=""
text_locations=""
text_links=""
for i in lsoup.select('.job-search-card__location'):
    text_locations+=i.getText().strip()+"\n"
    
for i in lsoup.select('.base-search-card__info '):
    t=i.contents[1].contents[0].strip()+"\n"
    text_titles+=t
    #print(t)
    try:
        comp=i.contents[3].contents[1].contents[0].strip()+"\n"
        text_companies+=comp
        text_links+=i.find_all('a')[0]['href']+"\n"
        #print(comp+"\n")
    except:
        comp=i.contents[3].contents[0].strip()+"\n"
        text_companies+=comp
        text_links+="NULL"+"\n"
        #print(comp+"\n")
        continue

for i in lsoup.select('.hidden-nested-link'):
    text_links+=i['href']+"\n"
    
text_links=text_links.split("\n")
text_titles=text_titles.split("\n")
text_companies=text_companies.split("\n")
text_locations=text_locations.split("\n")

for i in range(0,len(text_titles)):
    lval=(text_locations[i],)
    cval=(text_companies[i],text_locations[i],text_links[i])
    jval=(text_titles[i],text_companies[i],text_locations[i])
    csval=(searchterm,text_companies[i])
    try:
        mycursor.execute(lquery,lval)
    except:
        pass
    mydb.commit()
    try:
        mycursor.execute(cquery,cval)
    except:
        pass
    mydb.commit()
    try:
        mycursor.execute(jquery,jval)
    except:
        pass
    mydb.commit()
    try:
        mycursor.execute(csquery,csval)
    except:
        pass
    mydb.commit()


'''
    Part 3: Search for the same companies and scrape their details
'''

mycursor.execute("select link from company")
myres=mycursor.fetchall()
ls=myres
#driv=webdriver.Firefox()
dquery="insert into company(desc) values(%s) where company.link={0}".format(ls[0][0])
res=requests.get("https://in.linkedin.com/company/stockgro?trk=public_jobs_jserp-result_job-search-card-subtitle")
print(ls[0][0])
page_source=driver.page_source
lsoup = bs4.BeautifulSoup(res.text,"lxml")
print(lsoup)
desc="Description:"+lsoup.select('.about-us__description')[0].getText()
dval=desc
mycursor.execute(dquery,dval)
mydb.commit()