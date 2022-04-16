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

# def getFile(url):
#     """get all url which contain word download or datasets"""

def analyseCsv(csv_file):
    """analyse a csv file"""
    df = pandas.read_csv(csv_file)
    return df

# #On verra car on essaye de generer avec JavaScript
# def generateChart(csv_file):
#     """generate a chart from a csv file"""
#     df = pandas.read_csv(csv_file)
#     df.plot()
#     return df


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