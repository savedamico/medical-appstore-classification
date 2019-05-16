##EXTRACT ATTRIBUTES

#import libraries
from bs4 import BeautifulSoup
import urllib2
import re
import pandas as pd

#open excel with the URLs list
file_name='TT_listURL.xlsx'
excel=pd.ExcelFile(file_name)
links=excel.parse('Sheet1')

#select app's attributes
appName=[]
appDesc=[]
appSum=[]
n=0 #check the correct app number

for link in links.app_url:

    APP_NAME=[]
    DESCRIPTION=[]
    SUMMARY=[]
    tmp=''

    html_page = urllib2.urlopen(link)
    soup = BeautifulSoup(html_page, "lxml")

    #extract app name
    APP_NAME = soup.find("strong").get_text()
    name=APP_NAME.encode('ascii','ignore')
    name=str(name)
    name=name.strip()

    #extrct description
    DESCRIPTION = soup.find("div", class_='span4', style='text-align: left; margin-top: 10px;').get_text()

    #delete app with this symbol in the description
    if 'X' in DESCRIPTION:
        DESCRIPTION = soup.find_all("div", class_='span4', style='text-align: left; margin-top: 10px;')
        for i in DESCRIPTION:
            tag = i.find('p')
            if not tag==None:
                text=tag.get_text()
                DESCRIPTION=text.encode('ascii','ignore')
                DESCRIPTION=str(DESCRIPTION)
                desc=DESCRIPTION.strip()
    else:
        DESCRIPTION=DESCRIPTION.encode('ascii','ignore')
        DESCRIPTION=str(DESCRIPTION)
        desc=DESCRIPTION.strip()

    #extract summary
    div = soup.find_all("div", class_="span6")
    for span in div:
        labels = span.find_all("h3")
        clab = None

        for i in span.children:
            #create clab as lables list
            if i in labels:
                clab=i
                continue

            #take only text in labels
            if clab:

                #chose only the specify labels
                lab=clab.get_text()
                if lab=="Summary":
                    if i.name=="p":
                        tag=i.find("br")
                        if tag==None:
                            text=i
                            for i in text:
                                SUMMARY=i
                                SUMMARY=SUMMARY.encode('ascii','ignore')
                                SUMMARY=str(SUMMARY)
                                summ=SUMMARY.strip()
                                tag=i.find('br')
                                if not tag==None:
                                    SUMMARY=i
                                    SUMMARY=SUMMARY.encode('ascii','ignore')
                                    SUMMARY=str(SUMMARY)
                                    summ=SUMMARY.strip()
                                break

                    if SUMMARY==[]:
                        #show text without any tag
                        tag=i.find("Summary")
                        if not tag==1 and not tag== None:
                            SUMMARY=i
                            SUMMARY=SUMMARY.encode('ascii','ignore')
                            SUMMARY=str(SUMMARY)
                            summ=SUMMARY.strip()
                            continue

    name=name.lstrip()
    desc=desc.lstrip()
    summ=summ.lstrip()
    n=n+1

    appName.append(name)
    appDesc.append(desc)
    appSum.append(summ)

#create excel with app's attribute
excel=pd.DataFrame({'Name': appName,'Desc':appDesc,'Sum':appSum})

#save excel
import pandas as pd

writer = pd.ExcelWriter('TT_myhealthapps.xlsx', engine='xlsxwriter')
excel.to_excel(writer, sheet_name='Sheet1')
writer.save()
