from database import *

if __name__ == '__main__':
    # Build a database table
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
    
    # Create an handler object and connect to db file.
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
    #dbh.end()