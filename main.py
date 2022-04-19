""" TODO
(- Ajout des donnees dans base de donnees)
Nathan :
- Recuperer donnees (web parsing) (et les mettre dans une base de donnees)
- Analyser pour proposer des graphiques 


Victor :
(En cours) - Afficher des graph (en js ou images mais pas ouf(et ça c'est pas cool ;-;)) 
(Terminé) - Interface utilisateur (flask) 
    (Terminé) - Possibilité de rentrer un csv à la main ou de récup csv d'une page

Plan Flaskb (Victor) :
(Terminé) - Creer une page d'accueil 
(Terminé) - Creer un page pour rentrer des fichier csv à partir d'une page web ou d'un fichier mis à la main 
(Terminé) - Creer une page qui propose les graphiques à partir du fichier csv avec un bouton pour revenir a l'acceuil 


"""

from cgitb import text
from flask import Flask, render_template, request
import random
import sqlite3
import csv
import pandas
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

app.config["SECRET_KEY"] = "MotDePasse"

def getCsvFile(url):
    """get all csv file of a html page"""
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    csv_links = []
    for link in soup.find_all('a'):
        if link.get('href').endswith('.csv'):
            csv_links.append(link.get('href'))
    return csv_links

def analyseCsv(csv_file):
    """analyse a csv file"""
    df = pandas.read_csv(csv_file)
    return df

def getLink(url):
    """get all csv file of a html page"""
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    dlLink = []
    for link in soup.find_all('a'):
        dlLink.append(link.get('href'))
    return dlLink

def sortList(lst):
    newLst = []
    for compteur in lst:
        if compteur == None:
            pass
        else:
            urlStr=[]
            print(compteur)
            urlStr=compteur.split('/')
            for word in urlStr:
                if 'https://www.data.gouv.fr/fr/datasets/' in word or 'download' in word or 'dataset' in word:
                    newLst.append(compteur)
    return newLst

def download(lst): 
    """download all file of lst"""     
    num=0
    name=f'file{num}'
    for url in lst:
        try:
            print(f'Downloading {url}')
            name = f'file{num}'
            r = requests.get(url, allow_redirects=True)
            open(f'temp\\{name}', 'wb').write(r.content)
            if isJson(name):
                os.rename(f'temp\\{name}', f'files\\{name}.json')
                print(f'{name} is json saving it')
                num=num+1
            elif isCsv(name):
                os.rename(f'temp\\{name}', f'files\\{name}.csv')
                print(f'{name} is csv saving it')
                num=num+1
            else:
                os.remove(f'temp\\{name}')
                print(f'{name} is not csv or json deleting it')
        except requests.exceptions.MissingSchema:
            print(f'{url} is not a valid url')

def isCsv(file):
    """check if a file is a csv file by reading its first line"""
    try:
        with open(f'temp\\{file}', 'r') as f:
            first_line = f.readline()
            if ',' in first_line or ';' in first_line:
                return True
            else:
                return False
    except UnicodeDecodeError:
        return False

def isJson(file):
    """check if a file is a json file by reading its first line"""
    try:
        with open(f'temp\\{file}', 'r') as f:
            first_line = f.readline()
            if '{' in first_line:
                return True
            else:
                return False
    except UnicodeDecodeError:
        return False
          

@app.route("/", methods=["GET", "POST"])
def Data_Analyser():
    return render_template("Data_Analyser.html")

@app.route("/Import_CSV", methods=["GET", "POST"])
def Import_CSV():
    return render_template("Import_CSV.html")

@app.route("/Show_Graph", methods=["GET", "POST"])
def Show_Graph():
    lien = request.form.get("link")
    if lien == "":
        print('empty')
    else:
        print(lien)
    return render_template("Show_Graph.html")

if __name__ == "__main__":
    app.run()
    