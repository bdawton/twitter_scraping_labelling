#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============== packages ===================================================
from pickle import FALSE
import spacy
import json
import os
import csv
#import numpy as np
import re
import emoji
#=============================================================================
#========= Global variables =================================================
current_dir = os.path.dirname(__file__)
collectionWithODFile = "Data/Tweets/CollectionWithOD.json"
nounVerbCSV = "AnalysisResult/noun_verb.csv"
nounCooccurence_file = "AnalysisResult/noun_cooccurence.json"
nlp = spacy.load('ja_ginza_electra')
nouns_tweet_list=[]

input_folder ="Data/Tweets"
#input_data=[]
MAX_NOUN_WSIZE=2
#============================================================================
#============ Global functions ==============================================
def parseListObjectInfo (_list_objects):
    data=""
    for item in _list_objects:
        if 'text' in item:
            doc = nlp(item['text'])
            nouns_tweet=[]
            for sent in doc.sents:
                token_array = []
                nouns = []

                for token in sent:
                    #print(token.i, token.orth_, token.lemma_, token.pos_)
                    #if token.pos_ == 'VERB' and token.lemma_=='する':
                    if token.pos_ == 'VERB':
                        #print("here : "+str(sent))
                        """
                        print('##########size:'+str(len(token_array)))
                        for t in token_array:
                            print (t['word']+" :"+t['type'])
                        """
                        
                        if len(token_array)>=2 and token_array[len(token_array)-1]['type']=='ADP':
                            #print(token_array[len(token_array)-2]['word']+" type:"+token_array[len(token_array)-2]['type']+" verb:"+token.lemma_)
                            nouns = []
                            noun_detected=False
                            accepted_adp=0
                            for index in range(len(token_array)-MAX_NOUN_WSIZE, -1, -1): #LIFO
                                #print('//////'+str(index))
                                if token_array[index]['type']=='NOUN' or token_array[index]['type']=='PROPN':
                                    #print('****** '+token_array[index]['word'])
                                    word_modif = token_array[index]['word'].strip()
                                    nouns.append(word_modif)
                                    #nouns.append(token_array[index]['word'])
                                    noun_detected=True
                                else:
                                    if noun_detected==True and token_array[index]['type']=='ADP':
                                        if accepted_adp<=MAX_NOUN_WSIZE:
                                           # print('****** '+token_array[index]['word'])
                                            if token_array[index]['word']=='の' or token_array[index]['word']=='で':
                                                #nouns.append(token_array[index]['word'])
                                                word_modif = token_array[index]['word'].strip()
                                                nouns.append(word_modif)
                                            else:
                                                break
                                        accepted_adp +=1
                                    else:
                                        #print('br')
                                        break
                                if noun_detected==True and accepted_adp>MAX_NOUN_WSIZE:
                                    #print('break')
                                    break

                            result =''
                            #print('size nouns :'+str(len(nouns)))
                            for index in range(len(nouns)-1, -1, -1):
                                result += nouns[index] + ' '

                            #print(' '+result.replace('\n',' ')+' '+token_array[len(token_array)-1]['word']+' '+token.lemma_)
                            if result !='':
                                data_item=""
                                data_item += result.replace('\n',' ')+"," #noun
                                data_item += token_array[len(token_array)-1]['word']+"," #particle
                                data_item+= token.lemma_+"\n" #verb
                                data += data_item

                                print(data_item.replace(',',' '))
                                #data.insert(len(data),data_item)
                                #data.append(data_item)

                        token_array = []
                        
                    
                    else:
                        if token.pos_ != 'SYM':
                            token_obj={'word':token.lemma_,'type':token.pos_}
                            token_array.append(token_obj)
                    if token.pos_ == 'PUNCT':
                        token_array = []
                        nouns_tweet = nouns_tweet + nouns
                        nouns = []
                    
                #print('EOS')
                #print('========================')
            nouns_tweet_list.append(nouns_tweet)
    #print(data)
    return data
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
def analyzeSyntax(_text):
    #************** Rules ************** 
    """
    R1) NOUN/PROPN  + NOUN/PROPN + NOUN/PROPN ... = NOUN
    R2) NOUN/PROPN + ADP(NO) + NOUN/PROPN = NOUN (The first part or the second part can be ignored if one of the noun is in the KG, e.g, Itosaisai no restaurant)
    it can be consider in the following case: 福 +の +浦 =>福の浦 (name of a place)
    R3) NOUN(-san) => NOUN
    R4) NOUN + ADP + NOUN (e.g., N DE N : something at xxx , N TO N : n and n ....)/// ADP consider only if the followed word is NOUN (not PART for eg と か)
    Do not consider if ADP == は and followed by Noun or PROPN (preceded by kore or kochira)
    

    R5) MINNA/HITORI/FUTARI/...nin/jin + ADP (DE) = > Do not consider
    
    R6) AUX+AUX+AUX => AUX (Do not consider TAI)
    xR7) NOUN/PROPN + ADP(DE/NI/DEHA (だは)) + VERB => NOUN/PROPN = Place where VERB happened
    xR8) NOUN/PROPN + ADP(DE/NI/DEHA) + VERB + NOUN  => Similar with NOUN + DE+ NOUN + ADP + VERB
    ??には
    xR20) NOUN(最初) ADP(に) NOUN ADP(に) VERB(IKU) (最初に : at first)
    xR21) Consider 'から' (kara place not time) 昼過ぎ:afternoon
    xR9) NOUN/PROPN + ADP(HE) + VERB => direction
    xR10)  NOUN/PROPN + ADP(GA)
    *R11) ADP + ADP = ADP (e.g., DEHA)
    *R12) .... PUNCT ... => consider next sentence if PUNCT!=POINT(.)
    xR13) NOUN/PROPN + ADP(HA) + VERB => characteristics
    R14) NOUN/PROPN + ADV + VERB => Do not consider ADV (e.g., mono takusan kau)
    R15) NOUN + VERB => NOUN + ADP + VERB
    R16) VERB + SCONJ (TE / けど) => consider the following sentences. TE indicades a list of actions. けど=but

    VERB + AUX :
        R17) IF AUX == SURU/RERU/NAI => consider AUX
        R17') IF AUX == TENSE OF VERB (e.g., TA, DA) => do not consider AUX

    R18) NOUN + する => ADJ (e.g., '贅沢三昧 + する)
    ADJ + AUX (TA) + NOUN => ADJ of a noun (e.g., 贅沢 だ 晩御飯)
    {'word': '明日', 'type': 'NOUN'}, {'word': 'は', 'type': 'ADP'} ==> ignore
    こちらは (PRON ADP) => ignore
    R24) ADJ + AUX (TA) => ignore AUX
    R19)IF a sentence does not have neither VERB nor ADJ (but contains many nouns)=> ignore
    R22) 友達 + と : tomodachi to 
    R23) 芥屋から二見方面で帰る (Return from Shimakeya in the direction of Futami)
    R25) V/ADJ + のが好き : like doing something (の:SCONJ, が:ADP, 好き:ADJ, です:AUX(to ignore)) :海釣りはみんなで楽しいのが好きです --- みんな:NOUN /// 海釣りはみんなで楽しいのが好きです///海釣りはみんなで楽しいのが好きです
    R26) ん SCONJ です  AUX : Do not consider both (ん at the end of VERB-AUX(ta))
    R27)沸き出る(VERB) て(SCONJ) いる(VERB) => is boiling
    R28) Consider  ADV VERB (eg のんびり リフレッシュする)
    """
    print(_text)
    text = removeEmoji(_text)
    text = removePythonEmoji(text)
    text = removeUserMention(text)

    sentences_token=[]
    if ("I am at " in text) or ("I'm at " in text) or ("I was at " in text):
        print(text)
        token_array = []
        #e.g., I am at Itosaisai in Itoshima, Fukuoka
        text_tab=text.split("at")
        if "in" in text_tab[1]:
            poi=text_tab[1].split(" in ")[0].strip()
            if "http" in poi:
                poi = poi.split("http")[0].strip()
            if "http" in text_tab[1]:
                text_tab[1] = text_tab[1].split("http")[0]
            cities=text_tab[1].split("in")[1].strip().split(",")
            token_poi={'word':poi,'type':'FoursquarePOI'}
            token_array.append(token_poi)
            for city in cities:
                token_array.append({'word':city.strip(),'type':'LOCATION'})
            sentences_token.append(token_array)
        else:
            poi=text_tab[1].strip()
            if "http" in poi:
                poi = poi.split("http")[0].strip()
            token_poi={'word':poi,'type':'FoursquarePOI'}
            token_array.append(token_poi)
            sentences_token.append(token_array)
        text=""
    
    #print(text)
    doc = nlp(text)
    
    for sentence in doc.sents: # This is some magic that I don't understand at all. How is she getting sentences from here!?
        #print("sentence **")
        token_array_tmp=[]
        
        #for token in sentence:
            #print(token.i, token.orth_, token.lemma_, token.pos_)
        
        for token in sentence:
            token_obj={'word':token.lemma_,'type':token.pos_}
            token_array_tmp.append(token_obj)
        #Detect sentence form
        token_array = []
        tag=False
        for token in token_array_tmp:
            #pretreatment:
            token['word'] = token['word'].replace("さん","")#R3)
            token['word'] = token['word'].replace("\\","")
            token['word'] = token['word'].replace("'"," ")
            if token['type']=="PART" or token['type']=="INTJ" or token['type']=="X" or token['type']=="DET" or token['type']=="PRON" or token['word'].strip()=="": #R12
                continue
            if token['type']=="SYM" and token['word']!="#":
                continue
            
            if len(token_array)==0:
                token_array.append(token)
                continue
            last_token=token_array[len(token_array)-1]
            
            if (last_token['type']=="PROPN" or last_token['type']=="NOUN") and (token['type']=="PROPN" or token['type']=="NOUN") :#R1)
                #last_token['word'] += " "+token['word']
                last_token['word'] += token['word']
                continue
            if (last_token['type']=="ADP" and token['type']=="ADP") :#R11)
                last_token['word'] += token['word']
                continue
            if (last_token['type']=="ADV" and token['type']=="ADV") :
                last_token['word'] += token['word']
                continue
            if (last_token['type']=="VERB" and token['type']=="AUX" and (token['word']=="する" or token['word']=="レリ" or token['word']=="たい" or token['word']=="ない")) :#R17)
                last_token['word'] += token['word']
                continue
            if last_token['type']=="VERB" and token['type']=="AUX":#R17')
                continue
            if (last_token['type']=="AUX" and token['type']=="AUX") :#R6)
                last_token['word'] += token['word'] 
                continue

            
            token_array.append(token)
        print(token_array)
        if (token_array!=[]):
            sentences_token.append(token_array)
        print("===============")

    return sentences_token
    #******************************************  
