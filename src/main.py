import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'stream_watcher')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'lib')))

import time
import requests
from threading import Thread
from lib import twitch_api
from stream_watcher import stream_watcher
from threading import Thread

from clip_maker import clip_maker

def main():
    #Find top 10 streamers
    num_streamers = 5


    #Get top games
    games = twitch_api.get_top_games()

    #TODO Parallelize this with threads
    #Get top streamers
    print('Getting Top Streamers...')
    all_top_streamers = []
    for game in games:
        all_top_streamers.extend(twitch_api.get_top_streamers_of_game(game))

    streamer_viewers_dict = {}

    print('Getting Top Streamers Viewcounts...')
    for top_stream in all_top_streamers:
        print(''.join(['Getting Viewcount for ',top_stream]))
        streamer_viewers_dict.update({top_stream: twitch_api.get_streams_chatters(top_stream)}) 

    sorted_top_streamers = sorted(streamer_viewers_dict, key=streamer_viewers_dict.get)[::-1]

    #print(sorted_top_streamers[0:num_streamers])

    print('Ordered Streamers by Viewcount, Starting Monitor on Top '+ str(num_streamers) +' Streams')
    recording_threads = []
    for top_streamer in sorted_top_streamers[0:num_streamers]:
        T = Thread(target=stream_watcher.StreamWatcher, args=((top_streamer,)))
        recording_threads.append(T)
        T.start()
    #give threads a chance to start going
    time.sleep(10)
    for thread in recording_threads:
        thread.join()

    time.sleep(2)
    #now make clips with downloaded vods    
    for top_streamer in sorted_top_streamers[0:num_streamers]:
        clipmaker = clip_maker.ClipMaker(top_streamer)
        clipmaker.make_clips()
        #TODO upload clip to youtube
        


if(__name__ == '__main__'):
    main()
