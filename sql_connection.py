import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_data_table(conn, tweet_table):
    """
    Create a new entry into the data_table table
    """
    sql = ''' INSERT INTO data_table(location_keyword, text , author_id, tweet_id, source, created_at, retweet_count, reply_count, like_count, quote_count)
              VALUES(?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, tweet_table)
    conn.commit()
    return cur.lastrowid

def create_includes_table(conn, tweet_table):
    """
    Create a new entry into the includes_table table
    """
    sql = ''' INSERT INTO includes_table(location_keyword, username , created_at, description, user_id, location, name)
              VALUES(?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, tweet_table)
    conn.commit()
    return cur.lastrowid