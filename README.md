## Prerequisites

This project runs on python 3.8 and uses mongodb as a database

## Getting Started

1. Clone the repository
	```
    git clone https://github.com/kjv13/TwitchHighlights.git
    ```

## install external dependencies:

1. install ffmpeg: https://ffmpeg.org/download.html  
    Here is a youtube tutorial: https://www.youtube.com/watch?v=a_KqycyErd8  

1. add youtube-dl.exe to res folder.  
    Here is a youtube tutorial describing how to download and use it:
    https://www.youtube.com/watch?v=i6gKyfViie4



## set up the configs

1. Add ENV variables for mongodb (coming soon) 
	* Steps coming soon
	

1. set up twitch api:
    * ENV variables `TWITCH_OAUTH` `TWITCH_CLIENT_ID`
    * to get client id go to [this site](https://dev.twitch.tv/console) and 'register your application'
    * to get twitch oauth token make sure you are logged into twitch and go to [this site](https://twitchapps.com/tmi/) to get the oauth token
    * when done the TWICH_OAUTH token in env variable should look like  
	`oauth: oauth:abcdefghijklmnopqrstuvwxyz1234567890`

1. set vod download location
    * set res/downloadsettings.cfg to match where you want vods to be downloaded


## set up pypi dependencies
1. Set up python virtualenv (optional)
	```
    python3 -m venv ./venv
	git bash command: 
    . ./venv/Scripts/activate
    linux command:
    source venv/bin/activate
    ```

1. install the required pip libraries
	```
    pip install -r requirements.txt
    ```

## initialize the database
Set up the mongodb database by running 
note: if database has already been created this command will also erase and reset the db
    '''
    python src/lib/db_connect.py -y
    '''

## how to use
use:
to start downloading vods from the top 5 streamers (and monitor their chat) when
their streams have finished downloading clips will automatically be made :
    '''
    python src/main.py
    '''
# aron
