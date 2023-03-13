# twitter_scraping_labelling
Pulls tweets based on location keyword, and create a labelling application to label them as tourism-relevant or not!

Current status:
- Pull Tweets using API based on timeframe and keywords
- Prefilter tweets (only keep Japanese language tweets, or English tweets explicitly mentioning tourist activities. Remove emojis and mentions)
- Load into database (SQLite or PostgreSQL)
- Stratified time-based sampling for labelling
- *Working on*: Labelling process, and then relevance model (different repo)
