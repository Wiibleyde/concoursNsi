""" TODO

(- Ajout des donnees dans base de donnees)

Nathan :
- Recuperer donnees (web parsing) et les mettre dans une base de donnees
- Analyser pour proposer des graphiques 


Victor :
- Creer les graphiques (en js ou images mais pas ouf(et ça c'est pas cool ;-;)) 
- Interface utilisateur (flask)
    - Possibilité de rentrer un csv à la main ou de récup csv d'une page

Plan Flask :
- Creer une page d'accueil
- Creer un page pour rentrer des fichier csv à partir d'une page web ou d'un fichier mis à la main
- Creer une page qui propose les graphiques à partir du fichier csv
- Creer une page de visualisation avec un bouton pour revenir à la page d'accueil


"""

import flask
import random
import sqlite3
import csv
import pandas
import requests
from bs4 import BeautifulSoup


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



def createIndexPage():
    """create the main page"""
    return flask.render_template('index.html')