#==============================================================================
def writeInCSV(_csv_content):
    # open the file in the write mode
    """
    f = open(current_dir+"/"+nounVerbCSV, "a")
    f.write(_csv_content)
    f.close()
    return None
    """
    try:
        f = open(current_dir+"/"+nounVerbCSV, "a")
        f.write(_csv_content)
        f.close()
    except FileNotFoundError:
        print('Error on writing CSV file')
#==============================================================================

#UPDATE
def defineNounCooccurency0():
    co_occurence=[]
    for uplet in nouns_tweet_list:
        #remove redudance
        print(uplet)
        while 'の' in uplet: 
            uplet.remove('の')   
        while ' ' in uplet: 
            uplet.remove(' ')   
        while '' in uplet: 
            uplet.remove('')   
        while '\n\n' in uplet: 
            uplet.remove(' ') 
       
        uplet = list(dict.fromkeys(uplet))
        print(uplet)
        print("-----------")
        if len(uplet)>=MAX_NOUN_WSIZE:
            for index in range(len(uplet)):
                for index_j in range(index+1,len(uplet)):
                    index_couple = isElementInList(uplet[index], uplet[index_j], co_occurence)
                    if index_couple == -1:
                        co_occurence_item = {'noun_a':uplet[index], 'noun_b':uplet[index_j],'frequency':1}
                        co_occurence.append(co_occurence_item)
                    else:
                        co_occurence[index_couple]['frequency'] = co_occurence[index_couple]['frequency']+1
    writeJSONInFile(co_occurence, nounCooccurence_file)
