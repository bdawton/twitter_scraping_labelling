# =============== packages ===================================================
import re
import emoji
#==============================================================================
emoji_pattern = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
    "+", flags=re.UNICODE)
#================ remove emoji from text ============================ #FOR NOW LETS CONTINUE REMOVING THEM, BUT MAYBE IN FUTURE MIGHT BE USEFUL? FOR LABELLING? DUNNO LOL ....
def removeEmoji(text):
    #intermediate_text= emoji_pattern.sub(r'', text)
    #text = re.sub(r'[^(a-z|A-Z)]', ' ', intermediate_text)
    return emoji_pattern.sub(r' ', text)
#=====================================================
def removePythonEmoji(text):  
    return emoji.replace_emoji(text, ' ')
#==============================================================================
def removeUserMention(_text):
    text_tab=_text.split("@")
    result=""
    for item in text_tab:
        words=item.split(" ")
        for word in words:
            if "@"+word not in _text:
                result+=word+" "
    return(result.strip())
#==============================================================================
def prefilter_tweet(tweet_json):
    pop_idx_list = []
    idx=0
    for tweet in tweet_json['data']:
        if tweet['lang']=="ja" or ("I am at " in tweet['text']) or ("I'm at " in tweet['text']) or ("I was at " in tweet['text']):
            prefiltered_text = removeEmoji(tweet['text'])
            prefiltered_text = removePythonEmoji(prefiltered_text)
            prefiltered_text = removeUserMention(prefiltered_text)
            tweet['text'] = prefiltered_text

        else:
            print("deleting tweet")
            pop_idx_list.append(idx)
            
        idx += 1

    tweet_json['data'] = [i for j, i in enumerate(tweet_json['data']) if j not in set(pop_idx_list)] #set should be faster than list here


    return tweet_json
