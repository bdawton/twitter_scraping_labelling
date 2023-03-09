import pandas as pd
import numpy as np
import scipy.stats as st
import math
from sklearn.model_selection import train_test_split
from postgres_connection import create_postgres_database

df_full_data = pd.read_csv('df_full_data.csv', index_col='index', lineterminator='\n')
#df_full_includes = pd.read_csv('df_full_includes.csv', lineterminator='\n')
df_full_data.dropna(subset = ['text'], inplace=True)


df_2018_data= df_full_data[df_full_data.created_at.str[:4]=='2018']
df_2022_data = df_full_data[df_full_data.created_at.str[:4]=='2022']


#df_full_data[df_full_data.created_at.str[:4]=="2018"].count()
#df_full_data[df_full_data.created_at.str[:4]=="2022"].count()


# Cochran formula is from here

# Parameter setting for Cochran's formula

Z = st.norm.ppf(1-0.025) # Critical score for a significance level (alpha) = 5% IS THERE ANY REASON WHY HE WROTE IT LIKE THAT?
p = 0.5  # Probability of a tweet to be choosen as a sample (Bernoulli's even) when the real proportion in unknown
e = 0.02 # Desired margin of error (precision)




# Cochran's formula n_0 = (Z^2)*p*(1-p)/(e^2)
# n_0 is sample size for unknown data size
#INTERESTING, IT'S COMPLETELY INDEPENDENT OF THE ORIGINAL SIZE


n_0 = (Z**2)*p*(1-p)/(e**2)


N_2018 = df_full_data[df_full_data.created_at.str[:4]=='2018'].shape[0]
N_2022 = df_full_data[df_full_data.created_at.str[:4]=='2022'].shape[0]

# Adjustment of Cochran formula n = n_0/(1+(n_0-1)/N)
# n is an adjustment of sample size if we have only N data size.

n_2018 = math.ceil(n_0/(1+(n_0-1)/N_2018))
n_2022 = math.ceil(n_0/(1+(n_0-1)/N_2022))

#But original sample-size information is used here, I wonder how Ristu determined adjustment was needed

prop_2018 = round(n_2018/N_2018, 2)
prop_2022 = round(n_2022/N_2022, 2)
##### This is old code

r_s = 0
subsampled_df_list = []

for df,prop in zip([df_2018_data, df_2022_data],[prop_2018, prop_2022]):

    # dividing the data into groups
    # instantiating stratified sampling
    subsample_proportion = prop
    split_outputs = train_test_split(df, df.location_category, test_size = subsample_proportion, random_state=r_s, stratify=df.location_category)
    subsampled_df = split_outputs[1] #This corresponds to x_test output
    subsampled_df_list.append(subsampled_df)

# Only send to postgres for now. This is a bit of a hack workaround, as we are treating the 2018 and 2022 data tables ONLY (figure out the user data info later)
create_postgres_database(subsampled_df_list[0], subsampled_df_list[1], 'subsampled_data_2018_table', 'subsampled_data_2022_table')