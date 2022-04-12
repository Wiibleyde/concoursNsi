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

import flask
import random
import sqlite3
import csv

def getCsvFile(url):
    """get all csv file of a html page"""
    import requests
    from bs4 import BeautifulSoup
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    csv_links = []
    for link in soup.find_all('a'):
        if link.get('href').endswith('.csv'):
            csv_links.append(link.get('href'))
    return csv_links

def generateChart(csv_file):
    """generate a chart from a csv file"""
    import pandas as pd
    df = pd.read_csv(csv_file)
    df.plot()
    return df