import pandas as pd
import numpy as np
import copy
import time
import json
from tweet_input_output_functions import obtain_tweet, extract_information_from_tweet_json
from tweet_analysis_functions import prefilter_tweet
import sqlite3_connection
import postgres_connection


def main(db_type):

    #nlp = spacy.load('ja_ginza_electra')  #No idea when to deal with this
    tweet_data_frame_list = []
    tweet_users_frame_list = []
    start_dates=["2018-01-01","2018-04-01","2018-07-01","2018-10-01","2022-01-01","2022-04-01","2022-07-01","2022-10-01"]
    end_dates=["2018-03-31","2018-06-30","2018-09-30","2018-12-31","2022-03-31","2022-06-30","2022-09-30","2022-12-31"]

    text_file = open('tweet_queries.txt', 'r')
    
    lines = text_file.readlines()
    
    counter = 0

    for line in lines:
        # Get next line from file

        print(f"counter: {counter}")
        

        if line[0] != "=":

            location_keyword = line
            counter += 1

            for c in ['\\', '&', '.', '"', "'", "and"]: #The requests module doesn't like these characters, so we need to add a preventative backslash
                if c in line:
                    location_keyword = line.replace(c, "\\"+c)


            print(location_keyword)
            

            for start_date, end_date in zip(start_dates, end_dates):
                json_tweet = obtain_tweet(location_keyword , start_date, end_date)
                # Serializing json
                json_object = json.dumps(json_tweet)
                with open("log.txt", "w") as outfile:
                    outfile.write(json_object)
                time.sleep(2.5) #To avoid too many requests error
                
                try:
                    json_tweet["meta"] # Test if service is available (too many requests, or service unavailable)
                except KeyError:
                    print("key error")
                    flag = None
                    while flag is None:
                        print('waiting')
                        time.sleep(5) #Wait a bit in case service comes back online
                        json_tweet = obtain_tweet(location_keyword , start_date, end_date) #Then request again
                        print(flag)
                        try:
                            flag = json_tweet["meta"]
                            print("flag exists")
                            print(json_tweet)
                        except KeyError:
                            print("service still unavailable")
                            print(json_tweet)
                else: 
                    print("tweet exists") # If everything is OK, and the try statement works, print this
                    
                if json_tweet["meta"]["result_count"] == 0:# also need to check length here
                    print('tweet exists but no relevant results')
                    print('moving on to next keyword in list')
                    continue # Just go back to start of for loop and continue
                    
                else:
                    print('relevant results exist and will be logged')

                tweet_data_frame, tweet_users_frame = extract_information_from_tweet_json(*prefilter_tweet(json_tweet), location_keyword) #asterisk to unpack the two returned values and use as inputs
                tweet_data_frame_list.append(tweet_data_frame)
                tweet_users_frame_list.append(tweet_users_frame)
                
                print('moving on to next keyword in list')

    text_file.close()
    print('finished running through text file')
    
    if db_type == 'sqlite':
        sqlite3_connection.create_sqlite_database('scrapedtweets.db', tweet_data_frame_list, tweet_users_frame_list)
    elif db_type == 'postgres':
        concat_tweet_data_frame = pd.concat(tweet_data_frame_list)
        concat_tweet_users_frame = pd.concat(tweet_users_frame_list)
        postgres_connection.create_postgres_database(concat_tweet_data_frame, concat_tweet_users_frame)
    else:
        print('please specify a db type')


main(db_type = 'postgres')

print("finished")