"""
This module contains action definitions for database systems.
"""

global sr

import traceback
import inspect
import sys

from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as sr,
)
from Framework.Utilities.CommonUtil import (
    passed_tag_list,
    failed_tag_list,
    skipped_tag_list,
)  # Allowed return strings, used to normalize pass/fail
from Framework.Utilities.decorators import logger, deprecated

MODULE_NAME = inspect.getmodulename(__file__)

#################### Database Actions ####################
# Constant names for database related activities
DB_TYPE = "db_type"
DB_NAME = "db_name"
DB_USER_ID = "db_user_id"
DB_PASSWORD = "db_password"
DB_HOST = "db_host"
DB_PORT = "db_port"
DB_ODBC_DRIVER = "odbc_driver"


# [NON ACTION]
@logger
def find_odbc_driver(db_type="postgresql"):
    """
    Finds the ODBC driver to work with based on the given database type
    :param db_type: type of database (e.g postgres, mysql, etc.)
    :return: name of the driver (string)
    """

    import pyodbc

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    db_type = db_type.lower()

    # Check to see if any ODBC driver is specified
    selected_driver = sr.Get_Shared_Variables(DB_ODBC_DRIVER, log=False)

    # If no ODBC driver is specified
    if selected_driver == "failed":
        # Driver list for pyodbc to connect through the ODBC standard
        pyodbc_drivers = pyodbc.drivers()

        # Sort to get unicode items first
        pyodbc_drivers.sort(reverse=True, key=lambda x: "unicode" in x.lower())

        for odbc_driver in pyodbc_drivers:
            odbc_driver_lowercase = odbc_driver.lower()

            if db_type == "postgresql":
                if (
                    "postgre" in odbc_driver_lowercase
                    and "unicode" in odbc_driver_lowercase
                ):
                    selected_driver = odbc_driver
                    # We usually want the unicode drivers, so break once we've found it
                    break
                elif (
                    "postgre" in odbc_driver_lowercase
                    and "ansi" in odbc_driver_lowercase
                ):
                    selected_driver = odbc_driver
            elif db_type == "mariadb":
                # mariadb has only one type of odbc driver
                if "mariadb" in odbc_driver_lowercase:
                    selected_driver = odbc_driver
                    break
            elif db_type == "mysql":
                if (
                    "mysql" in odbc_driver_lowercase
                    and "unicode" in odbc_driver_lowercase
                ):
                    selected_driver = odbc_driver
                    # We usually want the unicode drivers, so break once we've found it
                    break
                elif (
                    "mysql" in odbc_driver_lowercase and "ansi" in odbc_driver_lowercase
                ):
                    selected_driver = odbc_driver

    CommonUtil.ExecLog(sModuleInfo, "[Database ODBC DRIVER]: %s" % selected_driver, 0)
    return selected_driver


def handle_db_exception(sModuleInfo, e):
    import pyodbc

    if isinstance(e, pyodbc.DataError):
        traceback.print_exc()
        CommonUtil.ExecLog(sModuleInfo, "pyodbc.DataError", 3)
        return CommonUtil.Exception_Handler(e)

    if isinstance(e, pyodbc.InternalError):
        traceback.print_exc()
        CommonUtil.ExecLog(sModuleInfo, "pyodbc.InternalError", 3)
        return CommonUtil.Exception_Handler(e)

    if isinstance(e, pyodbc.IntegrityError):
        traceback.print_exc()
        CommonUtil.ExecLog(sModuleInfo, "pyodbc.IntegrityError", 3)
        return CommonUtil.Exception_Handler(e)

    if isinstance(e, pyodbc.OperationalError):
        traceback.print_exc()
        CommonUtil.ExecLog(sModuleInfo, "pyodbc.OperationalError", 3)
        return CommonUtil.Exception_Handler(e)

    if isinstance(e, pyodbc.NotSupportedError):
        traceback.print_exc()
        CommonUtil.ExecLog(sModuleInfo, "pyodbc.NotSupportedError", 3)
        return CommonUtil.Exception_Handler(e)

    if isinstance(e, pyodbc.ProgrammingError):
        traceback.print_exc()
        CommonUtil.ExecLog(sModuleInfo, "pyodbc.ProgrammingError", 3)
        return CommonUtil.Exception_Handler(e)
    else:
        CommonUtil.ExecLog(sModuleInfo, "Database exception:\n%s" % e, 3)
        return CommonUtil.Exception_Handler(sys.exc_info())


