##COMPUTE CATEGORIZE

#import libraries
import re
from os import walk
import xml.etree.ElementTree

def stripString(pref_str):
    return pref_str
    i = pref_str
    i = re.sub(r'\([^)]*\)', '', i).strip()
    i = re.sub(r'\-[^-]*$', '', i).strip()
    i = re.sub(r'\,[^,]*$', '', i).strip()
    return i

# Listing all MeSH terms files in the dir "MeSH_terms_list/"
def getFilesInDir(terms_dir):
    f = []
    for (dirpath, dirnames, filenames) in walk(terms_dir):
        f.extend(filenames)
        break
    return f

# Reads all above files into a dict:
def loadTermsFiles(terms_dir = "MeSH_terms_list/"):
    f = getFilesInDir(terms_dir)

    terms_files = {}

    for i in range(len(f)):
        if f[i].endswith(".txt"): # Removing files that doesn't end with ".txt"
            terms_files[f[i]] = []
            with open(terms_dir + f[i]) as fobj:
                for line in fobj:
                    ls = line.split("|")
                    if len(ls) > 1:
                        terms_files[f[i]].append( ls[1].strip())
                    else:
                        terms_files[f[i]].append( line.strip())
    return terms_files

# Compares preferred words with terms files and prints matching terms for each file
def matchPrefWithTerms(terms_files, pref_cleaned):

    # Extracting the terms list and score list from dictionary in pref_cleaned
    cand_list = []
    score_list = []

    for cand_dict in pref_cleaned:
        cand = cand_dict.keys()[0]

        cand_list.append(cand)
        score_list.append(cand_dict[cand])

    b = cand_list

    file_matches = {}
    for filename in terms_files:
        a = terms_files[filename]
        matches = set(a).intersection(b)

        if bool(matches):
            file_matches[filename] = []
            for e in matches:
                # Calculate score
                score = 0
                for i in range(len(cand_list)):
                    if cand_list[i] == e:
                        score += score_list[i]

                file_matches[filename].append({e: {"score":score, "count": cand_list.count(e)} })

    if file_matches:
        return file_matches
    else:
        return None

#chek for acronym
def check_if_acronym(word):
    if word.isupper() and len(word) < 5:
        return True
    return False

#chek for eventually useless words
def parseXML(xmlFile = '10apps_xml_out.txt'):
    useless_words = [] #for eventually useless words (used for debugging)
    root = xml.etree.ElementTree.parse(xmlFile).getroot()
    my_dict = {}

    for utterance in root.findall('MMO/Utterances/Utterance'):
        pmid = utterance.find("PMID").text

        for cand in utterance.findall("Phrases/Phrase/Mappings/Mapping/MappingCandidates/Candidate"):

            candPref = cand.find("CandidatePreferred")
            candMatch = cand.find("CandidateMatched")
            candScore = cand.find("CandidateScore")

            score = int(candScore.text[1:])
            cpt = stripString( candPref.text )

            # Skip if candidate is a useless word or an acronym
            if cpt.lower() in useless_words or check_if_acronym(candMatch.text):
                continue

            if pmid in my_dict:
                my_dict[pmid].append({cpt:score})
            else:
                my_dict[pmid] = [{cpt:score}]

    return my_dict

# Viewing extracted information (for debugging)
my_dict = parseXML("TotalApp_metamap.out")

for key in my_dict:
    for i in my_dict[key]:
        term = i.keys()[0]
        score = i[term]

# Filtering low score (for debugging)
filter_threshold = 0

# If score is less than threshold then disregard
my_dict_filtered = {}
for app_id in my_dict:
    my_dict_filtered[app_id] = []
    for i in my_dict[app_id]:

        term = i.keys()[0]
        score = i[term]
        if score < filter_threshold:
            continue

        my_dict_filtered[app_id].append({term:score})

# Printing the filtered dictionary (for debugging)
for key in my_dict_filtered:
    for i in my_dict_filtered[key]:
        term = i.keys()[0]
        score = i[term]


MeSH_terms = loadTermsFiles("MeSH_terms_Merged/")


multi_prefs = my_dict_filtered

matches = {}
for app in multi_prefs:
    pref_cleaned = multi_prefs[app]
    matches[app] = matchPrefWithTerms(MeSH_terms, pref_cleaned)


