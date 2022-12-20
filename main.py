import pandas as pd
import numpy as np
import copy
import tweet_input_output_functions
from tweet_analysis_functions import prefilter_tweet
import sql_connection


def main():
    #nlp = spacy.load('ja_ginza_electra')  #No idea when to deal with this
    tweet_data_frame_list = []
    tweet_includes_frame_list = []
    location_keyword_list = ["伊牟田", "白糸滝", "香港"]
    debug_json_tweet_list = []
    prefiltered_tweet_list = []
    for location_keyword in location_keyword_list:
        json_tweet = tweet_input_output_functions.obtain_tweet(location_keyword , "2017-01-01"[CHANGE THIS TO A VARIABLE CORRESPODING TO START DATE AND LOOP],"2018-12-31"CHANGE THIS TO A VARIABLE CORRESPODING TO END DATE AND LOOP],"test_collection.json") ADD A FOR LOOP FOR EVERY 3 MONTHS (SO FOR EACH AREA, YOU GET 500 TWEETS EVERY 3 MONTHS) LANDY DID THIS SOMEWHERE WITH START AND END DATE LISTS
        BILLY YOU ALSO NEED TO OBTAIN AND STORE THE ACTUAL DATE OF THE TWEET IN THE DATABBASE TOO
        debug_tweet = copy.deepcopy(json_tweet) #this is for DEBUG purposes to check the effect of prefiltering
        debug_json_tweet_list.append(debug_tweet)
        
        prefiltered_tweet_list.append(prefilter_tweet(json_tweet)) #THIS DOESNT CATCH MULTIPLE LANGUAGES IN SAME TWEET, AND ALSO IT NEEDS TO BE FINE TUNED TO FURTHER REMOVE WEIRD TWEETS

        tweet_data_frame, tweet_includes_frame = tweet_input_output_functions.extract_information_from_tweet_json(json_tweet, location_keyword)
        tweet_data_frame_list.append(tweet_data_frame)
        tweet_includes_frame_list.append(tweet_includes_frame)


    database = r"scraped_tweets.db" #Sometimes update to commands don't update because constraints get passed to table despite other errors. In those cases, delete table and recreate one with new changes/params


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
    conn = sql_connection.create_connection(database)

    # create tables
    if conn is not None:

        # create tweet_data table
        sql_connection.create_table(conn, sql_create_data_table)

        # create tweet_includes table
        sql_connection.create_table(conn, sql_create_includes_table)
    else:
        print("Error! cannot create the database connection.")


    with conn:

        # populate data_table
        for tweet_data_frame in tweet_data_frame_list:
            list_of_tuples_from_data_frame = list(tweet_data_frame.itertuples(index=False, name=None))
            for data_tuple in list_of_tuples_from_data_frame:
                sql_connection.create_data_table(conn, data_tuple)

        # populate includes_table
        for tweet_includes_frame in tweet_includes_frame_list:
            list_of_tuples_from_includes_frame = list(tweet_includes_frame.itertuples(index=False, name=None))
            for includes_tuple in list_of_tuples_from_includes_frame:
                sql_connection.create_includes_table(conn, includes_tuple)


main()