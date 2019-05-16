##EXCEL TO METAMAP

#import libraries
import pandas as pd
import re

#open excel with the attributes list
fil='TT_myhealthapps.xlsx'
excel=pd.ExcelFile(fil)
df=excel.parse('Sheet1')

#extract attributes from excel and write into a txt file
descText=''

for desc, name, summ in zip(df.Desc, df.Name, df.Sum):
    name=str(name)
    name=name.strip(" ")
    desc=str(desc)
    desc=desc.strip(" ")
    summ=str(summ)
    summ=summ.strip(" ")

    descText += name + "| " + name + " " + desc + " " + summ + "\n"

#save txt file
with open('TTdescText.txt', 'w') as f:
    f.write(descText)
