from flask import Flask, render_template, request, g, redirect
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
        """Init of File class

        Args:
            fileName (str): Name of the file
        """
        self.fileName = fileName
        if 'http' in fileName:
            self.fileName=self.download(fileName)
            if not self.fileName:
                print("This file is not a csv file")

    def isCsv(self,fileName=None):
        """Test if a file is a csv file

        Args:
            fileName (str, optional): name of the file. Defaults to None.

        Returns:
            bool: true if the file is a csv
        """
        if fileName is None:
            fileName=self.fileName
        try:
            print(fileName)
            with open(fileName, 'r') as f:
                first_line = f.readline()
                if ',' in first_line or ';' in first_line:
                    return True
                else:
                    return False
        except UnicodeDecodeError or FileNotFoundError:
            return False

    def isXlsx(self, fileName=None):
        """Test if a file is a xlsx file

        Args:
            fileName (str, optional): name of the file. Defaults to None.

        Returns:
            bool: true if the file is a xlsx
        """
        if fileName is None:
            fileName=self.fileName
        try:
            excel=openpyxl.load_workbook(fileName)
            return True
        except openpyxl.utils.exceptions.InvalidFileException or FileNotFoundError:
            return False

    def download(self,url): 
        """Download file
        
        Args:
            url (str): url of a file
        """  
        try:
            print(f'Downloading {url}')
            name = self.getFileName()
            r = requests.get(url, allow_redirects=True)
            try:
                open(f'filesTemp\\{name}', 'wb').write(r.content)
                if self.isCsv(f'filesTemp\\{name}'):
                    newName=f'files\\{name}.csv'
                    os.rename(f'filesTemp\\{name}', newName)
                    print(f'{newName} is csv saving it')
                    return newName
                elif self.isXlsx(f'filesTemp\\{name}'):
                    newName=f'files\\{name}.xlsx'
                    os.rename(f'filesTemp\\{name}', newName)
                    print(f'{newName} is xlsx saving it')
                    return newName
                else:
                    os.remove(f'filesTemp\\{name}')
                    print(f'{name} is not csv or xlsx deleting it')
                return False
            except FileNotFoundError:
                return Error_Page("File not found")
        except requests.exceptions.MissingSchema:
            print(f'{url} is not a valid url')

        return f'files\\{self.getFileName()}.xlsx'

    def getFileName(self):
        """get the name of a file

        Returns:
            str: name of the file
        """
        if 'http' in self.fileName:
            print('http found')
            return self.fileName.split('/')[-1].split('.')[0]
        else:
            return self.fileName.split('\\')[-1].split('.')[0]

    def fieldNames(self):
        """name of field in csv file

        Returns:
            lst: list of fields of the csv file
        """
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
        """copying the content of csv file in a sqlite database

        Args:
            dbName (str): name of database (default name: Database.db)
        """
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
        self.deleteFile()

    def deleteFile(self):
        """deleting specific file
        """
        os.remove(self.fileName)
        print(f'{self.fileName} deleted')

    def getTitle(self,dbName):
        """get the title of the sqlite db

        Args:
            dbName (str): name of database

        Returns:
            lst: list of titles of sqlite database
        """
        con = sqlite3.connect(dbName)
        cur = con.cursor()
        # con.set_trace_callback(print)
        req="SELECT name FROM pragma_table_info('{}') ORDER BY cid".format(self.getFileName())
        lstTitle=cur.execute(req).fetchall()
        con.commit()
        titles=[]
        for ele in lstTitle:
            titles.append(ele[0])
        return titles
    
def deleteDatabase():
    """delete the database named 'Database.db'
    """
    os.remove('files\\Database.db')
    print('Database deleted')

@app.route("/", methods=["GET", "POST"])
def Data_Analyser():
    """main page"""
    return render_template("Data_Analyser.html")

@app.route("/Import_CSV", methods=["GET", "POST"])
def Import_CSV():
    """import a csv file"""
    return render_template("Import_CSV.html")

@app.route("/Selection", methods=["GET", "POST"])
def Selection():
    """select a title of csv file"""
    global fichier1

    if len(request.form)==0:
        if fichier1 is None:
            print('redirect')
            return redirect('/Import_CSV')
        else:
            Titles = fichier1.getTitle("files\\Database.db")
    else:
        if request.form.get("link") != '':
            lien = request.form.get("link")
            try:
                fichier1=File(lien)
            except FileNotFoundError:
                return Error_Page("File not found")
            fichier1.copyToSQLite("files\\Database.db")
            Titles = fichier1.getTitle("files\\Database.db")
        elif len(request.files)!=0:
            f = request.files['select-file']
            f.save(f'files\\{f.filename}')
            fichier1=File(f'files\\{f.filename}')
            fichier1.copyToSQLite(f'files\\Database.db')
            Titles = fichier1.getTitle("files\\Database.db")
        else:
            try:
                Titles = fichier1.getTitle("files\\Database.db")
            except NameError:
                print('redirect')
                return redirect('/Import_CSV')

    return render_template("Selection.html", Titles = Titles)

@app.route("/Show_Graph", methods=["GET", "POST"])
def Show_Graph():
    """show a graph"""
    Table = fichier1.getFileName()
    Name = request.form.get("tab")
    conn = sqlite3.connect("files\\Database.db", check_same_thread=False)
    cur = conn.cursor()
    query = "SELECT {} FROM '{}'".format(Name, Table)
    data = cur.execute(query).fetchone()
    print(data)
    cur.close()
    conn.commit()
    return render_template("Show_Graph.html", data=data)

@app.route("/Error_Page", methods=["GET", "POST"])
def Error_Page(error):
    """error page"""
    return render_template("Error_Page.html", error=error)

if __name__ == "__main__":
    app.run()
    try:
        deleteDatabase()
    except FileNotFoundError:
        print("Database not found")