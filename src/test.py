from moviepy.editor import *

#open videofile and read length
duration_in_seconds = 0
with VideoFileClip('./TwitchHighlightsOutput/2020.22.09/bren/bren.mkv') as clip:
    duration_in_seconds = clip.duration
    print(duration_in_seconds)
