from configparser import ConfigParser
import requests
import os
import sys


token = os.environ.get("TWITCH_OAUTH")
client_id =  os.environ.get("TWITCH_CLIENT_ID")
if token == None or client_id == None:
    print("error reading twitch oath token or client id, do you have env variables set?")
    sys.exit()

def get_top_games():
    """
    Gets top twitch games https://dev.twitch.tv/docs/v5/reference/games
    """
    games = []

    payload = {'limit': 10, 
                'api_version': 5,
                'client_id': client_id}

    result = requests.get('https://api.twitch.tv/kraken/games/top',params=payload)
    for game in result.json()['top']:
        games.append(game['game']['name'])

    return games

def get_top_streamers_of_game(game, viewer_limit=200):
    """
    returns the top streamers for a particular game as long as they are over the viewer limit
    """
    topStreams =[]

    payload = {
                'game': game,
                'limit': '10',
                'stream_type': 'live',
                'language': 'en',
                'api_version': 5,
                'client_id' : client_id
            }


    result = requests.get('https://api.twitch.tv/kraken/streams/', params=payload)

    for stream in result.json()['streams']:
        #  if the stream has enough viewers to be monitored
        if stream['viewers'] >= viewer_limit:
            topStreams.append(stream['channel']['name'])

    return topStreams

def get_streams_chatters(channel):
    """
    Gets a twitch channels twitch viewers.
    """
    payload = {'api_version': 5,
            'client_id': client_id}

    result = requests.get(''.join(['https://tmi.twitch.tv/group/user/',channel,'/chatters']), params=payload)
    usercount = result.json()['chatter_count']
    return usercount

#TODO implement getIsLive() from following url
#'https://api.twitch.tv/kraken/streams/YOUR_CHANNEL_NAME'

if(__name__ == '__main__'):
    print('ninja viewers: '+str(get_streams_chatters('ninja')))