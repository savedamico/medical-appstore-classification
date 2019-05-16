##CREATE LIST URL

#import libraries
from bs4 import BeautifulSoup
import urllib2
import re


html_mainpage = urllib2.urlopen("http://myhealthapps.net/language/show/12/english")
soup = BeautifulSoup(html_mainpage, "lxml")
temp_links = []
apps_number=0

#search for the link of every application in the html page
for link in soup.findAll('a', attrs={'href': re.compile("^/app/details/")}):
    temp_links.append(link.get('href'))
    apps_number=apps_number+1 #for check the correct number of apps

#deletes the link duplicate
temp_links=set(temp_links)
seen=set()
links=[]
for item in temp_links:
    if item not in seen:
        seen.add(item)
        links.append(item)

apps_number=len(links)

#add this for complete the link
string="http://myhealthapps.net"
real_links=[]

for link in links:
    tmp = string + link
    real_links.append(tmp)

#create the excel file with all the links
import pandas as pd
excel = pd.DataFrame({'app_url': real_links})

#save file
writer = pd.ExcelWriter('listURL_myhealthapps.xlsx', engine='xlsxwriter')
excel.to_excel(writer, sheet_name='Sheet1')
writer.save()
