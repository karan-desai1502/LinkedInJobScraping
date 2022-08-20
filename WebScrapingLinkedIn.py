# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 17:05:42 2022

@author: Karan Desai
"""
# import section
import requests
import bs4
import lxml
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import codecs

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
cats=""
titles=""
for j in soup.select('div.col-md-4 h2'):
    for i in j.next_sibling.children:
        #print(j.getText()+"->"+i.findAll('a')[0].getText())
        cats+=j.getText()+"->"+i.findAll('a')[0].getText()+"\n"
        titles+=i.findAll('a')[0].getText()+"\n"
#print(cats)
file.write(cats)
file2.write(titles)
file.close()
file2.close()

'''
Part 2: Searching for jobs on LinkedIn using the JobTitles.txt
        and scraping Job Title, Company Name and Location
'''

file=open("JobTitles.txt",'r',encoding="utf-8")
title=str(file.read())
title=title.split('\n')
file.close()

driver = webdriver.Firefox() #initialize Selenium webdriver

searchterm=title[0] #obtain the job title to search for, can be iterated for all titles

#using the searchterm in the url query
driver.get(f"https://in.linkedin.com/jobs/search?keywords={searchterm}&location=Bengaluru%2C%20Karnataka%2C%20India&geoId=105214831&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0")

page_source=driver.page_source #obtaining the page source

lsoup = BeautifulSoup(page_source,features="html.parser")
text_titles=""
text_companies=""
text_locations=""
for i in lsoup.select('.base-search-card__info '):
    t=i.contents[1].contents[0].strip()+"\n"
    text_titles+=t
    #print(t)
    try:
        comp=i.contents[3].contents[1].contents[0].strip()+"\n"
        text_companies+=comp
        #print(comp+"\n")
    except:
        comp=i.contents[3].contents[0].strip()+"\n"
        text_companies+=comp
        #print(comp+"\n")
        continue
for i in lsoup.select('.job-search-card__location'):
    text_locations+=i.getText().strip()+"\n"

text_titles=text_titles.split("\n")
text_companies=text_companies.split("\n")
text_locations=text_locations.split("\n")

file3=open("LinkedinJobs.txt",'w',encoding='utf-8')
for i in range(0,len(text_titles)):
    file3.write(text_titles[i]+"\n"+text_companies[i]+"\n"+text_locations[i]+"\n")
file3.close()

file4=open("JobLinks.txt","w",encoding='utf-8')
for i in lsoup.select('.hidden-nested-link'):
    file4.write(i['href']+"\n")
file4.close()

'''
    Part 3: Search for the same companies and scrape their details
'''

file4=open("JobLinks.txt",'r',encoding='utf-8')
links=str(file4.read())
links=links.split("\n")

driver.get(f"{links[0]}")
page_source=driver.page_source

lsoup = BeautifulSoup(page_source,features="html.parser")

file5=open("JobDesc.txt",'w',encoding='utf-8')
desc="Description:"+lsoup.select('.about-us__description')[0].getText()
loc="Location:"+lsoup.select('dd.font-sans.text-md.text-color-text.break-words.overflow-hidden')[3].getText().strip()
emp="Employees:"+lsoup.select('dd.font-sans.text-md.text-color-text.break-words.overflow-hidden')[2].getText().strip()
file5.write(desc+"\n")
file5.write(loc+"\n")
file5.write(emp+"\n")
file5.close()



