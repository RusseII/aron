from threading import Thread
import chat_logger
import video_downloader
import os

class StreamWatcher:
    """
    This class will watch a particular twitch stream. It does this by logging into the channels twitch chat via IRC
    and logging entries into a mongodb database. It additionally starts downloading the twitch stream as a VOD recording the
    stream recording start time. This syncs the twitch chat and the VOD. 
    """

    def __init__(self, streamName):
        """
        Takes twitch stream name as an argument and starts watching that chat.
        """

        chat_thread = Thread(target=chat_logger.ChatLogger, args=((streamName,)))
        chat_thread.start()
        #Open IRC chat to stream
        #chatlogger = chat_logger.ChatLogger(streamName)
        #Start downloading VOD
        vod_thread = Thread(target=video_downloader.VideoDownloader, args=((streamName,)))
        vod_thread.start()
        #vodLogger = video_downloader.VideoDownloader(streamName)

        vod_thread.join()
        
        
        #TODO Start polling 1 time each 30 seconds to see if the channel is still online
        #if channel is offline, stop IRC and VOD download

        #TODO Kill self if number of viewers goes below number

        #TODO Run DB analyser after finished
        

if (__name__ == "__main__"):
    print(os.getcwd())
    #streamwatcher = StreamWatcher('xqcow')