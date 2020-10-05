from configparser import ConfigParser
from threading import Thread 
import subprocess
import datetime
import os
import sys

#default output file location
output_file_location = '../../output/'

current_dir = os.path.dirname(__file__)
config_rel_path = '../../res/downloadsettings.cfg'
config_abs_path = os.path.join(current_dir, config_rel_path)

config = ConfigParser()
config.read(config_abs_path)

try:
    output_file_location = config['Download Settings']['output_file_location'] + datetime.datetime.now().strftime("%Y.%d.%m") + '/'
except Exception as e:
    print('there was a problem accessing the downloadsettings.cfg file')
    print(str(e))
    print("assuming Default output file location")

if not os.path.exists(output_file_location):
                print('Making dir ' + output_file_location)
                os.makedirs(output_file_location)

class VideoDownloader:
    """
    This class automatically downloads a streamers livestream.
    """
    def __init__(self, channel):
        T = Thread(target=download_process, args=(''.join(['https://www.twitch.tv/',channel]),channel))
        T.start()
        T.join()

def download_process_time(URI,download_name,time):
    """
    download_process is a target function for threading that takes a URI, name of file, and amount of time the clip should be and downloads a particular clip
    This function IS blocking
    URI a url in the form of 'https://www.twitch.tv/shroud' and should lead to a twitch stream
    download_name can be any string without spaces
    time A string of the form '00:00:10.00' or HH:MM:SS.milisecondMilisecond
    """

    print(''.join(["Starting Download process for ", download_name]))
    path_to_res = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','res'))
    this_stream_output_file_location = output_file_location + download_name +'/'

    #command = ''.join(['../../res/youtube-dl.exe -f best -g ',URI])
    command = ''.join([path_to_res,'/youtube-dl.exe -f best -g ',URI])
    clipLink = subprocess.run(command, capture_output=True, text=True)
    if(clipLink.returncode):
        print("An error occured Getting video link")
        print(clipLink.stderr)
    else:
        print(''.join(["Clip found! Now downloading ",download_name,'!']))

    if not os.path.exists(this_stream_output_file_location):
                print('Making dir '+ this_stream_output_file_location)
                os.makedirs(this_stream_output_file_location)

    #log time of start of recording
    with open(''.join([this_stream_output_file_location,download_name,".txt"]), "w") as f:
        f.write(''.join([download_name,' ', str(datetime.datetime.now())]))

    if time is None:
        command2 = ''.join(['ffmpeg -i ',clipLink.stdout,' -y -c copy ',this_stream_output_file_location,download_name,'.mkv'])
    else:
        #https://unix.stackexchange.com/questions/230481/how-to-download-portion-of-video-with-youtube-dl-command
        command2 = ''.join(['ffmpeg -i ',clipLink.stdout,' -t ',time,' -y -c copy ',this_stream_output_file_location,download_name,'.mkv'])
    downloader = subprocess.run(command2, capture_output=True, text=True)

    if(downloader.returncode):
        print("as error occured when downloading the video")
        print(downloader.stderr) 
    else:
        #print(downloader.stdout)
        print(''.join(['Finished Downloading video ',download_name]))
        #Now cut the video into clips

def download_process(URI,download_name):
    """
    download_process is a target function for threading that takes a URI and name of file and downloads a particular clip
    This function IS blocking
    URI a url in the form of 'https://www.twitch.tv/shroud' and should lead to a twitch stream
    download_name can be any string without spaces
    """
    download_process_time(URI,download_name, None)

def main():
    videodownloader = VideoDownloader('reinforce')

if __name__ =='__main__':

    #print(output_file_location)
    main()