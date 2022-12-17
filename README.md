# twitter_scraping_labelling
Pulls tweets based on location keyword, and create a labelling application to label them as tourism-relevant or not!

Current status:
-Pull Tweets using API based on timeframe and keywords
-Prefilter tweets (only keep Japanese language tweets, or English tweets explicitly mentionning tourist activities. Remove emojis and mentions)
-Load into database (SQLite)
-Working on:Stratified sampling for labelling
