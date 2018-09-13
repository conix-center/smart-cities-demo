#!/usr/bin/python3

import psycopg2

class TimescalePoster:

    def __init__(self, host, port, database, username, password):
        self.connection = psycopg2.connect(dbname=database, host=host, port=port, user=username, password=password)
    
    """
    Inserts data into an existing table. On failure due to not enough columns
    will automatically add columns to the table as necessary.
    Takes:
    tableName - string of the table being inserted into
    timeStamp - the timeStamp of the insertion
    tableObj - a dict of key/value pairs to insert
    """
    def insertData(self, tableName, timeStamp, tableObj):
        cursor = connection.cursor()

        try:
            cursor.execute("INSERT INTO %s (TIMESTAMP" + cols + ") VALUES (%s", nameList)
        except psycopg2.Error as e:
            print("CREATE TABLE Error: %s".format(e))

        self.connection.commit()


    """
    Add a column to a table
    Takes:
    tableName - string of the table being inserted into
    tableObj - a dict of key/value pairs to add
    """
    def addColumn(self, tableName, tableObj):
        pass

    def __getType(self, value):
        t = type(value)
        if(t is str):
            return 'TEXT'
        elif(t is bool):
            return 'BOOLEAN'
        elif(t is int):
            return 'DOUBLE PRECISION'
        elif(t is float):
            return 'DOUBLE PRECISION'
        else(t is list):
            t2 = type(value[0])
            if(t2 is str):
                return 'TEXT[]'
            elif(t2 is bool):
                return 'BOOLEAN[]'
            elif(t2 is int):
                return 'DOUBLE PRECISION[]'
            elif(t2 is float):
                return 'DOUBLE PRECISION[]'
            else:
                return 'err'
        else:
            return 'err'

    """
    Creates a timescaledb table with at least a timestamp field. Partitions table
    by time.
    Takes:
    tableName - string of the table being inserted into
    tableObj - a dict of key/value pairs to start the table with
    """
    def createTable(self, tableName, tableObj):
        #find the number of columns in the in the tableobj and create
        #placeholders
        cols = ""
        for key in tableObj:
            cols = cols + ", %s %s"

        #map the type of those objects to the correct postgres type
        nameList = []
        nameList.append(tableName)
        for key in tableObj:
            t = self.__getType(tableObj[key])
            if(t is not 'err'):
                nameList.append(key)
                nameList.append(t)
            else:
                print('Error with object %s at key %s with value %s'.format(tableObj, key, tableObj[key]))

        cursor = connection.cursor()

        try:
            cursor.execute("CREATE TABLE %s (TIMESTAMP TIMESTAMPTZ NOT NULL" + cols + ")", nameList)
        except psycopg2.Error as e:
            print("CREATE TABLE Error: %s".format(e))

        self.connection.commit()

    """
    Checks if a table exists
    takes:
    tableName - name of the table
    """
    def tableExists(self, tableName):
        pass

