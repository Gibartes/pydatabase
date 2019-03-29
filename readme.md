# Pydatabase SQL
---------------------------------------
## Documentations
* Install
  * pip install sqlHelper
* Class
  * DataBaseTable
    * Create a database table.
  * DataBaseTableHandler
    * A default handler class for table created from DataBaseTable class
    
* Class API
    * DataBaseHandlerConst
      * QUERYBYID
      * QUERYBYCOND
      * MODIFYEACH
      * MODIFYCOLOUMNS
      * ADDCOLUMN
      * DROPCOLUMN
      
    * DataBaseTable Class
      * setTable(name,col,colist,primary=None)
      * setTableName(name)     
      * setDefaultName(name)
      * setColumns(col,colist,primary=None)
      * showColumns()
      * showName()
          
          
    * DataBaseTableHandler Class
      * (bool,int)   begin(path=None)
      * void         end()
      * (bool,list)  add(data_row)
      * (bool,list)  delete(primary_unique_key)
      * (bool,list)  pop()
      * (bool,list)  get(primary_unique_key)
      * (bool,list)  getByCol(primary_unique_key,column)
      * (bool,list)  getByCond(SQL_condition_statement)
      * (bool,list)  getByColCond(column,SQL_condition_statement)
      * (bool,lists) getAll()
      * (bool,lists) filter(SQL_condition_statement)
      * (bool,lists) filterAll(SQL_condition_statement)
      * (bool,list)  set(primary_unique_key,column,value)
      * (bool,list)  setByCols(primary_unique_key,column_list,data_list)
      * (bool,bool)  group(SQL_condition_statement,group)
      * (bool,bool)  createView(view_name,str_column_list,SQL_condition_statement)
      * (bool,bool)  destroyView(view_name)
      * (bool,bool)  alterColumn(operation,new(old)_column,type)
      * (bool,lists) getMin(column,SQL_condition_statement)
      * (bool,lists) getMax(column,SQL_condition_statement)

      
    * ( Examples )
```python
    from database import *
    
    dbt = database.DataBaseTable()
    dbt.setTable(
                    name   = "CONFIG_TABLE",
                    col    = """
                            key    text primary key not NULL,
                            value  int,
                            desc   varchar[128]
                            """,
                    colist = ["key","value","desc"],
                )
    dbt.setDefaultName("_config.db")
    dbt.showColumns()
    
    dbh = database.DataBaseTableHandler(dbt)
    dbh.begin()
  
    # Data operation in the database
    dbh.add(["height",1,"description"])
    dbh.add(["weight",1,"description"])
    dbh.add(["age",9,"description"])
    print(dbh.get("height"))
    dbh.delete("height")
    print(dbh.get("height"))
    dbh.add(["height",1,"description"])
    dbh.set("height","value",3)
    print(dbh.get("height"))
    print(dbh.setByCols("height",["value","desc"],[6,"world"]))
    print(dbh.getByCol("height","value"))

    # filter data under certain condition
    print(dbh.filterAll("value < 3 AND key < 'w'"))

    # Create View
    dbh.createView("Key_Desc_View","key, desc","value > 2")

    # Clear database.
    dbh.end()
```

* Build a custom Database table handler
```python

class DataBaseTableHandler(DataBaseHandler):
    # The type must be DataBaseTable.
    # tableStruct = DataBaseTable()
    # ... setup TableStruct ...
    # handler = DataBaseTableHandler(talbeStruct)
    
    def __init__(self,DataBaseTableStruct):
        super().__init__(DataBaseTableStruct)
    def onCreate(self):     # when database is created
        pass
    def onDestory(self):    # when database is destroyed
        pass
    def onSched(self,ptr):  # cache scheduling callback
        pass
```
      
---------------------------------------