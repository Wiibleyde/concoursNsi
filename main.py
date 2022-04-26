from flask import Flask, render_template, request, g
import sqlite3
import csv
import requests
import os
import pandas as pd
import openpyxl

app = Flask(__name__)

app.config["SECRET_KEY"] = "MotDePasse"

class File:
    def __init__(self, fileName):
        self.fileName = fileName
        if 'http' in fileName:
            self.download(fileName)
            if self.isCsv(): 
                self.fileName = f'files\\{self.getFileName()}.csv'
            elif self.isXlsx():
                self.fileName = f'files\\{self.getFileName()}.xlsx'
            else:
                print("This file is not a csv file")
                
    def isCsv(self):
        """check if a file is a csv file by reading its first line"""
        try:
            print(self.fileName)
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

    def download(self,url): 
        """download all file of lst"""     
        try:
            print(f'Downloading {url}')
            name = self.getFileName()
            r = requests.get(url, allow_redirects=True)
            open(f'temp\\{name}', 'wb').write(r.content)
            if isCsv(name):
                os.rename(f'temp\\{name}', f'files\\{name}.csv')
                print(f'{name} is csv saving it')
            else:
                os.remove(f'temp\\{name}')
                print(f'{name} is not csv or json deleting it')
        except requests.exceptions.MissingSchema:
            print(f'{url} is not a valid url')

        return f'files\\{self.getFileName()}.xlsx'

    def getFileName(self):
        if 'http' in self.fileName:
            return self.fileName.split('/')[-1].split('.')[0]
        else:
            return self.fileName.split('\\')[-1].split('.')[0]

    def fieldNames(self):
        """returns the field names of a csv or xlsx file"""
        if self.isCsv():
            with open(self.getfileName(), 'r') as f:
                reader = csv.reader(f, delimiter=';')
                firstLine=next(reader)
                cols=firstLine #[0].split(';')
                for compteur in range(len(cols)):
                    cols[compteur]="'"+cols[compteur].replace(' ','_')+"'"
                return cols               
        elif self.isXlsx():
            excel = openpyxl.load_workbook(self.getfileName())
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

    def getTitle(self,dbName):
        con = sqlite3.connect(dbName)
        cur = con.cursor()
        con.set_trace_callback(print)
        req="SELECT name FROM pragma_table_info('{}') ORDER BY cid".format(self.getFileName())
        lstTitle=cur.execute(req).fetchall()
        con.commit()
        return lstTitle

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

@app.route("/", methods=["GET", "POST"])
def Data_Analyser():
    return render_template("Data_Analyser.html")

@app.route("/Import_CSV", methods=["GET", "POST"])
def Import_CSV():
    return render_template("Import_CSV.html")

@app.route("/Selection", methods=["GET", "POST"])
def Selection():
    lien = request.form.get("link")
    Titles = fichier1.getTitle("files\\Database.db")
    return render_template("Selection.html", Titles = Titles)

@app.route("/Show_Graph", methods=["GET", "POST"])
def Show_Graph():
    Table = fichier1.getFileName()
    Name = request.form.get("tab")
    conn = sqlite3.connect("files\\Database.db", check_same_thread=False)
    cur = conn.cursor()
    query = "SELECT {} FROM '{}'".format(Name, Table)
    data = cur.execute(query).fetchall()
    print(data)
    cur.close()
    conn.commit()
    return render_template("Show_Graph.html", data=data)

if __name__ == "__main__":
    fichier1=File("https://www.observatoires-des-loyers.org/datagouv/2021/Base_OP_2021_Nationale.csv")
    lstFichier1=fichier1.copyToSQLite("files\\Database.db")
    machin = fichier1.getTitle("files\\Database.db")
    app.run()
