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


## Env Variables

See `.env.sample` for needed env variables
	

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


## view DB data
To view the database data - download `Mongodb Atlas`

Use `'mongodb+srv://admin:' + os.environ.get('MONGODB_PASS') + '@c0.relki.mongodb.net')` as connection screen. Replace the os.environ.get with the actual mongodb pass


## how to use
use:
to start downloading vods from the top 5 streamers (and monitor their chat) when
their streams have finished downloading clips will automatically be made :
    '''
    python src/main.py
    '''
