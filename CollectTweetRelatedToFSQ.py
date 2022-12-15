#Before running this script please check the parameter values of event_detection_config.ini in EventDectionProject and edit if necessary
import os
import sys
import json
import time


current_dir = os.path.dirname( __file__ )
onto_module_dir = os.path.join( current_dir, './')
sys.path.append(onto_module_dir)
import CollectTweets

FSQ_dataFolder="./FSQCollectedData/"

#=======================================
def loadCollection(_json_file):
    with open(current_dir+"/"+_json_file, "r") as f_collection:
       collection = json.load(f_collection)
       return collection
#===================================
def writeJSONInFile(_json, _output_file):
    json_file = open(current_dir+"/"+_output_file, "w")
    json_file.write(json.dumps(_json))
    json_file.close()
#=======================================
def collectTweetsRelatedToFSQPOI(_categories):
    nb=0
    for categ in _categories:
        #create new folder for output
        outputfolder = os.path.join(current_dir+"/FSQ_Collected_tweets/", str(categ))
        isExist = os.path.exists(outputfolder)
        if isExist==False:
            os.mkdir(outputfolder)
        
        fsq_file = loadCollection(FSQ_dataFolder+"FSQ_"+str(categ)+".json")
        data = fsq_file['results']
        for item in data:
            tweet_keyword = item['name'].lower().strip()
            keywords = tweet_keyword+" OR #"+tweet_keyword
            poiname=item['name'].replace(" ","_")
        
            start_dates=["2019-01-01","2019-04-01","2019-07-01","2019-10-01","2020-01-01","2020-04-01","2020-07-01","2020-10-01","2021-01-01","2021-04-01","2021-07-01","2021-10-01"]
            end_dates=["2019-03-31","2019-06-30","2019-09-30","2019-12-31","2020-03-31","2020-06-30","2020-09-30","2020-12-31","2021-03-31","2021-06-30","2021-09-30","2021-12-31"]
            
            for index in range(len(start_dates)):
                CollectTweets.main(keywords,start_dates[index],end_dates[index],str(categ)+"/CollectedTweets_"+poiname+"_"+str(index)+".json")
                print("Part :"+str(index))
                time.sleep(5)
            
            #CollectTweets.main(keywords,start_dates[0],end_dates[0],str(categ)+"/CollectedTweets_"+poiname+"_"+str(0)+".json")

        

        
#=======================================
#ID categories provided by Foursquare
categories = [13065,13003, 16027, 12108, 17003, 16032, 16021, 19009, 16003, 
17065, 19047, 16052]
#collectTweetsRelatedToFSQPOI([categories[1]])
#collectTweetsRelatedToFSQPOI([categories[2]])