# [NON ACTION]
@logger
def db_get_connection():
    """
    Convenience function for getting the cursor for db access
    :return: pyodbc.Cursor
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        import pyodbc
        db_con = None

        # Alias for Shared_Resources.Get_Shared_Variables
        g = sr.Get_Shared_Variables

        # Get the values
        db_type = g(DB_TYPE)
        db_name = g(DB_NAME)
        db_user_id = g(DB_USER_ID)
        db_password = g(DB_PASSWORD)
        db_host = g(DB_HOST)
        db_port = int(g(DB_PORT))

        if "postgres" in db_type:
            import psycopg2

            # Connect to db
            db_con = psycopg2.connect(
                user=db_user_id,
                password=db_password,
                database=db_name,
                host=db_host,
                port=db_port
            )
        elif "mysql" in db_type:
            import mysql.connector

            # Connect to db
            db_con = mysql.connector.connect(
                user=db_user_id,
                password=db_password,
                database=db_name,
                host=db_host,
                port=db_port
            )
        elif "mariadb" in db_type:
            import mariadb

            # Connect to db
            db_con = mariadb.connect(
                user=db_user_id,
                password=db_password,
                database=db_name,
                host=db_host,
                port=db_port
            )
        else:
            # Get the driver for the ODBC connection
            odbc_driver = find_odbc_driver(db_type)

            # Construct the connection string
            connection_str = f"DRIVER={{{odbc_driver}}};UID={db_user_id};PWD={db_password};DATABASE={db_name};SERVER={db_host};PORT={db_port}"

            # Connect to db
            db_con = pyodbc.connect(connection_str)

            db_con.setdecoding(pyodbc.SQL_CHAR, encoding="utf-8")
            db_con.setdecoding(pyodbc.SQL_WCHAR, encoding="utf-8")
            db_con.setencoding(encoding="utf-8")

        # Get db_cursor
        return db_con

    except Exception as e:
        return handle_db_exception(sModuleInfo, e)


@logger
def connect_to_db(data_set):
    """
    This action just stores the different database specific configs into shared variables for use by other actions.
    NOTE: The actual db connection does not happen here, connection to db is made inside the actions which require it.

    db_type         input parameter         <type of db, ex: postgres, mysql>
    db_name         input parameter         <name of db, ex: zeuz_db>
    db_user_id      input parameter         <user id of the os who have access to the db, ex: postgres>
    db_password     input parameter         <password of db, ex: mydbpass-mY1-t23z>
    db_host         input parameter         <host of db, ex: localhost, 127.0.0.1>
    db_port         input parameter         <port of db, ex: 5432 for postgres by default>
    odbc_driver     optional parameter      <specify the odbc driver, optional, can be found from pyodbc.drivers()>
    connect to db   database action         Connect to a database

    :param data_set: Action data set
    :return: string: "passed" or "failed" depending on the outcome
    """

    try:
        for left, _, right in data_set:
            if left == DB_TYPE:
                sr.Set_Shared_Variables(DB_TYPE, right)
            if left == DB_NAME:
                sr.Set_Shared_Variables(DB_NAME, right)
            if left == DB_USER_ID:
                sr.Set_Shared_Variables(DB_USER_ID, right)
            if left == DB_PASSWORD:
                sr.Set_Shared_Variables(DB_PASSWORD, right, allowEmpty=True)
            if left == DB_HOST:
                sr.Set_Shared_Variables(DB_HOST, right)
            if left == DB_PORT:
                sr.Set_Shared_Variables(DB_PORT, right)
            if left == DB_ODBC_DRIVER:
                sr.Set_Shared_Variables(DB_ODBC_DRIVER, right)

        return "passed"
    except Exception:
        traceback.print_exc()
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def db_select(data_set):
    """
    This action performs a select query and stores the result of the query in the variable <var_name>
    The result will be stored in the format: list of lists
        [ [row1...], [row2...], ... ]

    query               input parameter         <query: SELECT * FROM test_cases ORDER BY tc_id ASC LIMIT 10>
    select query        database action         <var_name: name of the variable to store the result of the query>

    :param data_set: Action data set
    :return: string: "passed" or "failed" depending on the outcome
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        variable_name = None
        query = None

        for left, mid, right in data_set:
            if left == "query":
                # Get the and query, and remove any whitespaces
                query = right.strip()

            if "action" in mid:
                variable_name = right.strip()

        if variable_name is None:
            CommonUtil.ExecLog(sModuleInfo, "Variable name must be provided.", 3)
            return "failed"
        
        if query is None:
            CommonUtil.ExecLog(sModuleInfo, "SQL query must be provided.", 3)
            return "failed"

        # Get db_cursor and execute
        db_con = db_get_connection()
        db_cursor = db_con.cursor()
        db_cursor.execute(query)

        # Fetch all rows and convert into list
        db_rows = []
        while True:
            db_row = db_cursor.fetchone()
            if not db_row:
                break
            db_rows.append(list(db_row))

        # Set the rows as a shared variable
        sr.Set_Shared_Variables(variable_name, db_rows)

        CommonUtil.ExecLog(
            sModuleInfo,
            "Fetched %d rows and stored into variable: %s"
            % (len(db_rows), variable_name),
            0,
        )
        return "passed"
    except Exception as e:
        return handle_db_exception(sModuleInfo, e)


