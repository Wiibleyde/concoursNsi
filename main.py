""" TODO
(- Ajout des donnees dans base de donnees)
Nathan :
- Recuperer donnees (web parsing)
- Analyser pour proposer des graphiques
Victor :
- Creer les graphiques (en js ou images mais pas ouf(et ça c'est pas cool ;-;))
- Interface utilisateur (flask)
    - Possibilité de rentrer un csv à la main ou de récup csv d'une page
"""

from flask import Flask, render_template
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

# #On verra car on essaye de generer avec JavaScript
# def generateChart(csv_file):
#     """generate a chart from a csv file"""
#     df = pandas.read_csv(csv_file)
#     df.plot()
#     return df


@app.route("/", methods=["GET", "POST"])
def Acceuil():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()