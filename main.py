import sqlite3
from sqlite3 import Error
import requests
import os
import json
import pandas as pd
import numpy as np
import config
import spacy
import copy
from tweet_analysis_functions import prefilter_tweet


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
    sql = ''' INSERT INTO data_table(location_keyword, text , author_id, tweet_id, source, retweet_count, reply_count, like_count, quote_count)
              VALUES(?,?,?,?,?,?,?,?,?) '''
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

def obtain_tweet(_word, _start_time, _end_time,_output_Jsonfile):
    URL = "https://api.twitter.com/2/tweets/search/all"
    headers = {'Content-Type': 'text/plain', "Authorization": config.Bearer}
    query = _word +" -is:retweet"
    start_time = _start_time+"T00:00:00Z"
    end_time= _end_time+"T23:58:00Z"
    params = {
        "query":query, 
        "start_time":start_time,
        "end_time":end_time,
        "max_results":100,
        "expansions":"entities.mentions.username,author_id,attachments.media_keys,geo.place_id", 
        "tweet.fields":"created_at,geo,lang,entities,author_id,public_metrics,source",
        "media.fields":"preview_image_url,url",
        "place.fields":"country,country_code,full_name,geo,id,name,place_type",
        "user.fields":"created_at,description,id,location,name,username"
    }
    
    response = requests.get(URL, headers=headers, params=params).json()

    with open("test.json", "w") as outfile:
        json.dump(response, outfile)


    return response




def extract_information_from_tweet_json(tweet_json, location_searchterm):

    # Grab "data" data:
    tweet_location_searchterm_list = []
    tweet_text_list = []
    tweet_author_id_list = []
    tweet_tweet_id_list = []
    tweet_source_list = []
    tweet_retweet_count_list = []
    tweet_reply_count_list = []
    tweet_like_count_list = []
    tweet_quote_count_list = []
    tweet_language_list = []

    tweet_data = tweet_json["data"]
    for tweet in tweet_data:
        #From out of function
        tweet_location_searchterm_list.append(location_searchterm)
        #Top Level
        tweet_text = tweet["text"]
        tweet_author_id = tweet["author_id"]
        tweet_tweet_id = tweet["id"]
        tweet_source = tweet["source"]
        tweet_text_list.append(tweet_text)
        tweet_author_id_list.append(tweet_author_id)
        tweet_tweet_id_list.append(tweet_tweet_id)
        tweet_source_list.append(tweet_source)
        #One Level Down
        tweet_retweet_count = tweet["public_metrics"]["retweet_count"]
        tweet_reply_count = tweet["public_metrics"]["reply_count"]
        tweet_like_count = tweet["public_metrics"]["like_count"]
        tweet_quote_count = tweet["public_metrics"]["quote_count"]
        tweet_retweet_count_list.append(tweet_retweet_count)
        tweet_reply_count_list.append(tweet_reply_count)
        tweet_like_count_list.append(tweet_like_count)
        tweet_quote_count_list.append(tweet_quote_count)
        

    df_tweet_data = pd.DataFrame({"location_keyword":tweet_location_searchterm_list, "text":tweet_text_list , "author_id":tweet_author_id_list, 
                                    "tweet_id":tweet_tweet_id_list, "source":tweet_source_list,
                                    "retweet_count":tweet_retweet_count_list , "reply_count":tweet_reply_count_list, 
                                    "like_count":tweet_like_count_list, "quote_count":tweet_quote_count_list})
    
    
    # Grab "includes" data:
    user_location_searchterm_list = []
    user_username_list = []
    user_created_at_list = []
    user_description_list = []
    user_id_list = []
    user_location_list = []
    user_name_list = []

    tweet_includes = tweet_json["includes"]
    for user in tweet_includes["users"]:
        #From out of function
        user_location_searchterm_list.append(location_searchterm)
        #Top Level
        user_username = user["username"]
        user_created_at = user["created_at"]
        try:
            user_description = user["description"]
            if user_description == '': #Also catch empty strings, as well as no values
                print("This user did not write a description")
                user_description = np.nan
        except KeyError:
            print("This user did not write a description")
            user_description = np.nan
        user_id = user["id"]
        try:
            user_location = user["location"]
            if user_location == '': #Also catch empty strings, as well as no values
                print("This user did not specify a location")
                user_location= np.nan
        except KeyError:
            print("This user did not specify a location")
            user_location= np.nan
        user_name = user["name"]
        user_username_list.append(user_username)
        user_created_at_list.append(user_created_at)
        user_description_list.append(user_description)
        user_id_list.append(user_id)
        user_location_list.append(user_location)
        user_name_list.append(user_name)
        
    
        df_tweet_includes = pd.DataFrame({"location_keyword":user_location_searchterm_list, "username":user_username_list , "created_at":user_created_at_list, 
                                    "description":user_description_list, "user_id":user_id_list,
                                    "location":user_location_list , "name":user_name_list})
    
    
    return df_tweet_data, df_tweet_includes



def main():
    #nlp = spacy.load('ja_ginza_electra')  #No idea when to deal with this
    tweet_data_frame_list = []
    tweet_includes_frame_list = []
    location_keyword_list = ["伊牟田", "白糸滝", "香港"]
    debug_json_tweet_list = []
    prefiltered_tweet_list = []
    for location_keyword in location_keyword_list:
        json_tweet = obtain_tweet(location_keyword , "2019-01-01","2021-12-31","test_collection.json")
        debug_tweet = copy.deepcopy(json_tweet) #this is for DEBUG purposes to check the effect of prefiltering
        debug_json_tweet_list.append(debug_tweet)
        
        prefiltered_tweet_list.append(prefilter_tweet(json_tweet)) #THIS DOESNT CATCH MULTIPLE LANGUAGES IN SAME TWEET, AND ALSO IT NEEDS TO BE FINE TUNED TO FURTHER REMOVE WEIRD TWEETS

        tweet_data_frame, tweet_includes_frame = extract_information_from_tweet_json(json_tweet, location_keyword)
        tweet_data_frame_list.append(tweet_data_frame)
        tweet_includes_frame_list.append(tweet_includes_frame)


    database = r"scraped_tweets5.db" #Sometimes update to commands don't update because constraints get passed to table despite other errors. In those cases, delete table and recreate one with new changes/params


    sql_create_data_table = """CREATE TABLE IF NOT EXISTS data_table (
                                    location_keyword text NOT NULL,
                                    text text NOT NULL,
                                    author_id text NOT NULL, 
                                    tweet_id text NOT NULL,
                                    source text NOT NULL,
                                    retweet_count float NOT NULL,
                                    reply_count float NOT NULL,
                                    like_count float NOT NULL,
                                    quote_count float NOT NULL
                                );"""


    sql_create_includes_table = """CREATE TABLE IF NOT EXISTS includes_table (
                                    location_keyword text NOT NULL,
                                    username text NOT NULL,
                                    created_at datetime NOT NULL, 
                                    description text,
                                    user_id text NOT NULL,
                                    location text,
                                    name text NOT NULL
                                );"""


    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:

        # create tweet_data table
        create_table(conn, sql_create_data_table)

        # create tweet_includes table
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


main()