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

from flask import Flask, render_template, request, g
import sqlite3
import csv
import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
import openpyxl



app = Flask(__name__)

app.config["SECRET_KEY"] = "MotDePasse"

# def getCsvFile(url):
#     """get all csv file of a html page"""
#     page = requests.get(url)
#     soup = BeautifulSoup(page.content, 'html.parser')
#     csv_links = []
#     for link in soup.find_all('a'):
#         if link.get('href').endswith('.csv'):
#             csv_links.append(link.get('href'))
#     return csv_links

# def analyseCsv(csv_file):
#     """analyse a csv file"""
#     df = pandas.read_csv(csv_file)
#     return df

# def getLink(url):
#     """get all csv file of a html page"""
#     page = requests.get(url)
#     soup = BeautifulSoup(page.text, 'html.parser')
#     dlLink = []
#     for link in soup.find_all('a'):
#         dlLink.append(link.get('href'))
#     return dlLink

# def sortList(lst):
#     newLst = []
#     for compteur in lst:
#         if compteur == None:
#             pass
#         else:
#             urlStr=[]
#             urlStr=compteur.split('/')
#             for word in urlStr:
#                 if 'https://www.data.gouv.fr/fr/datasets/' in word or 'download' in word or 'dataset' in word:
#                     newLst.append(compteur)
    # return newLst


class File:
    def __init__(self, fileName):
        self.fileName = fileName

    def isCsv(self):
        """check if a file is a csv file by reading its first line"""
        try:
            with open(self.fileName, 'r') as f:
                first_line = f.readline()
                if ',' in first_line or ';' in first_line:
                    return True
                else:
                    return False
        except UnicodeDecodeError:
            return False

    def isXlsx(self):
        try:
            excel=openpyxl.load_workbook(self.fileName)
            return True
        except openpyxl.utils.exceptions.InvalidFileException:
            return False


    def getFileName(self):
        return self.fileName.split('\\')[-1].split('.')[0]

    def fieldNames(self):
        """returns the field names of a csv or xlsx file"""
        if self.isCsv():
            with open(self.fileName, 'r') as f:
                reader = csv.reader(f, delimiter=';')
                firstLine=next(reader)
                cols=firstLine #[0].split(';')
                for compteur in range(len(cols)):
                    cols[compteur]="'"+cols[compteur].replace(' ','_')+"'"
                return cols               
        elif self.isXlsx():
            excel = openpyxl.load_workbook(self.fileName)
            sheet = excel.active
            cols=[]
            firstRow=next(sheet.rows)
            for c in firstRow:
                cols.append(c.value)
            print(cols)
            for compteur in range(len(cols)):
                if cols[compteur] is not None:
                    cols[compteur]="'"+cols[compteur].replace(' ','_')+"'"
                else:
                    cols[compteur]="'"+str(compteur)+"'"
            return cols   
        else:
            print("This file is not a csv file")

    def copyToSQLite(self,dbName):
        """read a csv file and write it to a sqlite database"""
        if self.isCsv():
            with open(self.fileName, 'r') as f:
                reader = csv.reader(f, delimiter=';')
                con = sqlite3.connect(dbName)
                cur = con.cursor()
                con.set_trace_callback(print)
                cur.execute("DROP TABLE IF EXISTS '{}'".format(self.getFileName()))
                cur.execute("CREATE TABLE '{}' ({})".format(self.getFileName(),','.join(self.fieldNames())))
                next(reader)
                for row in reader:
                    sql="INSERT INTO '{}' VALUES (?{})".format(self.getFileName(),(len(self.fieldNames())-1)*",?")
                    cur.execute(sql,row)
                con.commit()
        elif self.isXlsx():
            excel = openpyxl.load_workbook(self.fileName)
            sheet = excel.active
            con = sqlite3.connect(dbName)
            cur = con.cursor()
            con.set_trace_callback(print)
            cur.execute("DROP TABLE IF EXISTS '{}'".format(self.getFileName()))
            cur.execute("CREATE TABLE '{}' ({})".format(self.getFileName(),','.join(self.fieldNames())))
            for r in sheet.rows:
                sql="INSERT INTO '{}' VALUES (?{})".format(self.getFileName(),(len(self.fieldNames())-1)*",?")
                cur.execute(sql,[cell.value for cell in r])
            con.commit()
        else:
            print("This file is not a csv file")

    def convertToCSV(self):
        excel = openpyxl.load_workbook(self.fileName)
        sheet = excel.active
        name=self.getFileName()
        col = csv.writer(open(f'files\\{name}.csv','w',newline="",encoding="utf-8"))
        for r in sheet.rows:
            col.writerow([cell.value for cell in r])
        df = pd.DataFrame(pd.read_csv(f'files\\{name}.csv'))
        return df


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
            if isCsv(name):
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

# def isJson(file):
#     """check if a file is a json file by reading its first line"""
#     try:
#         with open(f'temp\\{file}', 'r') as f:
#             first_line = f.readline()
#             if '{' in first_line:
#                 return True
#             else:
#                 return False
#     except UnicodeDecodeError:
#         return False
          
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("Database.db")
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

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
        download(lien)
    return render_template("Show_Graph.html")


if __name__ == "__main__":
    fichier1=File("files\\file0.csv")
    lstFichier1=fichier1.copyToSQLite("files\\Database.db")
    app.run()