#==============================================================================
def isElementInList(_elem_a, _elem_b, _list):
    for index in range(len(_list)):
        if (_list[index]['noun_a']==_elem_a and _list[index]['noun_b']==_elem_b) or (_list[index]['noun_b']==_elem_a and _list[index]['noun_a']==_elem_b):
            return index
    return -1
#==============================================================================
def loadDataInFolder():
    input_data = []
    files = os.listdir(current_dir+"/"+input_folder)
    for filename in files:
        print(filename)
        with open(os.path.join(current_dir+"/"+input_folder, filename), 'r') as f_collection:
            collection = json.load(f_collection)
            input_data = input_data+collection['data']
    return input_data
#==============================================================================
def writeJSONInFile(_json_dico, _file):
    try:
        dicoJSONFile = open(current_dir+"/"+_file, "w")
        dicoJSONFile.write(json.dumps(_json_dico))
        dicoJSONFile.close()
    except FileNotFoundError:
        print('Error on writing JSON file')

#==============================================================================
def loadNouns():
    nouns = []
    try :
        with open(current_dir+"/"+nounVerbCSV, "r") as f:
            for row in f:
                row_tab=row.split(',')
                noun = row_tab[0].strip()
                nouns.append(noun)
        nouns = list(dict.fromkeys(nouns))
        return nouns
    except FileNotFoundError:
        print('Noun-verb CSV file is not present')
        return None