@logger
def select_from_db(data_set):
    """
    This action performs a select query and stores the result of the query in the variable <var_name>
    The result will be stored in the format: list of lists
        [ [row1...], [row2...], ... ]

    table             input parameter         <table name: test >
    columns             input parameter         <column name: name,id>
    select from db        database action         <var_name: name of the variable to store the result of the query>

    :param data_set: Action data set
    :return: string: "passed" or "failed" depending on the outcome
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        table_name = None
        query = None
        where=None
        columns=None
        variable_name=None
        group_by=None
        order_by=None
        order=" "

        for left, mid, right in data_set:
            if "table" in left.lower():
                # Get the and query, and remove any whitespaces
                table_name= right.strip()
            if left.lower()=="where":
                where=right.strip()
            if "action" in mid.lower():
                variable_name = right.strip()
            if "group" in left.lower():
                group_by=right.split(',')
            if "order" in left.lower():
                order_by=right.split(',')

            if "columns" in left.lower():
                if right=="" or right=="*":
                    columns=["*"]
                columns=right.split(',')

        if variable_name is None:
            CommonUtil.ExecLog(sModuleInfo, "Variable name must be provided.", 3)
            return "failed"

        query="select "
        for index in range(len(columns)):
            query+=columns[index]+" "
            if(index!=(len(columns)-1)):
                query+=","

        query+="from "+table_name
        if where is not None:
            query+=" where "+where

        if group_by is not  None:
            query+=" group by "
            for index in range(len(group_by)):
                query+=group_by[index]+" "
                if(index!=(len(group_by)-1)):
                    query+=","

        if order_by is not None:
            query += " order by "
            for index in range(len(order_by)):
                query += order_by[index] + " "
                if (index != (len(order_by) - 1)):
                    query += ","

        # Get db_cursor and execute
        db_con = db_get_connection()
        db_cursor = db_con.cursor()
        db_cursor.execute(query)
        # Commit the changes
        db_con.commit()
        # Fetch all rows and convert into list
        db_rows = []
        while True:
            db_row = db_cursor.fetchone()
            if not db_row:
                break
            db_rows.append(list(db_row))

        # Set the rows as a shared variable
        sr.Set_Shared_Variables(variable_name, db_rows)

        CommonUtil.ExecLog(
            sModuleInfo,
            "Fetched %d rows and stored into variable: %s"
            % (len(db_rows), variable_name),
            0,
        )
        return "passed"
    except Exception as e:
        return handle_db_exception(sModuleInfo, e)


@logger
def insert_into_db(data_set):
    """
    This action performs a  insert query and stores the "number of rows affected"
    in the variable <var_name>

    The result will be stored in the format: int
        value

    table             input parameter         <table name: test >
    columns             input parameter         <column name: name>
    values             input parameter         <values : admin>
    insert into db        database action         <var_name: name of the variable to store the result of the query>

    :param data_set: Action data set
    :return: string: "passed" or "failed" depending on the outcome
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        table_name = None
        query = None
        values=None
        columns=None
        variable_name=None

        for left, mid, right in data_set:
            if "table" in left.lower():
                # Get the and query, and remove any whitespaces
                table_name= right.strip()
            if "values" in left.lower():
                values=right.split(',')
            if "action" in mid:
                variable_name = right.strip()
            if "columns" in left.lower():
                columns=right.split(',')

        if variable_name is None:
            CommonUtil.ExecLog(sModuleInfo, "Variable name must be provided.", 3)
            return "failed"

        query="insert into  "+table_name+' ( '
        for index in range(len(columns)):
            query+=columns[index]+" "
            if(index!=(len(columns)-1)):
                query+=","
                # Get db_cursor and execute
        query+=") values ("
        for index in range(len(values)):
            query += values[index] + " "
            if (index != (len(values) - 1)):
                query += ","
        query+=" ) "
        db_con = db_get_connection()
        db_cursor = db_con.cursor()
        db_cursor.execute(query)
        # Commit the changes
        db_con.commit()

        # Fetch the number of rows affected
        db_rows_affected = db_cursor.rowcount

        # Set the rows as a shared variable
        sr.Set_Shared_Variables(variable_name, db_rows_affected)

        CommonUtil.ExecLog(
            sModuleInfo, "Number of rows affected: %d" % db_rows_affected, 0
        )
        return "passed"

    except Exception as e:
        return handle_db_exception(sModuleInfo, e)