# compiling score_dict with all scores, values and categories for each app
score_dict = {}
topolino=0
paperino=0

for appid in matches:
    if matches[appid]:

        score_dict[appid] = {'categories':[],
                             'total_score':0}

        rows = []

        for term_file in matches[appid]:
            score = 0
            count = 0

            perc_max=0
            terms = []

            for term in matches[appid][term_file]:

                for key in term:
                    score = term[key]["score"]
                    count = term[key]["count"]
                    terms.append(key)

                    topolino= topolino + score  #score effettive
                    paperino=paperino+ count*1000 #score max if all match are 1000

            perc_bon=100* (float(topolino)/float(paperino)) #quality of category for one app
            perc_bon=int(perc_bon)
            terms_category = term_file.split(".")[0]
            rows.append({'matched_terms': term, 'score':topolino, 'count':count, 'scoreByCount':paperino, "category":terms_category,"percentage":perc_bon})
            score_dict[appid]['total_score'] += score
            topolino=0
            paperino=0

        for row in rows:
            total_score = score_dict[appid]['total_score']
            score = row["score"]
            count = row["count"]
            row["scoreTotalFraction"] = round(float(score)/total_score, 2)
            row["sbcMsf"] = round(float(score/count) * float(score)/total_score, 2)
            score_dict[appid]['categories'].append(row)
    else:
        score_dict[appid] = None


# Filtering and selecting best candidate categories:
colAppid = []
colCat1 = []
colCat2 = []

for appid in score_dict:

    colAppid.append(appid)

    #for not medical step1
    if score_dict[appid] == None:
        colCat1.append("Not medical")
        colCat2.append("None")
    else:
        stf_max = 0
        cat1stf = 0
        cat2stf = 0
        cat1row = None
        cat2row = None
        n_categories=0

        for row in score_dict[appid]['categories']:

            cat = row["category"]

            #number of words for the merged MeSH terms files (parameter Q)
            if cat=="Cardiology": pippo=1983
            if cat=="Dentistry": pippo=211
            if cat=="Dermatology": pippo=1003
            if cat=="DiabetesCare": pippo=88
            if cat=="EmergencyMedicine": pippo=35
            if cat=="Endocrinology": pippo=534
            if cat=="Gastroenterology": pippo=557
            if cat=="GinecologyAndObstetrics": pippo=1181
            if cat=="MentalHealth_Neurology": pippo=3931
            if cat=="Nutrition": pippo=445
            if cat=="Oncology": pippo=1841
            if cat=="Pediatrics": pippo=40
            if cat=="SensorySystemsHealthcare": pippo=1290
            if cat=="SleepAndRespiratoryCare": pippo=15
            if cat=="Surgery": pippo=1654

            topolino = row['score']
            paperino = row['scoreByCount']
            perc=row['percentage']
            bon=float(perc)/100
            cat = row["category"] #category name
            stf=(float(topolino)/float(pippo))*(float(bon)) #parameters for classify

            if stf > 4 and perc > 60 : #filter category with stf > 4 (not medical step2)

                if cat1stf < stf:
                    cat2row = cat1row
                    cat2stf = cat1stf
                    cat1stf = stf
                    cat1row = row
                elif cat2stf < stf:
                    cat2stf = stf
                    cat2row = row

                n_categories=n_categories+1

        #for eventually accorss species
        if n_categories>6:
            colCat1.append("**DICTIONARY or NOT SPECIFY**")
            colCat2.append("None")

        #also not medical step2
        elif n_categories==0:
            colCat1.append("Not medical")
            colCat2.append("None")

        else:
            if cat1row:
                colCat1.append(cat1row["category"])
            else:
                colCat1.append("None")

            if cat2row:
                colCat2.append(cat2row["category"])
            else:
                colCat2.append("None")


#save excel
import pandas as pd

#create a Pandas dataframe from some data.
df = pd.DataFrame({'appid': colAppid, 'class1':colCat1, 'class2':colCat2})

#create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('TotalApp_automatic_classification.xlsx', engine='xlsxwriter')

# convert the dataframe to an XlsxWriter Excel object.
df.to_excel(writer, sheet_name='Sheet1')

# close the Pandas Excel writer and output the Excel file.
writer.save()
