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
    sql = ''' INSERT INTO data_table(location_category, location_keyword, text , author_id, tweet_id, source, created_at, retweet_count, reply_count, like_count, quote_count)
              VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, tweet_table)
    conn.commit()
    return cur.lastrowid

def create_includes_table(conn, tweet_table):
    """
    Create a new entry into the includes_table table
    """
    sql = ''' INSERT INTO includes_table(location_category, location_keyword, username , created_at, description, user_id, location, name)
              VALUES(?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, tweet_table)
    conn.commit()
    return cur.lastrowid

def create_sqlite_database(database_name, tweet_data_frame_list, tweet_includes_frame_list):
    # create a database connection
    conn = create_connection(database_name)

    # create tables
    if conn is not None:
        
        # create tweet_data table
        sql_create_data_table = """CREATE TABLE IF NOT EXISTS data_table (
                                            location_category text NOT NULL,
                                            location_keyword text NOT NULL,
                                            text text NOT NULL,
                                            author_id text NOT NULL, 
                                            tweet_id text NOT NULL,
                                            source text,
                                            created_at datetime NOT NULL, 
                                            retweet_count float NOT NULL,
                                            reply_count float NOT NULL,
                                            like_count float NOT NULL,
                                            quote_count float NOT NULL
                                        );"""
        create_table(conn, sql_create_data_table)

        # create tweet_includes table
        sql_create_includes_table = """CREATE TABLE IF NOT EXISTS includes_table (
                                location_category text NOT NULL,
                                location_keyword text NOT NULL,
                                username text NOT NULL,
                                created_at datetime NOT NULL, 
                                description text,
                                user_id text NOT NULL,
                                location text,
                                name text NOT NULL
                            );"""
        create_table(conn, sql_create_includes_table)

    else:
        print("Error! cannot create the database connection.")


    with conn:

        # populate data_table
        for tweet_data_frame in tweet_data_frame_list:
            list_of_tuples_from_data_frame = list(tweet_data_frame.itertuples(index=False, name=None))
            for data_tuple in list_of_tuples_from_data_frame:
                create_data_table(conn, data_tuple)

        # populate includes_table
        for tweet_includes_frame in tweet_includes_frame_list:
            list_of_tuples_from_includes_frame = list(tweet_includes_frame.itertuples(index=False, name=None))
            for includes_tuple in list_of_tuples_from_includes_frame:
                create_includes_table(conn, includes_tuple)
