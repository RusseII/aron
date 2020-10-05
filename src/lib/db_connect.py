from configparser import ConfigParser
import pymongo
from pymongo import MongoClient
import datetime
import os
import sys
import math
from moviepy.editor import *

class DBClient:
    """
    Class handles all connections to and from the mongodb database.
    """

    current_dir = os.path.dirname(__file__)
    db_config_rel_path = '../../res/db.cfg'
    db_config_abs_path = os.path.join(current_dir, db_config_rel_path)

    dl_config_rel_path = '../../res/downloadsettings.cfg'
    dl_config_abs_path = os.path.join(current_dir, dl_config_rel_path)

    def __init__(self):
        """
        Initializes the connection to the mongodb database
        """
        db_config = ConfigParser()
        db_config.read(self.db_config_abs_path)
        try:
            self.db_name = db_config['mongoDB Details']['db_name']
            self.hostname = db_config['mongoDB Details']['hostname']
        except Exception as e:
            print('there was a problem accessing the db.cfg file and reading')
            print(str(e))
            sys.exit()

        dl_config = ConfigParser()
        dl_config.read(self.dl_config_abs_path)        
        try:
            self.output_file_location = dl_config['Download Settings']['output_file_location'] + datetime.datetime.now().strftime("%Y.%d.%m") + '/'
            self.hostname = db_config['mongoDB Details']['hostname']
        except Exception as e:
            print('there was a problem accessing the downloadsettings.cfg file and reading')
            print(str(e))
            sys.exit()
                
        self.mongo_client = MongoClient(self.hostname)

        self.db = self.mongo_client[self.db_name]
        self.messagesCollection = self.db["messages"]
        self.streamsCollection = self.db["streams"]
    
    def inputMessage(self, username, contents, thedatetime, streamer):
        """
        Inputs a message into the database
        username and streamer are strings without spaces
        contents is a string
        thedatetime is a datetime 
        """

        messageDocument = {"username":username, "contents":contents, "datetime" : str(thedatetime), "streamer": streamer}
        x = self.messagesCollection.insert_one(messageDocument)

    def inputStream(self, streamer, thedatetime, numviewers):
        """
        Inputs a stream into the database
        streamer is a string without spaces
        numviewers is an int
        thedatetime is a datetime
        e.g. ("captainSparklez", datetime.datetime.now(), 500)
        """
        streamsDocument = {"streamer":streamer,"datetime":str(thedatetime),"numviewers": str(numviewers)}

        y = self.streamsCollection.insert_one(streamsDocument)

    def recreate_db(self):
        """
        drops the database and recreates it from scratch
        WARNING: all data will be lost
        """

        self.mongo_client.drop_database(self.db_name)
        db = self.mongo_client[self.db_name]
        messagesCollection = db["messages"]
        streamsCollection = db["streams"]

        messageDocument = {"username":"testUser", "contents":"I am posting a new message", "datetime" : str(datetime.datetime.now()), "streamer": "teststreamer"}
        streamsDocument = {"streamer":"teststreamer","datetime":str(datetime.datetime.now()),"numviewers":"9002"}

        x = messagesCollection.insert_one(messageDocument)
        y = streamsCollection.insert_one(streamsDocument)

        #print(x.inserted_id)
        #print(y.inserted_id)
        print("Database Recreated")

    def analyze_number_of_stream_viewers(self, streamer):
        """
        This function returns a streamers viewers over time
        """
        streamer_output_file_location = self.output_file_location + streamer + '/'
        #open file and read start time.
        with open(''.join([streamer_output_file_location,streamer,'.txt']),'r') as f:
            data = f.read()
            streamer = data.split(' ',1)[0]
            onlydata = data.split(' ',1)[1]
            print(onlydata)
            clip_start_time = datetime.datetime.strptime(onlydata,'%Y-%m-%d %H:%M:%S.%f')
            print("Video clip start time: " + str(clip_start_time))
            #print(datetime_onlydata + datetime.timedelta(days=1))
        
        #open videofile and read length
        duration_in_seconds = 0
        with VideoFileClip(''.join([streamer_output_file_location,streamer,'.mkv'])) as clip:
           duration_in_seconds = clip.duration

        clip_duration = datetime.timedelta(seconds=duration_in_seconds)

        clip_end_time = clip_start_time + clip_duration

        results = self.streamsCollection.find({"streamer":streamer, "datetime":{'$gte':str(clip_start_time),'$lt':str(clip_end_time)}})

        total_data = []
        for result in results:
            clips_real_time = datetime.datetime.strptime(result['datetime'], '%Y-%m-%d %H:%M:%S.%f')
            output_time = clips_real_time - clip_start_time
            total_data.append({'deltatime_from_start_of_clip':output_time, 'num_viewers':result['numviewers'] ,'source_clip':streamer})

        return total_data
        

    def analyzeStream(self, streamer):
        """
        This function returns a streamers messege information during the duration of a videoclip
        """
        streamer_output_file_location = self.output_file_location + streamer + '/'

        #open file and read start time.
        with open(''.join([streamer_output_file_location,streamer,'.txt']),'r') as f:
            data = f.read()
            streamer = data.split(' ',1)[0]
            onlydata = data.split(' ',1)[1]
            print(onlydata)
            clip_start_time = datetime.datetime.strptime(onlydata,'%Y-%m-%d %H:%M:%S.%f')
            print("Video clip start time: " + str(clip_start_time))
            #print(datetime_onlydata + datetime.timedelta(days=1))

        #open videofile and read length
        duration_in_seconds = 0
        with VideoFileClip(''.join([streamer_output_file_location,streamer,'.mkv'])) as clip:
           duration_in_seconds = clip.duration

        minutes = math.ceil(duration_in_seconds/60)

        #get average messages/min
        ##repeated searches through mongo db using rotating minutemark

        #make array of datetimes
        
        total_data = []

        start_time = clip_start_time - datetime.timedelta(minutes=1)
        for x in range(minutes):
            #increment start time
            start_time = start_time + datetime.timedelta(minutes=1)
            end_time = start_time + datetime.timedelta(minutes=1)
            results = self.messagesCollection.find({"streamer":streamer, "datetime":{'$gte':str(start_time),'$lt':str(end_time)}})
            # for result in results:
            #     print(result["datetime"])
            #total_data.append({'start_time':start_time,'end_time':end_time,'messeges_count':results.count()})        
            if(results.count() > 0):
                #print("messeges posted from " + str(start_time) +" to " + str(end_time))
                #print(results.count())
                output_start_time = start_time - clip_start_time
                output_end_time = end_time - clip_start_time
                print("Adding data for time: " + str(output_start_time) + ' to ' + str(output_end_time))

                total_data.append({'start_time':output_start_time,'end_time':output_end_time,'messeges_count':results.count(), 'source_clip':streamer})

        results = self.messagesCollection.find({"streamer":streamer})
        #results = self.messagesCollection.find({"streamer":streamer, "datetime":{'$gte':str(start),'$lt':str(end)}})

        print("total messages: " + str(results.count()))

        return total_data



if (__name__ == "__main__"):
    while True:
        value = input("Would you like to erase and recreate the database?[Y/N]")
        if (value == "Y"):
            dbclient = DBClient()
            dbclient.recreate_db()
            break
        elif (value == "N"):
            break
        print("Incorrect input provided.")