@logger
def delete_from_db(data_set):
    """
    This action performs a  delete query and stores the "number of rows affected"
    in the variable <var_name>

    The result will be stored in the format: int
        value

    table             input parameter         <table name: test >
    where             input parameter         <where condition: name='admin'>
    delete from db        database action         <var_name: name of the variable to store the result of the query>

    :param data_set: Action data set
    :return: string: "passed" or "failed" depending on the outcome
    """


    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        table_name = None
        query = None
        where = None
        variable_name = None

        for left, mid, right in data_set:
            if "table" in left.lower():
                # Get the and query, and remove any whitespaces
                table_name = right.strip()
            if left == "where":
                where = right.strip()
            if "action" in mid:
                variable_name = right.strip()

        if variable_name is None:
            CommonUtil.ExecLog(sModuleInfo, "Variable name must be provided.", 3)
            return "failed"

        query = "delete from "+ table_name
        if where is not None:
            query +=" where "+where
        # Get db_cursor and execute
        db_con = db_get_connection()
        db_cursor = db_con.cursor()
        db_cursor.execute(query)

        # Commit the changes
        db_con.commit()

        # Fetch the number of rows affected
        db_rows_affected = db_cursor.rowcount

        # Set the rows as a shared variable
        sr.Set_Shared_Variables(variable_name, db_rows_affected)

        CommonUtil.ExecLog(
            sModuleInfo, "Number of rows affected: %d" % db_rows_affected, 0
        )
        return "passed"

    except Exception as e:
        return handle_db_exception(sModuleInfo, e)


@logger
def update_into_db(data_set):
    """
    This action performs a  update query and stores the "number of rows affected"
    in the variable <var_name>

    The result will be stored in the format: int
        value

    table             input parameter         <table name: test >
    columns             input parameter         <column name: name>
    values             input parameter         <column name: admin>
    where             input parameter         <where condition: name='admin'>
    update into db        database action         <var_name: name of the variable to store the result of the query>

    :param data_set: Action data set
    :return: string: "passed" or "failed" depending on the outcome
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        table_name = None
        query = None
        where=None
        columns=None
        values=None
        variable_name=None

        for left, mid, right in data_set:
            if "table" in left.lower():
                # Get the and query, and remove any whitespaces
                table_name= right.strip()
            if left=="where":
                where=right.strip()
            if "action" in mid:
                variable_name = right.strip()
            if "columns" in left.lower():
                columns=right.split(',')
            if "values" in left.lower():
                values=right.split(',')

        if variable_name is None:
            CommonUtil.ExecLog(sModuleInfo, "Variable name must be provided.", 3)
            return "failed"

        query="update "+table_name+" set "
        for index in range(len(columns)):
            query+=columns[index]+"= "
            query+=values[index]+" "
            if(index!=(len(columns)-1)):
                query+=","
        if where is not None:
            query+=" where "+where
        # Get db_cursor and execute
        db_con = db_get_connection()
        db_cursor = db_con.cursor()
        db_cursor.execute(query)
        db_con.commit()

        # Fetch the number of rows affected
        db_rows_affected = db_cursor.rowcount

        # Set the rows as a shared variable
        sr.Set_Shared_Variables(variable_name, db_rows_affected)

        CommonUtil.ExecLog(
            sModuleInfo, "Number of rows affected: %d" % db_rows_affected, 0
        )
        return "passed"

    except Exception as e:
        return handle_db_exception(sModuleInfo, e)


@logger
def db_non_query(data_set):
    """
    This action performs a non-query (insert/update/delete) query and stores the "number of rows affected"
    in the variable <var_name>

    The result will be stored in the format: int
        value

    query                            input parameter    <query: INSERT INTO table_name(col1, col2, ...) VALUES (val1, val2, ...)>
    insert update delete query       database action    <var_name: name of the variable to store the no of rows affected>

    :param data_set: Action data set
    :return: string: "passed" or "failed" depending on the outcome
    """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        variable_name = None
        query = None

        for left, mid, right in data_set:
            if left == "query":
                # Get the query, and remove any whitespaces
                query = right.strip()

            if "action" in mid:
                variable_name = right.strip()
        
        if variable_name is None:
            CommonUtil.ExecLog(sModuleInfo, "Variable name must be provided.", 3)
            return "failed"
        
        if query is None:
            CommonUtil.ExecLog(sModuleInfo, "SQL query must be provided.", 3)
            return "failed"

        # Get db_cursor and execute
        db_con = db_get_connection()
        db_cursor = db_con.cursor()
        db_cursor.execute(query)

        # Commit the changes
        db_con.commit()

        # Fetch the number of rows affected
        db_rows_affected = db_cursor.rowcount

        # Set the rows as a shared variable
        sr.Set_Shared_Variables(variable_name, db_rows_affected)

        CommonUtil.ExecLog(
            sModuleInfo, "Number of rows affected: %d" % db_rows_affected, 0
        )
        return "passed"
    except Exception as e:
        return handle_db_exception(sModuleInfo, e)
