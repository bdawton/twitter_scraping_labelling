import requests
import json
import pandas as pd
import numpy as np
import config




def obtain_tweet(_word, _start_time, _end_time):
    URL = "https://api.twitter.com/2/tweets/search/all"
    headers = {'Content-Type': 'text/plain', "Authorization": config.Bearer}
    query = _word +" -is:retweet"
    start_time = _start_time+"T00:00:00Z"
    end_time= _end_time+"T23:58:00Z"
    params = {
        "query":query, 
        "start_time":start_time,
        "end_time":end_time,
        "max_results":500, #Max comme Landy
        "expansions":"entities.mentions.username,author_id,attachments.media_keys,geo.place_id", 
        "tweet.fields":"created_at,geo,lang,entities,author_id,public_metrics,source",
        "media.fields":"preview_image_url,url",
        "place.fields":"country,country_code,full_name,geo,id,name,place_type",
        "user.fields":"created_at,description,id,location,name,username"
    }
    
    response = requests.get(URL, headers=headers, params=params).json()

    return response




def extract_information_from_tweet_json(tweet_data, tweet_users, location_searchterm):

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
    tweet_created_at_list = []


    for tweet in tweet_data:
        #From out of function
        tweet_location_searchterm_list.append(location_searchterm)
        #Top Level
        tweet_text = tweet["text"]
        tweet_author_id = tweet["author_id"]
        tweet_tweet_id = tweet["id"]
        if "source" in tweet_data:
            tweet_source = tweet["source"]
        else:
            tweet_source = np.nan
        tweet_created_at = tweet["created_at"]
        tweet_text_list.append(tweet_text)
        tweet_author_id_list.append(tweet_author_id)
        tweet_tweet_id_list.append(tweet_tweet_id)
        tweet_source_list.append(tweet_source)
        tweet_created_at_list.append(tweet_created_at)
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
                                    "tweet_id":tweet_tweet_id_list, "source":tweet_source_list, "created_at":tweet_created_at_list,
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


    for user in tweet_users:
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