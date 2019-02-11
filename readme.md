# Pydatabase SQL
---------------------------------------
## Documentations
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
      * SCHED_MODIFY
      * SCHED_SEARCH
      
    * DataBaseTable Class
      * setTable(name,col,colist,primary=None)
      * setTableName(name)     
      * setDefaultName(name)
      * setColumns(col,colist,primary=None)
    * ( Examples ) 
```python
    dbt = DataBaseTable()
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
```
    * DataBaseTableHandler Class
      * begin(path=None)
      * end()
      * add(data_row)
      * delete(primary_unique_key)
      * pop()
      * get(primary_unique_key)
      * getByCol(primary_unique_key,column)
      * getByCond(SQL_condition_statement)
      * set(primary_unique_key,column,value)
      * setByCols(primary_unique_key,column_list,data_list)
      * group(SQL_condition_statement,group)
      * createView(view_name,str_column_list,SQL_condition_statement)
      * destroyView(view_name)
      * alterColumn(operation,new(old)_column,type)
      * cachedInit()
      * cachedClear()
      * cachedDelete(primary_unique_key,sync=True,sched=True)
      * cachedModify(modify_operation,primary_unique_key,column(list),value(list),sync=True,sched=True)
      * cachedSearch(search_operation,query_object,sched=True)
      * cachedPop(primary_unique_key,sched=True)
      * setCacheSize(hit=0)
      * cachedAlterColumnSync(operation,new(old)_column,type)
      * cachedAlterColumnOnly(operation,new(old)_column,type)
      * setCustomSched(bool)
```python
    dbh = DataBaseTableHandler(dbt)
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

    # Create View
    dbh.createView("Key_Desc_View","key, desc","value > 2")

    # Caching Test
    print("Cache Test")
    dbh.cachedInit()
    print(dbh.cachedSearch(DataBaseHandlerConst.QUERYBYID,"weight"))
    dbh.add(["IQ",7,"alter column test"])
    print(dbh.cachedSearch(DataBaseHandlerConst.QUERYBYID,"IQ"))

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