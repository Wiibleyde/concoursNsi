import csv
import requests
from bs4 import BeautifulSoup
import os

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
                if 'datasets' in word or 'download' in word or 'dataset' in word:
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


            

lstUrl=getLink('https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/')
print(lstUrl)
newLst=sortList(lstUrl)
print(newLst)
download(newLst)
