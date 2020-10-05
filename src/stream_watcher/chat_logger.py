from configparser import ConfigParser
import socket
import datetime
import re
import requests
import time
from threading import Thread 
import sys
import os

#from db_connect import db_connect
try:
    from lib import db_connect
    from lib import twitch_api
except Exception as e:
    print("error importing mongodb, Did you add lib to path?")
    print("adding lib to path for this instance only...")
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from lib import db_connect
    from lib import twitch_api


#Connect to twitch server via IRC
server = 'irc.chat.twitch.tv'
port = 6667
nickname = 'chatalytics'
default_channel = 'ninja'

token = os.environ.get("TWITCH_OAUTH")
if (token == None):
    print("error reading twitch oath token or client id, do you have env variables set?")
    sys.exit()

class ChatLogger:
    """
    This class logs a twitch streamers chat to a database using threads.
    """

    def __init__(self, channel):
        self.chat_thread = Thread(target=self.monitor_chat, args=((channel,)))
        self.chat_thread.start()

        self.streamer_views_thread = Thread(target=self.monitor_viewers, args=(channel, 60))
        self.streamer_views_thread.start()

        #self.chat_thread.join()
        #self.streamer_views_thread.join()        

    def monitor_chat(self, channel):
        """
        Monitors a streamer channel and records all messages sent in their twitch chat
        """
        #Connect to db
        mydb = db_connect.DBClient()

        #Connect to server
        sock = socket.socket()
        
        print(''.join(["connecting to ",channel,"'s server..."]))
        sock.connect((server, port))
        sock.send(''.join(['PASS ',token,'\r\n']).encode('utf-8'))
        sock.send(''.join(['NICK ',nickname, '\r\n']).encode('utf-8'))
        sock.send(''.join(['JOIN #', channel,'\r\n']).encode('utf-8'))

        #readbuffer = sock.recv(1024).decode('utf-8')
        readbuffer = sock.recv(1024).decode('latin1')
        for line in str.split(readbuffer,"\n"):
            #print(line)
            if("End of /NAMES list" in line):
                pass

        print(''.join(["Successfully joined ",channel,"'s chat!"]))

        try:
            while True:
                resp = sock.recv(1024).decode('latin1')
                #print(resp)
                if resp.startswith('PING'):
                    # sock.send("PONG :tmi.twitch.tv\n".encode('utf-8'))
                    #print("sending pong :)")
                    sock.send("PONG\r\n".encode('utf-8'))
                elif len(resp) > 0:
                    # print(resp)
                    try:
                        Parts = resp.split(":", 2)
                        username = Parts[1].split("!",1)[0]
                        message = Parts[2]
                        timestamp = datetime.datetime.now().strftime("%b %d %H:%M:%S %Y")
                        #print(timestamp+":"+username + ":" + message)
                        #print(message)
                        mydb.inputMessage(username, message, datetime.datetime.now(), channel)
                    except IndexError:
                        pass
                    except OSError:
                        pass
        except Exception as e:
            print(channel + "'s chat has stopped being monitored")
            pass

    def monitor_viewers(self, channel, seconds=60):
        """
        Logs a channels viewers into the database every time seconds
        Function is blocking
        """
        #Connect to db
        mydb = db_connect.DBClient()

        try:
            while True:
                mydb.inputStream(channel, datetime.datetime.now(), twitch_api.get_streams_chatters(channel))
                time.sleep(seconds)
        except Exception as e:
            print('No longer monitoring viewers for ' + channel)
            pass

def main():
    chatlogger = ChatLogger(default_channel)


if __name__ == '__main__':
    #print(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','lib')))
    
    main()
