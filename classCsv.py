import csv

class csv:
    """class to analyse csv"""
    def __init__(self, file):
        self.file = file
        self.data = []
        self.read()

    def getRow(self, row):
        """returns a list of the values in the row"""
        return self.data[row]
    
    def getRowColumn(self, row, column):
        """returns the value in the row and column"""
        return self.data[row][column]
    
    def getRowColumns(self, row, columns):
        """returns a list of the values in the row and columns"""
        return [self.data[row][column] for column in columns]

    def getColumns(self, columns):
        """returns a list of the values in the columns"""
        return [row[column] for row in self.data for column in columns]
