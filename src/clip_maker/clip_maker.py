from configparser import ConfigParser
import os
import sys
import datetime
import matplotlib.pyplot as pyplot
import matplotlib.dates as mdates

from moviepy.editor import *

try:
    from lib import db_connect
except Exception as e:
    print('error importing mongodb, Did you add lib to path?')
    print("adding lib to path for this instance only...")
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
    from lib import db_connect




output_file_location = './TwitchHighlightsOutput/' + datetime.datetime.now().strftime("%Y.%d.%m") + '/'



class ClipMaker:
    """
    Given a streamers name that has a coresponding video mkv file in the output file directory,
    makes clips out of that file based on highlights provided by chatters.
    This requires connection to the mongodb database.
    """

    def __init__(self,streamer):
        self.streamer = streamer
        self.streamer_clips_output_file_location = output_file_location + streamer + '/clips/'

        if not os.path.exists(self.streamer_clips_output_file_location):
            print('making dir ' + self.streamer_clips_output_file_location)
            os.makedirs(self.streamer_clips_output_file_location)
    
        print('clip maker for ' + streamer +' instantiated.')

    def __do_analysis(self):
        """
        private method that handles the analysis on a video file to determine what clips should be made 
        """
        #Step 1: connect to mongodb and pick a streamer
        dbclient = db_connect.DBClient()
        streamer_data = dbclient.analyze_number_of_stream_viewers(self.streamer)
        streamer_messeges_data = dbclient.analyzeStream(self.streamer)

        timearr = []
        messagesarr = []
        streamer_timearr = []
        num_chattersarr = []

        #create time and messages array for plotting purposes
        for entry in streamer_messeges_data:
            timearr.append(entry['start_time'])
            messagesarr.append(entry['messeges_count'] * entry['messeges_count'])
            #print(entry['start_time'])

        #create time and chatters array for plotting purposes
        for entry in streamer_data:
            streamer_timearr.append(entry['deltatime_from_start_of_clip'])
            num_chattersarr.append(entry['num_viewers'])

        # print('start time: ' + str(timearr[0]))
        # print('end time: ' + str(timearr[-1]))
        # print('duration: ' + str(timearr[-1] - timearr[0]))
        # print('average views/min = ' + str(sum(messagesarr) / len(messagesarr)))

        average_message_count = sum(messagesarr) / len(messagesarr)

        averagearr = []
        plotting_time_arr = []
        labelarr = []

        for i in range(len(timearr)):
            averagearr.append(average_message_count*1.8)
            #print(str(timearr[i]) + ' converts to ' + str(datetime.datetime(2020, 1, 1, 0, 0) + timearr[i]))
            plotting_time_arr.append(datetime.datetime(2020, 1, 1, 0, 0) + timearr[i])
            labelarr.append(str(i))

        plotting_streamer_timearr = []
        for i in range(len(streamer_timearr)):
            plotting_streamer_timearr.append(datetime.datetime(2020, 1, 1, 0, 0) + streamer_timearr[i])

        #plot messages and cuttoff
        messeges_over_time_fig = pyplot.figure(1)
        messeges_over_time_fig.set_figheight(15)
        messeges_over_time_fig.set_figwidth(30)
        messeges_over_time_fig.suptitle(self.streamer + "'s video data")
        messeges_over_time_sub = messeges_over_time_fig.add_subplot(211)

        pyplot.plot(plotting_time_arr,messagesarr,label='messages/min')
        dots = pyplot.plot(plotting_time_arr,messagesarr,'bo',label='messages/min')

        #label dots
        count = 0
        last_entry_was_above_line = False
        for i in range(len(plotting_time_arr)):
            #print(str(count) +': comparing ' + str(messagesarr[i]) + ' with ' + str(averagearr[i]))
            if(messagesarr[i] > averagearr[i]):
                if(last_entry_was_above_line):
                    #Don't increment the count because this is part of the same clip
                    count = count
                else:
                    #new clip above the line, increment clip count
                    count = count + 1
                messeges_over_time_sub.annotate(count,xy=(plotting_time_arr[i],messagesarr[i]))
                last_entry_was_above_line = True
            else:
                last_entry_was_above_line = False
            #    messeges_over_time_sub.annotate('NA',xy=(plotting_time_arr[i],messagesarr[i]))

        #finish plotting
        pyplot.plot(plotting_time_arr, averagearr,'',label='average')
        pyplot.gcf().autofmt_xdate()
        pyplot.ylabel('Messeges*Messeges')
        pyplot.xlabel('Time')

        viewers_over_time_sub = messeges_over_time_fig.add_subplot(212)

        pyplot.plot(plotting_streamer_timearr,num_chattersarr,label='num chatters')
        pyplot.ylabel('Chatters')
        pyplot.xlabel('Time')

        pyplot.tight_layout()
        pyplot.savefig(output_file_location+self.streamer+'.png')
        print('saved chart to ' + output_file_location+self.streamer+'.png')
        # pyplot.show()
        return average_message_count, streamer_messeges_data

    def make_clips(self):
        """
        Starts clip making process.
        """

        average_messege_count, streamer_messeges_data = self.__do_analysis()

        clipworthy_clips = []

        #add clipworthy clips
        for entry in streamer_messeges_data:
            if((entry['messeges_count']*entry['messeges_count']) > (average_messege_count*1.8)):
                clipworthy_clips.append(entry)

        #combine clips that are next to one another in time
        clip_number = 0
        while(True):
            #print('clip_number = ' + str(clip_number) +' , length of cliparr = ' + str(len(clipworthy_clips)))
            if(clip_number >= (len(clipworthy_clips))-1):
                #at end of clips
                break

            if (clipworthy_clips[clip_number]['end_time']==clipworthy_clips[clip_number+1]['start_time']):
                #duplicate clip detected
                #print('dublicate clip detected for clip ' + str(clip_number))
                clipworthy_clips[clip_number]['end_time']=clipworthy_clips[clip_number+1]['end_time']
                #print('cliparr length before ridding: ' + str(len(clipworthy_clips)))
                clipworthy_clips.remove(clipworthy_clips[clip_number+1])
                #print('cliparr length after ridding: ' + str(len(clipworthy_clips)))
                #print('')
            else:
                clip_number = clip_number + 1


        print('clipworthy clips will now be made')
        clipSlicer = ClipSlicer(clipworthy_clips)
        clipSlicer.make_clips()

        print("clipworthy clips for streamer "+ self.streamer + " have been made")

    



