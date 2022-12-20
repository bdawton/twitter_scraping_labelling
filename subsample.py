import pandas as pd
import numpy as np
import sqlite3
from sklearn.model_selection import train_test_split

r_s = 0
# Read sqlite query results into a pandas DataFrame
con = sqlite3.connect("scraped_tweets.db")
df = pd.read_sql_query("SELECT * from data_table", con)

# Verify that result of SQL query is stored in the dataframe
print(df.head())

con.close()

# dividing the data into groups
# instantiating stratified sampling
subsample_proportion = 0.1
split_outputs = train_test_split(df, df.location_keyword, test_size = subsample_proportion, random_state=r_s, stratify=df.location_keyword)
subsampled_df = split_outputs[1] #This corresponds to x_test output
print("toto")

#PULL FROM SQL
#SUBSAMPLE
#PLOT STATS FOR BOTH (MAYBE THE PLOTTING WILL WORK BETTER ON JUPYTER?)df.columns