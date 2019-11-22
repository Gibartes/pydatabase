#!/usr/bin/python

# MIT License
# Author : Kwon Hong Kyun

"""
MIT License

    Copyright (c) 2018 

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

import time
import sqlite3,os
from collections import OrderedDict
from abc import *

# Create only one instance for a (handler) class
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# You don't have to directly call this class instance on the outside.
# I'd recommend that create a handler class for the database query.
# SELECT column-list FROM table_name WHERE [conditions] GROUP BY column1, column2 .... columnN ORDER BY column1, column2 .... columnN

class DataBaseHandlerConst(object):
    QUERYBYID       = 1
    QUERYBYCOND     = 2
    MODIFYEACH      = 1
    MODIFYCOLUMNS   = 2
    ADDCOLUMN       = 1
    DROPCOLUMN      = 2

class DataBaseQuery:
    def __init__(self,dbname,primary):
        self.TBL     = dbname
        self.primary = primary
        self.conn    = 0
        self.cursor  = 0
    def __del__(self):
        return self.close()
    def __query(self,sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except:return None
    def __query_lazy(self,sql):
        try:
            self.cursor.execute(sql)
            return True
        except:return None
    def __fetch(self,sql):
        try:
            self.cursor.execute(sql)
            for row in self.cursor:
                return row
        except:return None
    def __fetchAll(self,sql):
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except:return None
    # Database Initialization Method Family
    def connect(self,path):
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
    def close(self):
        self.conn.close()
    def build(self,tables):
        self.conn.execute("""DROP TABLE IF EXISTS {0}""".format(self.TBL))
        self.conn.execute("""CREATE TABLE {0} ( {1} )""".format(self.TBL,tables))
        self.conn.commit()

    # Data Operation Method Family
    def drop(self):
        self.conn.execute("""DROP TABLE IF EXISTS {0}""".format(self.TBL))
        self.conn.commit()
    def delete(self,ID):
        sql = "DELETE FROM {0} WHERE {1}='{2}'".format(self.TBL,self.primary,ID)
        return self.__query(sql)
    def insert(self,row,lazy=False):
        cols = ', '.join('"{}"'.format(col) for col in row.keys())
        vals = ', '.join(':{}'.format(col)  for col in row.keys())
        sql  = 'INSERT INTO "{0}" ({1}) VALUES ({2})'.format(self.TBL,cols,vals)
        self.cursor.execute(sql,row)
        if(lazy==False):self.conn.commit()
    def commit(self):
        self.conn.commit()

    # Read Method Family
    # get a row with primary id in the database
    def read(self,ID,PRIMARY_ORDER=""):
        sql  = "SELECT * FROM {0} WHERE {1}='{2}' ORDER BY {3} DESC".format(self.TBL,self.primary,ID,PRIMARY_ORDER)
        return self.__fetch(sql)
    # get a row matched primary id with the specific column in the database
    def readByCol(self,ID,col,PRIMARY_ORDER=""):
        sql  = "SELECT {0} FROM {1} WHERE {2}='{3}' ORDER BY {4} DESC".format(col,self.TBL,self.primary,ID,PRIMARY_ORDER)
        return self.__fetch(sql)
    # get a row with the given condition statement in the database
    def readByCond(self,cond,PRIMARY_ORDER=""):
        sql  = "SELECT * FROM {0} WHERE {1} ORDER BY {2} DESC".format(self.TBL,cond,PRIMARY_ORDER)
        return self.__fetch(sql)
    # get a row with the given condition statement and specific column in the database
    def readByColCond(self,col,cond,PRIMARY_ORDER=""):
        sql  = "SELECT {0} FROM {1} WHERE {2} ORDER BY {3} DESC".format(col,self.TBL,cond,PRIMARY_ORDER)
        return self.__fetch(sql)
    def readAll(self,PRIMARY_ORDER=""):
        sql  = "SELECT * FROM {0} ORDER BY {1} DESC".format(self.TBL,PRIMARY_ORDER)
        return self.__fetchAll(sql)
    # get rows with the given condition statement in the database
    def filter(self,cond,PRIMARY_ORDER=""):
        sql  = "SELECT * FROM {0} WHERE {1} ORDER BY {2} DESC".format(self.TBL,cond,PRIMARY_ORDER)
        return self.__fetchAll(sql)
    # Modify Method Family
    def modify(self,ID,col,data,lazy=False):
        sql  = "UPDATE {0} SET {1}='{2}' WHERE {3}='{4}'".format(self.TBL,col,data,self.primary,ID)
        if(lazy==False):
            return self.__query(sql)
        return self.__query_lazy(sql)
    def modifies(self,ID,col,data,lazy=False):
        var = list()
        for (i,j) in zip(col,data):var.append("{0} = '{1}'".format(i,j))
        var = ', '.join(var)
        sql  = "UPDATE {0} SET {1} WHERE {2}='{3}'".format(self.TBL,var,self.primary,ID)
        if(lazy==False):
            return self.__query(sql)
        return self.__query_lazy(sql)

    # Adds on
    def getTop(self):
        sql  = "SELECT * FROM {0} LIMIT 1".format(self.TBL)
        return self.__fetch(sql)

    def group(self,cond,groups,PRIMARY_ORDER=""):
        sql  = "SELECT * FROM {0} WHERE {1} GROUP BY {2} ORDER BY {3} DESC".format(self.TBL,cond,groups,PRIMARY_ORDER)
        return self.__fetch(sql)

    def createView(self,view,col,cond=""):
        if(cond==""):return self.__query("CREATE VIEW {0} AS SELECT {1} FROM {2}".format(view,col,self.TBL))
        else:return self.__query("CREATE VIEW {0} AS SELECT {1} FROM {2} WHERE {3}".format(view,col,self.TBL,cond))
    def destroyView(self,view):
        return self.__query("DROP VIEW {0}".format(view))
    def alterColumn(self,cmd,add,type):
        if(cmd==DataBaseHandlerConst.ADDCOLUMN):
            return self.__query("ALTER TABLE {0} ADD {1} {2}".format(self.TBL,add,type))
        elif(cmd==DataBaseHandlerConst.DROPCOLUMN):
            return self.__query("ALTER TABLE {0} DROP {1} {2}".format(self.TBL,add))
        else:return None
        
    def getMin(self,col,cond=""):
        if(cond==""):
            return self.__fetchAll("SELECT {2}, MIN({0}) FROM {1}".format(col,self.TBL,self.primary))
        else:
            return self.__fetchAll("SELECT {3}, MIN({0}) FROM {1} WHERE {2}".format(col,self.TBL,cond,self.primary))
    def getMax(self,col,cond=""):
        if(cond==""):
            return self.__fetchAll("SELECT {2}, MAX({0}) FROM {1}".format(col,self.TBL,self.primary))
        else:
            return self.__fetchAll("SELECT {3}, MAX({0}) FROM {1} WHERE {2}".format(col,self.TBL,cond,self.primary))    

# This class is a parent class for the inheritance
class DataBaseHandler(metaclass=ABCMeta):
    def __init__(self,Table):
        self.db      = DataBaseQuery(Table.TBL_NAME,Table.PRIMARY_ORDER)
        self.sep     = os.sep
        self.table   = Table
        self.__count = 0
        self.page    = 0
        self.onCreate()
    def __del__(self):
        return self.end()
    # Create a database according to defined table class.
    def create(self):
        self.db.build(self.table.COLUMNS)
    # Connect to the database
    def begin(self,path=None):
        if(path==None):
            path = "{0}{1}{2}".format(self.table.PATH,self.sep,self.table.DEFAULT_NAME)
        ret = os.path.exists(path)
        self.db.connect(path)
        if(ret==False):
            self.create()
            return (True,1)
        return (True,0)
    # Close the current connection.
    def end(self):
        self.db.close()
        self.onDestory()
    # Commit to the database.
    def commit(self):
        try:
            self.db.commit()
            self.__count=0
            return (True,0)
        except sqlite3.Error as e:
            return (None,e)
    # Add a row in the database.
    def add(self,value,lazy=False):
        if(type(value)!=list and len(value)!=self.table.LENGTH):
            return (False,0)
        try:
            self.db.insert(OrderedDict(zip(self.table.COLUMNSLIST,value)),lazy)
            return (True,0)
        except sqlite3.Error as e:
            return (None,e)
    # Add records in the database (Lazy)
    def addCount(self,value):
        if(type(value)!=list and len(value)!=self.table.LENGTH):
            return (False,0)
        try:
            self.db.insert(OrderedDict(zip(self.table.COLUMNSLIST,value)),True)
            self.__count+=1
            if(self.__count>=self.page):
                self.commit()
                self.__count=0
            return (True,0)
        except sqlite3.Error as e:
            return (None,e)
    # Remove a row from the database.
    def delete(self,key):
        try:return (True,self.db.delete(key))
        except sqlite3.Error as e:return (None,e)
    # Pop a row in the database.
    def pop(self):
        ret = self.db.getTop()
        if(ret==None or ret==False):
            return (None,0)
        try:
            self.db.delete(ret[0])
            return (True,ret)
        except sqlite3.Error as e:
            return (None,e)
        return (None,0)

    # Get a row from the database.
    def get(self,key):
        try:return (True,self.db.read(key,self.table.PRIMARY_ORDER))
        except sqlite3.Error as e:return (None,e)
    def getByCol(self,key,col):
        try:return (True,self.db.readByCol(key,col,self.table.PRIMARY_ORDER))
        except sqlite3.Error as e:return (None,e)
    def getByCond(self,cond):
        try:return (True,self.db.readByCond(cond,self.table.PRIMARY_ORDER))
        except sqlite3.Error as e:return (None,e)
    def getByColCond(self,col,cond):
        try:return (True,self.db.readByColCond(col,cond,self.table.PRIMARY_ORDER))
        except sqlite3.Error as e:return (None,e)
    def getAll(self):
        try:return (True,self.db.readAll(self.table.PRIMARY_ORDER))
        except sqlite3.Error as e:return (None,e)
    def filter(self,cond):
        try:return (True,self.db.readByCond(cond,self.table.PRIMARY_ORDER))
        except sqlite3.Error as e:return (None,e)
    def filterAll(self,cond):
        try:return (True,self.db.filter(cond,self.table.PRIMARY_ORDER))
        except sqlite3.Error as e:return (None,e)
    # Modify the value in database by the specific column.
    def set(self,key,col,value,lazy=False):
        try:return (True,self.db.modify(key,col,value,lazy))
        except sqlite3.Error as e:return (None,e)
    def setByCols(self,key,col,data,lazy=False):
        if(len(col)!=len(data)):return (False,0)
        try:return (True,self.db.modifies(key,col,data,lazy))
        except sqlite3.Error as e:return (None,e)
        
    def group(self,cond,grp):
        if(len(grp)>len(cond)):return (False,0)
        try:return (True,self.db.group(col,cond))
        except sqlite3.Error as e:return (None,e)
    def createView(self,view,col,cond=""):
        try:return (True,self.db.createView(view,col,cond))
        except sqlite3.Error as e:return (None,e)
    def destroyView(self,view):
        try:return (True,self.db.destroyView(view))
        except sqlite3.Error as e:return (None,e)
    def alterColumn(self,cmd,add,type):
        return self.db.alterColumn(cmd,add,type)
    def getMin(self,col,cond=""):
        try:return (True,self.db.getMin(col,cond))
        except sqlite3.Error as e:return (None,e)
    def getMin(self,col,cond=""):
        try:return (True,self.db.getMax(col,cond))
        except sqlite3.Error as e:return (None,e)
        
    # Interfaces.
    @abstractmethod
    def onCreate(self):
        pass
    @abstractmethod
    def onDestory(self):
        pass

class __DataBaseTableStruct(object):
    TBL_NAME      = "Configuration_Table"
    DEFAULT_NAME  = "conf.db"
    COLUMNS       = """
                    key    text primary key not NULL,
                    value  int,
                    desc   varchar[128]
                    """
    COLUMNSLIST   = ["key","value","desc"]
    PRIMARY_ORDER = "key"
    LENGTH        = len(COLUMNSLIST)
    PATH          = "."

class DataBaseTable(__DataBaseTableStruct):
    def __init__(self):
        super().__init__()
    def setTableName(self,name):
        self.TBL_NAME = name
    def setDefaultName(self,name):
        self.DEFAULT_NAME = name
    def setColumns(self,col,colist,primary=None):
        self.COLUMNS     = col
        self.COLUMNSLIST = colist
        self.LENGTH      = len(self.COLUMNSLIST)
        if(primary==None):
            self.PRIMARY_ORDER = colist[0]
        else:self.PRIMARY_ORDER = primary
    def setPath(self,path):
        self.PATH   = path
    def setTable(self,name,col,colist,primary=None):
        self.setTableName(name)
        self.setColumns(col,colist,primary)
    def showColumns(self):
        print(self.COLUMNSLIST)
    def showName(self):
        print(self.TBL_NAME)
    @staticmethod
    def createTableTextFormPair(column):
        __str = ""
        for i in column:
            if(len(i)!=2):return ""
            __str += "{0} {1}, ".format(i[0],i[1])
        return __str[:-2]
    @staticmethod
    def createColumnListFromPair(column):
        __str = list()
        for i in column:
            __str.append(i[0])
        return __str

class DataBaseTableHandler(DataBaseHandler):
    # The type must be DataBaseTable.
    # tableStruct = DataBaseTable()
    # ... setup TableStruct ...
    # handler = DataBaseTableHandler(talbeStruct)
    def __init__(self,DataBaseTableStruct):
        super().__init__(DataBaseTableStruct)
    def onCreate(self):
        pass
    def onDestory(self):
        pass