class ClipSlicer:
    """
    makes clips out of video in outputdirectory given a list of clips to make that look like the following:

    clip_list = [{'start_time':datetime,'end_time':datetime,'messeges_count':int, 'source_clip':streamer}
    , {'start_time':datetime,'end_time':datetime,'messeges_count':int, 'source_clip':streamer}]

    source_clip is the name of the videofile that the clip_list will be derived from
    """
    
    def __init__(self,clip_list):
        """
        clip_list must be of form
        clip_list = [{'start_time':datetime,'end_time':datetime,'messeges_count':int, 'source_clip':streamer}
        , {'start_time':datetime,'end_time':datetime,'messeges_count':int, 'source_clip':streamer}]
        """
        self.requested_clips=clip_list

    def make_clips(self):
        """
        Start the clip making!
        """
        print('starting to make clips!')
        #TODO parallelize this with multiprocessing
        clip_number = 1
        
        for requested_clip in self.requested_clips:
            streamer_output_file_location = output_file_location + requested_clip['source_clip'] + '/'
            streamer_clips_output_file_location = streamer_output_file_location + 'clips/'

            print('opening file ' + streamer_output_file_location+requested_clip['source_clip']+'.mkv')
            entire_stream_clip = VideoFileClip(streamer_output_file_location+requested_clip['source_clip']+'.mkv')
            print('requested time: ' + str(requested_clip['start_time'].total_seconds()))
            print('requested end time: ' + str(requested_clip['end_time'].total_seconds()))
            print('clip duration:'+ str(entire_stream_clip.duration))
            clip = None
            if(requested_clip['end_time'].total_seconds()>entire_stream_clip.duration):
                #longer time than clip specified, use end of clip as end time
                clip = entire_stream_clip.subclip(requested_clip['start_time'].total_seconds(),entire_stream_clip.duration)
            else:
                clip = entire_stream_clip.subclip(requested_clip['start_time'].total_seconds(),requested_clip['end_time'].total_seconds())
            
            if not os.path.exists(streamer_clips_output_file_location):
                print('No directory found for given streamer, making new dir...')
                os.makedirs(streamer_clips_output_file_location)
            print("now rendering clip " + self.requested_clips[0]['source_clip']+str(clip_number)+'.mp4 out of ' + str(len(self.requested_clips)))
            clip.write_videofile(streamer_clips_output_file_location + str(clip_number)+'.mp4')
            clip_number = clip_number + 1            

if(__name__ == '__main__'):
    clipmaker = ClipMaker('nickmercs')
    clipmaker.make_clips()
    print('all clips finished')
        