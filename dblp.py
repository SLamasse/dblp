# -*- coding: utf-8 -*-
import os
import sys
import requests
import json
import csv

def rechercheapi(nbresult, outformat, search, first=None, year=None):
    #
    if year is not None and first is not None: 
        query = "https://dblp.uni-trier.de/search/publ/api?q=\""+ search +"\" year:" + str(year) + "&f=" + str(first) + "&h=" + str(nbresult) +"&format=" + outformat
    elif year is not None :
        query = "https://dblp.uni-trier.de/search/publ/api?q=\""+ search +"\" year:" + str(year) + "&h=" + str(nbresult) +"&format=" + outformat
    else:
        query = "https://dblp.uni-trier.de/search/publ/api?q=\""+ search +"\"&f=" + str(first) + "&h=" + str(nbresult) +"&format=" + outformat

    resp = requests.get(url=query)
    data = resp.json()
    #print(query)
    return data



def parsejson(res):
    # Il faut introduire les tests 
    reference = []
    auteurs = []
    for elt in res['result']['hits']['hit'] :
        iddblp = elt['@id']
        if 'title' not in elt['info']:
            title = "pas de titre"
        else:
            title =  elt['info']['title']
        if 'ee' not in elt['info']:
            doi = "pas de doi"
        else:
            doi = elt['info']['ee']
        if 'pages' not in elt['info']:
            pages = "pas de pages"
        else:
            pages = elt['info']['pages']
            
        annee = elt['info']['year']
        typeref = elt['info']['type']
        try :
            authors = elt['info']['authors']
            for k,v in authors.items():
                if isinstance(v, list):
                    for elt in v:
                        pid = elt['@pid']
                        a, b = pid.split("/")
                        name = elt['text']
                        pageperson = "https://dblp.uni-trier.de/pid/" + a +"/"+ b +".html"
                        auteurs.append([iddblp, name, pageperson])
                else:
                    pid = v['@pid']
                    a, b = pid.split("/")
                    name = v['text']
                    pageperson = "https://dblp.uni-trier.de/pid/" + a +"/"+ b +".html"
                    auteurs.append([iddblp, name, pageperson])
        except:
            pass
        reference.append([iddblp, title, annee, typeref, pages, doi])
    return reference, auteurs


## Alors pour décomposer le travail on fait année par année, on débute dès 1950
authors = []
reference = []
length = len(sys.argv);                   #Je regarde le nombre d'arguments
if length >= 5:                           #S'il y en a plus de 4, je prends le range
    mini = int(sys.argv[3])
    maxi = int(sys.argv[4])
else :                                    #Sinon, je mets la valeur par defaut
    mini = 1955
    maxi = 2023
if length >= 3:                           #Pareil avec le nombre par année
    nb = sys.argv[2]
else :
    nb = "10"
if length >= 2 :                          #Et pour le mot clef
    search = sys.argv[1]
else :
    search = input("Mot clef : ")         #Si je ne l'ai pas, je le demande dans le terminal


for a in range(mini,maxi):
    # mini et maxi sont ici les deux années entre lesquelles on veut
    # interroger dblp
    outformat = "json"
    res1 = rechercheapi(nb, outformat, search, first="0", year=a)
    total = res1['result']['hits']['@total']
    fi = int(total)
    i = 0
    # On cherche les milliers et le reste
    q, r = divmod(fi,1000)
    if q== 0 and r ==0 :
        pass
    else:
       while (i <= q):
           # f : c'est le nombre du début de la liste de chaque retour
           # r : c'est le nombre de référence dans chaque retour
           f = (i * 1000)
           if i == q : 
                nb = r
           else :
               nb = 1000
           res = rechercheapi(nb, outformat, search, first=f, year=a)
           mylistref = parsejson(res)
           reference.append(mylistref[0])
           authors.append(mylistref[1])
           i += 1



out = search + "_parsed_data.csv"
with open(out, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile, quoting=csv.QUOTE_ALL,delimiter=';')
    for elt in reference:
        writer.writerows(elt)

out = search + "_authors.csv"
with open(out, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile, quoting=csv.QUOTE_ALL,delimiter=';')
    for elt in authors:
        writer.writerows(elt)
