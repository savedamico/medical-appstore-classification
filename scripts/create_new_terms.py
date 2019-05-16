##CREATE NEW TERMS

#import libraries
import xml.etree.ElementTree
import re

def stripString(pref_str):
    return pref_str
    i = pref_str
    i = re.sub(r'\([^)]*\)', '', i).strip()
    i = re.sub(r'\-[^-]*$', '', i).strip()
    i = re.sub(r'\,[^,]*$', '', i).strip()
    return i

# Parses XML file and puts CandidatePreferred into a list ordered as they are read in the xml
def parseXML(filename = '10apps_xml_out.txt'):
    root = xml.etree.ElementTree.parse(filename).getroot()
    my_dict = []
    pmids = {}
    index = 0
    for utterance in root.findall('MMO/Utterances/Utterance'):
        candPrefMapping = "Phrases/Phrase/Mappings/Mapping/MappingCandidates/Candidate/CandidatePreferred"
        for candPref in utterance.findall(candPrefMapping):
            pmid = utterance.find("PMID").text

            cpt = stripString( candPref.text )

            if pmid in pmids:
                my_dict[index-1].append(cpt)
            else:
                pmids[pmid] = None
                my_dict.append([cpt])
                index += 1

    return my_dict

d = parseXML("mesh_terms_metamap.out ")

orderedFiles = ['Surgery.txt',
                'Oncology.txt',
                'Cardiology.txt',
                'Pediatrics.txt',
                'DiabetesCare.txt',
                'Endocrinology.txt',
                'SensorySystemsHealthcare.txt',
                'EmergencyMedicine.txt',
                'Nutrition.txt',
                'Gastroenterology.txt',
                'Dentistry.txt',
                'Dermatology.txt',
                'GinecologyAndObstetrics.txt',
                'SleepAndRespiratoryCare.txt',
                'MentalHealth_Neurology.txt']

fileIndexCandidates = {}

for i in range(len(d)):
    fileIndexCandidates[orderedFiles[i]] = d[i]

#write new files
newDir = "MeSH_terms_Candidatepreferred/"

for key in fileIndexCandidates:
    with open(newDir + key, 'w') as f:
        writeString = ""
        for line in set(fileIndexCandidates[key]):
            writeString += line + "\n"
        f.write(writeString)
