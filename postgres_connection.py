import pandas as pd
import sqlalchemy as sa
import psycopg2
import config
from tweet_analysis_functions import prefilter_tweet

engine = sa.create_engine(config.engine ,connect_args={"connect_timeout": 60})

def create_postgres_database(tweet_data_frame_list, tweet_users_frame_list):

    data_table_name = 'data_table'
    users_table_name = 'users_table'


    if (isinstance(tweet_data_frame_list, pd.DataFrame) and isinstance(tweet_users_frame_list, pd.DataFrame)):
        df_data = tweet_data_frame_list
        df_users = tweet_users_frame_list

    elif (isinstance(tweet_data_frame_list, list) and isinstance(tweet_users_frame_list, list)):    
        df_data = pd.concat(tweet_data_frame_list)
        df_users = pd.concat(tweet_users_frame_list)

    else:
        print('Error')
        return


    df_data.to_sql(
    name=data_table_name.lower(), 
    con=engine, 
    if_exists='replace'  # If the table already exists, replace it
    )

    df_users.to_sql(
    name=users_table_name.lower(), 
    con=engine, 
    if_exists='replace'  # If the table alrady exists, replace it
    )
