# Author : by Gibartes

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
    MODE_LRU        = 0
    MODE_OTHER      = 1
    MODE_TIMESTAMP  = "__timestamp__"
    SCHED_MODIFY    = 0
    SCHED_SEARCH    = 1
    DEFAULT_CONT    = 100

class DataBaseQuery:
    def __init__(self,dbname,primary):
        self.TBL     = dbname
        self.primary = primary
        self.conn    = 0
        self.cursor  = 0
    def __query(self,sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except:return None
    def __fetch(self,sql):
        try:
            self.cursor.execute(sql)
            for row in self.cursor:
                return row
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
    def insert(self,row):
        cols = ', '.join('"{}"'.format(col) for col in row.keys())
        vals = ', '.join(':{}'.format(col)  for col in row.keys())
        sql  = 'INSERT INTO "{0}" ({1}) VALUES ({2})'.format(self.TBL,cols,vals)
        self.cursor.execute(sql,row)
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

    # Modify Method Family
    def modify(self,ID,col,data):
        sql  = "UPDATE {0} SET {1}='{2}' WHERE {3}='{4}'".format(self.TBL,col,data,self.primary,ID)
        return self.__query(sql)
    def modifies(self,ID,col,data):
        var = list()
        for (i,j) in zip(col,data):var.append("{0} = '{1}'".format(i,j))
        var = ', '.join(var)
        sql  = "UPDATE {0} SET {1} WHERE {2}='{3}'".format(self.TBL,var,self.primary,ID)
        return self.__query(sql)

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
            return self.__fetch("SELECT {2}, MIN({0}) FROM {1}".format(col,self.TBL,self.primary))
        else:
            return self.__fetch("SELECT {3}, MIN({0}) FROM {1} WHERE {2}".format(col,self.TBL,cond,self.primary))

    def getMax(self,col,cond=""):
        if(cond==""):
            return self.__fetch("SELECT {2}, MAX({0}) FROM {1}".format(col,self.TBL,self.primary))
        else:
            return self.__fetch("SELECT {3}, MAX({0}) FROM {1} WHERE {2}".format(col,self.TBL,cond,self.primary))    

# This class is a parent class for the inheritance
class DataBaseHandler(metaclass=ABCMeta):
    def __init__(self,Table):
        self.db     = DataBaseQuery(Table.TBL_NAME,Table.PRIMARY_ORDER)
        self.sep    = os.sep
        self.table  = Table
        self.value  = list()
        self.cache  = None
        self.hit    = 0
        self.MaxHit = 100
        self.sched  = False # custom scheduling (default:disabled)
        self.onCreate()
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
        self.cachedClear()
        self.onDestory()

    # Add a row in the database.
    def add(self,value):
        if(type(value)!=list and len(value)!=self.table.LENGTH):
            return (False,0)
        try:
            self.db.insert(OrderedDict(zip(self.table.COLUMNSLIST,value)))
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

    # Modify the value in database by the specific column.
    def set(self,key,col,value):
        try:return (True,self.db.modify(key,col,value))
        except sqlite3.Error as e:return (None,e)
    def setByCols(self,key,col,data):
        if(len(col)!=len(data)):return (False,0)
        return (True,self.db.modifies(key,col,data))

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



    # Cached.
    def __cacheUpdate(self,value):
        if(type(value)!=list and len(value)!=self.table.LENGTH):
            return (False,0)
        try:
            self.cache.insert(OrderedDict(zip(self.table.COLUMNSLIST,value)))
            return (True,0)
        except sqlite3.Error as e:
            return (None,e)
    def __cachedSearch(self,opt,batch):
        ret = (False,False)
        try:
            if(opt==DataBaseHandlerConst.QUERYBYID):
                ret = self.cache.read(batch,self.table.PRIMARY_ORDER)
            elif(opt==DataBaseHandlerConst.QUERYBYCOND):
                ret = self.cache.readByCond(batch,self.table.PRIMARY_ORDER)
            return ret 
        except sqlite3.Error as e:return (None,e)
    def __cachedModify(self,opt,key,col,value):
        try:
            if(opt==DataBaseHandlerConst.MODIFYEACH):
                return (True,self.cache.modify(key,col,value))
            elif(opt==DataBaseHandlerConst.MODIFYCOLUMNS):
                return (True,self.cache.modifies(key,col,value))
        except sqlite3.Error as e:return (None,e)
    def cachedClear(self):
        if(type(self.cache)==DataBaseQuery):
            self.cache.build(self.table.COLUMNS)
            self.cache.close()
            self.hit = 0
    def cachedInit(self):
        path = ".{0}_cached_{1}".format(self.sep,self.table.DEFAULT_NAME)
        ret  = os.path.exists(path)
        self.cache = DataBaseQuery(self.table.TBL_NAME,self.table.PRIMARY_ORDER)
        self.cache.connect(path)
        if(ret==False):
            self.cache.build(self.table.COLUMNS)
            ret = self.cachedAlterColumnOnly(DataBaseHandlerConst.ADDCOLUMN,DataBaseHandlerConst.MODE_TIMESTAMP,"int")
            return (True,1)
        return (True,0)
    def cachedDelete(self,key,sync=True,sched=True):
        ret = self.cachedPop(key,sched)
        if(sync==True):
            return self.delete(key)
        return ret
    def cachedModify(self,opt,key,col,value,sync=True,sched=True):
        ret = self.__cachedModify(opt,key,col,value)
        if(ret[0]==True):
            if(sched==True and self.sched==False):
                self.cache.modify(ret[1][0],DataBaseHandlerConst.MODE_TIMESTAMP,time.time())
            elif(sched==True and self.sched==True):self.onSched(DataBaseHandlerConst.SCHED_MODIFY)
        if(sync==True and opt==DataBaseHandlerConst.MODIFYEACH):
            return self.set(key,col,value)
        elif(sync==True and opt==DataBaseHandlerConst.MODIFYCOLUMNS):
            return self.setByCols(key,col,value)
        return ret 
    def cachedSearch(self,opt,batch,sched=True):
        ret = self.__cachedSearch(opt,batch)
        if(ret!=None and ret[0]!=None):
            if(sched==True and self.sched==False):
                self.cache.modify(ret[0],DataBaseHandlerConst.MODE_TIMESTAMP,time.time())
                self.cachedLRUSched()
            elif(sched==True and self.sched==True):
                self.onSched(DataBaseHandlerConst.SCHED_SEARCH)
            return ret 	# short circuit
        if(opt==DataBaseHandlerConst.QUERYBYID):
            ret = self.get(batch)
        elif(opt==DataBaseHandlerConst.QUERYBYCOND):
            ret = self.getByCond(batch)
        else:return ret
        if(ret[0]==True):
            if(sched==True and self.sched==False):
                self.__cacheUpdate(ret[1])
                self.cache.modify(ret[1][0],DataBaseHandlerConst.MODE_TIMESTAMP,time.time())
                self.hit+=1
                self.cachedLRUSched()
            elif(sched==True and self.sched==True):
                self.onSched(DataBaseHandlerConst.SCHED_SEARCH)
                self.__cacheUpdate(ret[1])
        return ret
    def cachedPop(self,key,sched=True):
        try:
            ret = self.cache.delete(key)
            if(sched==True and ret!=None and self.sched==False):
                self.hit-=1
            elif(sched==True and ret!=None and self.sched==True):
                self.onSched()
            return (True,ret)
        except sqlite3.Error as e:return (None,e)
    def setCacheSize(self,hit=0):
        if(hit<1):self.MaxHit = DataBaseHandlerConst.DEFAULT_CONT
        else:self.MaxHit = int(hit)
        
    # LRU scheduling
    def __cachedLRUSched(self):
        try:
            ret = self.cache.getMin(DataBaseHandlerConst.MODE_TIMESTAMP)
            if(ret==None):return
            self.cache.delete(ret[0])
            self.hit-=1
            return ret[0]
        except:return
    def cachedLRUSched(self):
        if(self.hit==self.MaxHit):
            return self.__cachedLRUSched()
        return
    def cachedAlterColumnSync(self,cmd,add,type):
        try:return (self.db.alterColumn(cmd,add,type),self.cache.alterColumn(cmd,add,type))
        except:return (None,None)
    def cachedAlterColumnOnly(self,cmd,add,type):
        try:return (True,self.cache.alterColumn(cmd,add,type))
        except:return (None,None)
    
    
    
    # Interfaces.
    @abstractmethod
    def onCreate(self):
        pass
    @abstractmethod
    def onDestory(self):
        pass
    @abstractmethod
    def onSched(self,ptr):
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
    def onSched(self,ptr):
        # self.sched = True
        # if you want to use cache alogrithm like LRU and add LRU Algorithm
        pass


