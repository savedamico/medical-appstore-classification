##CREATE MERGED TERMS

#import libraries
from os import walk

terms_dir = "MeSH_terms_list/" #change every time manually
def loadTermsFiles(terms_dir):
    f = []

    for (dirpath, dirnames, filenames) in walk(terms_dir):
        f.extend(filenames)
        break

    terms_files = {}

    for i in range(len(f)):
        if f[i].endswith(".txt"): # Removing files that doesn't end with ".txt"
            terms_files[f[i]] = []
            with open(terms_dir + f[i]) as fobj:
                for line in fobj:
                    term = line.split("|")[1].strip()
                    terms_files[f[i]].append( term )
    return terms_files

tf = loadTermsFiles("MeSH_terms_list/")
filestring = ""

orderedFiles = []

for fn in tf:
    orderedFiles.append(fn)

    for term in tf[fn]:
        sterm = term.split(",")
        if len(sterm) > 1:
            cterm = sterm[-1].strip() + " " + " ".join(sterm[:-1])
        else:
            cterm = term
        filestring += cterm + ",\n"
    filestring += "\n"
    filestring=filestring.replace(',','')
