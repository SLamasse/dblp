# -*- coding: utf-8 -*-
import os
import sys
import requests
import json
import csv
import time

def rechercheapi(nbresult, outformat, search, first=None, year=None):
    max_retries = 5  # Nombre maximum de tentatives en cas d'erreur 429
    retry_delay = 2  # Délai initial en secondes entre les tentatives

    for attempt in range(max_retries):
        try:
            if year is not None and first is not None:
                query = f"https://dblp.uni-trier.de/search/publ/api?q=\"{search}\" year:{year}&f={first}&h={nbresult}&format={outformat}"
            elif year is not None:
                query = f"https://dblp.uni-trier.de/search/publ/api?q=\"{search}\" year:{year}&h={nbresult}&format={outformat}"
            else:
                query = f"https://dblp.uni-trier.de/search/publ/api?q=\"{search}\"&f={first}&h={nbresult}&format={outformat}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            resp = requests.get(url=query, headers=headers)
            resp.raise_for_status()  # Lève une exception si la requête échoue
            data = resp.json()
            return data
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 429:  # Too Many Requests
                print(f"Trop de requêtes. Attente de {retry_delay} secondes avant de réessayer...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Délai exponentiel
            else:
                print(f"Erreur HTTP : {e}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Erreur de décodage JSON : {e}")
            return None

    print("Nombre maximum de tentatives atteint. Abandon.")
    return None

def parsejson(res):
    reference = []
    auteurs = []
    if 'result' not in res or 'hits' not in res['result'] or 'hit' not in res['result']['hits']:
        return reference, auteurs

    for elt in res['result']['hits']['hit']:
        iddblp = elt.get('@id', 'N/A')
        title = elt['info'].get('title', 'pas de titre') if 'info' in elt else 'pas de titre'
        doi = elt['info'].get('ee', 'pas de doi') if 'info' in elt else 'pas de doi'
        pages = elt['info'].get('pages', 'pas de pages') if 'info' in elt else 'pas de pages'
        annee = elt['info'].get('year', 'N/A') if 'info' in elt else 'N/A'
        typeref = elt['info'].get('type', 'N/A') if 'info' in elt else 'N/A'

        if 'authors' in elt['info']:
            authors = elt['info']['authors']
            if isinstance(authors, dict):
                for k, v in authors.items():
                    if isinstance(v, list):
                        for author in v:
                            pid = author.get('@pid', 'N/A')
                            name = author.get('text', 'N/A')
                            if pid != 'N/A':
                                a, b = pid.split("/")
                                pageperson = f"https://dblp.uni-trier.de/pid/{a}/{b}.html"
                                auteurs.append([iddblp, name, pageperson])
                    else:
                        pid = v.get('@pid', 'N/A')
                        name = v.get('text', 'N/A')
                        if pid != 'N/A':
                            a, b = pid.split("/")
                            pageperson = f"https://dblp.uni-trier.de/pid/{a}/{b}.html"
                            auteurs.append([iddblp, name, pageperson])

        reference.append([iddblp, title, annee, typeref, pages, doi])
    return reference, auteurs

# Vérification des arguments
if len(sys.argv) < 2:
    search = input("Mot clef : ")
else:
    search = sys.argv[1]

nb = int(sys.argv[2]) if len(sys.argv) >= 3 else 10
mini = int(sys.argv[3]) if len(sys.argv) >= 4 else 1955
maxi = int(sys.argv[4]) if len(sys.argv) >= 5 else 2023

# Créer le répertoire "results" s'il n'existe pas
results_dir = "results"
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# Boucle principale
for a in range(mini, maxi):
    # Vérifier si les fichiers existent déjà
    parsed_data_file = os.path.join(results_dir, f"{search}_{a}_parsed_data.csv")
    authors_file = os.path.join(results_dir, f"{search}_{a}_authors.csv")

    if os.path.exists(parsed_data_file) and os.path.exists(authors_file):
        print(f"Les fichiers pour l'année {a} existent déjà. Passage à l'année suivante.")
        continue

    reference = []
    authors = []
    outformat = "json"
    res1 = rechercheapi(nb, outformat, search, first="0", year=a)
    if res1 is None:
        continue

    total = int(res1['result']['hits'].get('@total', 0))
    if total == 0:
        continue

    q, r = divmod(total, 1000)
    for i in range(q + 1):
        f = i * 1000
        nb_current = r if i == q else 1000
        res = rechercheapi(nb_current, outformat, search, first=f, year=a)
        if res is None:
            continue

        mylistref, mylistauthors = parsejson(res)
        reference.extend(mylistref)
        authors.extend(mylistauthors)

        # Ajouter un délai entre les requêtes pour éviter l'erreur 429
        time.sleep(1)

    # Écriture des fichiers CSV dans le répertoire "results"
    if reference:
        with open(parsed_data_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, quoting=csv.QUOTE_ALL, delimiter=';')
            writer.writerows(reference)

    if authors:
        with open(authors_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, quoting=csv.QUOTE_ALL, delimiter=';')
            writer.writerows(authors)

    print(f"Fichiers pour l'année {a} créés avec succès.")