#==============================================================================
def defineNounCooccurency(_nouns, _tweets):
    cooccurence=[]
    if len(_nouns)>=MAX_NOUN_WSIZE:
        for index in range(len(_nouns)):
            for index_j in range(index+1,len(_nouns)):
                #is in same tweet?
                noun_a = _nouns[index]
                noun_b = _nouns[index_j]
                count = isInSameTweet(noun_a,noun_b, _tweets)
                #print(count)
                if count >=MAX_NOUN_WSIZE:
                    if len(cooccurence)==0:
                        co_occurence_item = {'noun_a':noun_a, 'noun_b':noun_b,'frequency':count}
                        cooccurence.append(co_occurence_item)

                    else:
                        index_couple = isElementInList(noun_a, noun_b, cooccurence)
                        if index_couple == -1:
                            co_occurence_item = {'noun_a':noun_a, 'noun_b':noun_b,'frequency':count}
                            cooccurence.append(co_occurence_item)
                        else:
                            cooccurence[index_couple]['frequency'] = cooccurence[index_couple]['frequency']+count
    
    #print("coo :"+str(len(cooccurence)))
    writeJSONInFile(cooccurence, nounCooccurence_file)
#==============================================================================
def isInSameTweet(_noun_a, _noun_b, _tweets):
    count =0
    for tweet in _tweets:
        if _noun_a in tweet['text'] and _noun_b in tweet['text']:
            count += 1
    return count
#==============================================================================
def callModule(_input_data):
    data_res = parseListObjectInfo(_input_data)
    print(data_res)
#************************ MAIN *****************************

#========== Load tweets from Collection JSON File =============================
#def main():
def analyse_tweet(input_data):
    #verb, noun, particle
    """
    try :
        with open(current_dir+"/"+collectionWithODFile, "r") as f_collection:
            collection = json.load(f_collection)
            #print('I am here')
            objects_list = collection['data']
            data_res = parseListObjectInfo(objects_list)
            #writeInCSV(data_res)
    except FileNotFoundError:
        print('Tweet_OD collection  file is not present')
    """

    
    tweet_data = loadDataInFolderBilly(input_data)                                                             
    data_res = parseListObjectInfo(tweet_data)
    #writeInCSV(data_res)
    #defineNounCooccurency()
    
    """
    nouns_collection = loadNouns()
    print(len(nouns_collection))
    defineNounCooccurency(nouns_collection, input_data)
    """
    

#============================================================================== 
def analyzeCollection(_collection):
    analyzed_collection=[]
    index=0
    for tweet in _collection:
        print("tweet :"+str(index))
        if tweet['lang']=="ja" or ("I am at " in tweet['text']) or ("I'm at " in tweet['text']) or ("I was at " in tweet['text']):
            #print("collection : "+str(index))
            item={'id':tweet['id'], 'text':tweet['text'],'sentences':[],'posting-date':tweet['created_at']}
            item['sentences']=analyzeSyntax(item['text'])
            analyzed_collection.append(item)
            index +=1
    return analyzed_collection



