import os
from gcloud import storage, pubsub
#from moviepy.editor import *
from flask import Flask, request, render_template,json
import sys
import logging
import pprint
import shlex

import subprocess


PROJECT_ID = 'set-cloud-gaston'
TOPIC = 'projects/{}/topics/youtube_partners'.format(PROJECT_ID)
VIDEO_NAME = 'anim_card_flip.mp4'

def trim_blacks_reencoding_command(file_name, content_segments , video_duration):
    ffmpeg_command = ""
    trim_parameters = ""
    atrim_parameters = ""
    trim_streams = ""
    file_name_parts = file_name.split( '.' )
    replacement_files = ""
    segment_number = 0
    file_number =  0
    current_replacement_file_name = ""
    
    for time_stamp in content_segments:
        
        if time_stamp[0] >= 0:
            trim_streams += "[v" + str( segment_number ) + "][a" + str( segment_number ) + "]"
        else:
            file_number += 1
            current_replacement_file_name = time_stamp[1]
            trim_streams += "[" + str( file_number )  + ":v]"
            trim_streams += "[" + str( file_number )  +  ":a]"
            replacement_files = " -i " + current_replacement_file_name + " "
            
        if time_stamp[0] >= 0 :
            trim_parameters += "[0:v]trim=" + str( time_stamp[0] ) 
            atrim_parameters += "[0:a]atrim=" + str( time_stamp[0] ) 
            trim_parameters +=  ":" + str(  time_stamp[1]  )
            atrim_parameters += ":" + str(  time_stamp[1]  )
            trim_parameters += ",setpts=PTS-STARTPTS[v" + str(segment_number ) + "]; "
            atrim_parameters += ",asetpts=PTS-STARTPTS[a" + str(segment_number ) +  "]; "			
        segment_number+= 1
    #ffmpeg_command += os.path.join( os.path.dirname(os.path.abspath(__file__)) , "ffmpeg" )                
    ffmpeg_command +=  "./ffmpeg" 
    ffmpeg_command += " -i " + file_name +  " " + replacement_files  +  " "  +  " -strict -2 -y -filter_complex \""
    ffmpeg_command += trim_parameters + atrim_parameters  + trim_streams +  "  " 
    ffmpeg_command += "concat=n=" + str( len( content_segments )  ) + ":v=1:a=1[out] \""
    ffmpeg_command += " -map \"[out]\" "
    ffmpeg_command += file_name_parts[0] + "_nb_re." + file_name_parts[1] 
    return ffmpeg_command

def testRunAVConv():
    avconvCommand = "/usr/local/bin/runavconv.sh -filename youtube_demo.mp4 -segments '00:00:00-00:00:05|00:00:10-00:00:05|00:00:20-00:00:03'"
    print("about to call")
    print(avconvCommand)
    ret = os.system(avconvCommand)
    if ret:
        sys.stderr.write("FAILED")
        print('avconvCommand OS command failed')
        return "Failed"
    print('OS command finished successfully 1') 

def testLibAV():
    #2:31-23:40
    print('inside def testLibAV() line 89')
    client = storage.Client('set-cloud-gaston')
    bucket = client.bucket('set-cloud-gaston.appspot.com')
    blob = bucket.blob("MM41916160062.mp4")
    tempFile = "/tmp/MM41916160062.mp4"
    with open(tempFile, 'w') as f:
        print("about to download {}".format(tempFile))
        blob.download_to_file(f)
        print("{} downloaded".format(tempFile))
        
    # os.system('rm /tmp/output.webm')
    
    command = '/usr/bin/avconv -ss 151 -i ' + tempFile + ' -t 60 -vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y /tmp/output_1.ts'
    print('executing OS command 1')
    print(command)
    ret = os.system( command )
    if ret:
        sys.stderr.write("FAILED")
        print('OS command failed')
        return "Failed"
    print('OS command finished successfully 1') 
    command = '/usr/bin/avconv -ss 300 -i ' + tempFile + ' -t 60 -vcodec libx264 -acodec aac -bsf:v h264_mp4toannexb -f mpegts -strict experimental -y /tmp/output_2.ts'
    print('executing OS command 2')
    print(command)
    ret = os.system( command )
    if ret:
        sys.stderr.write("FAILED")
        print('OS command failed')
        return "Failed"
    print('OS command finished successfully 2')
    command = '/usr/bin/avconv -i concat:"/tmp/output_2.ts|/tmp/output_1.ts" -c copy -bsf:a aac_adtstoasc -y /tmp/full.mp4'
    print('about to execute final command for libav')
    print(command)
    ret = os.system( command )
    if ret:
        sys.stderr.write("FAILED")
        print('OS command failed')
        return "Failed"
    print('OS command finished successfully 3')
       
    blob = bucket.blob('nuevo.mp4')
    blob.upload_from_file(open('/tmp/full.mp4'))
    sys.stdout.write("SUCCESS")
    return "SUCCESS"
        


def testMoviePy():
    clips_array = []
    client = storage.Client('set-cloud-gaston')
    bucket = client.bucket('set-cloud-gaston.appspot.com')
    blob = bucket.blob("MM41916160062.mp4")
    tempFile = "/tmp/MM41916160062.mp4"
    
    print("testMoviePy - about to download {}".format(tempFile))
    
    with open(tempFile, 'w') as f:
        blob.download_to_file(f)
    print("testMoviePy - downloaded {}".format(tempFile))
        
    rgb = VideoFileClip(tempFile)
    collor_bars_1 = rgb.subclip(0,150)  
    content = rgb.subclip(150,1419)
    collor_bars_2 = rgb.subclip(1419,1517)
    print("testMoviePy - clip extraction done ")

    clips_array.append(content)
    print("testMoviePy - about to contatenate ")

    final = concatenate_videoclips(clips_array)
    print("testMoviePy - about to write video /tmp/MM41916160062_edited.mp4")

    final.write_videofile("/tmp/MM41916160062_edited.mp4")
    print("testMoviePy - /tmp/MM41916160062_edited.mp4 file created")
    
    blob = bucket.blob('MM41916160062_edited.mp4')
    print("testMoviePy - about to upload to GC video as MM41916160062_edited.mp4")
    blob.upload_from_file(open('/tmp/MM41916160062_edited.mp4'))
    print("testMoviePy - done succesfully")
    

def transcode(messageAsString):
    #testMoviePy()
    print('inside def transcode(messageAsString) line 10')
    client = storage.Client('set-cloud-gaston')
    bucket = client.bucket('set-cloud-gaston.appspot.com')
    blob = bucket.blob(messageAsString)
    tempFile = "/tmp/" + messageAsString
    with open(tempFile, 'w') as f:
        print("about to download {}".format(tempFile))
        blob.download_to_file(f)
        print("{} downloaded".format(tempFile))
        
    # os.system('rm /tmp/output.webm')
    
    command = '/usr/bin/avconv -i ' + tempFile + ' -c:v libvpx -crf 10 -b:v 1M -c:a libvorbis /tmp/output.webm'
    print('executing OS command')
    print(command)
    ret = os.system( command )
    if ret:
        sys.stderr.write("FAILED")
        print('OS command failed')
        return "Failed"
    print('OS command finished successfully')    
    blob = bucket.blob('youtube_demo.webm')
    blob.upload_from_file(open('/tmp/output.webm'))
    sys.stdout.write("SUCCESS")
    return "SUCCESS"
    
    
    

def main_func():
#if __name__ == '__main__':
    
    
    #Logging configurarion
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    segments = [[ 10 , 25 ],[ 30 , 40 ],[ 50 , 55 ]]#,[ 65 , 75 ],[ 80 , 90 ] ]

    ffmpeg_command = trim_blacks_reencoding_command(  "audio_video.mp4", segments , "200"  )
    print("ffmpeg command is{}".format(ffmpeg_command))

    #ffmpeg_command = './ffmpeg -i _   -strict -2 -y -filter_complex "[0:v]trim=10:25,setpts=PTS-STARTPTS[v0]; [0:v]trim=30:32,setpts=PTS-STARTPTS[v1]; [0:v]trim=33:35,setpts=PTS-STARTPTS[v2]; [0:v]trim=37:39,setpts=PTS-STARTPTS[v3]; [0:v]trim=42:45,setpts=PTS-STARTPTS[v4]; [0:v]trim=47:49,setpts=PTS-STARTPTS[v5]; [0:v]trim=50:55,setpts=PTS-STARTPTS[v6]; [0:v]trim=65:75,setpts=PTS-STARTPTS[v7]; [0:v]trim=80:90,setpts=PTS-STARTPTS[v8];  [v0][v1][v2][v3][v4][v5][v6][v7][v8] concat=n=9:v=1[out] " -map "[out]" test_video_nb_re.mp4'

    #ffmpeg_command = './ffmpeg -framerate 1/5 -i final_%d.png -c:v libx264 -r 30 -pix_fmt yuv420p new_merged_test.mp4'
    subprocess.check_call(ffmpeg_command, shell=True)
    print("calling ffmpeg with: {}".format(ffmpeg_command))
    
    subprocess.call(ffmpeg_command, shell=True) 
    print("ffmpeg call finished is{}".format(ffmpeg_command))
    
    #
    
    
    pubsub_client = pubsub.Client(PROJECT_ID)
    topic = pubsub_client.topic("youtube_partners")
    subscription = topic.subscription("set_videos")
    sys.stderr.write("Polling the topic")
    while True:
        results = subscription.pull(
            return_immediately=False, max_messages=1)
        if results:
            print("Received {} messages.".format(len(results)))
            for ack_id, message in results:
                print("worker.main message received in loop is {}: {}, {}".format(message.message_id, message.data, message.attributes))
                subscription.acknowledge([ack_id for ack_id, message in results])
                print("Aknowledged {}: ".format(message.message_id))
                messageAsString = message.data.decode('utf-8')
                print("worker.main calling transcode with parameter:")
                print(messageAsString)
                #transcode(messageAsString)

if __name__ == '__main__':
    testRunAVConv()
    #testLibAV()

    #Logging configurarion
    logging.basicConfig(level=logging.DEBUG,format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",datefmt="%Y-%m-%d %H:%M:%S")

    # Init Pretty Printer, just in case




    # 00:00:00-00:00:10|00:00:25-00:00:30|00:00:40-00:00:50|00:00:55-00:01:05|00:01:15-00:01:20|00:01:30-00:01:40

    segments = [[ 10 , 25 ],[ 30 , 40 ],[ 50 , 55 ]]#,[ 65 , 75 ],[ 80 , 90 ] ]


    #print trim_blacks_reencoding_command(  "test_video.mp4", segments , "100"  )
    ffmpeg_command = trim_blacks_reencoding_command(  "audio_video.mp4", segments , "200"  )
    print ffmpeg_command
    #print 'end'

    #ffmpeg_command = './ffmpeg -i _   -strict -2 -y -filter_complex "[0:v]trim=10:25,setpts=PTS-STARTPTS[v0]; [0:v]trim=30:32,setpts=PTS-STARTPTS[v1]; [0:v]trim=33:35,setpts=PTS-STARTPTS[v2]; [0:v]trim=37:39,setpts=PTS-STARTPTS[v3]; [0:v]trim=42:45,setpts=PTS-STARTPTS[v4]; [0:v]trim=47:49,setpts=PTS-STARTPTS[v5]; [0:v]trim=50:55,setpts=PTS-STARTPTS[v6]; [0:v]trim=65:75,setpts=PTS-STARTPTS[v7]; [0:v]trim=80:90,setpts=PTS-STARTPTS[v8];  [v0][v1][v2][v3][v4][v5][v6][v7][v8] concat=n=9:v=1[out] " -map "[out]" test_video_nb_re.mp4'

    #ffmpeg_command = './ffmpeg -framerate 1/5 -i final_%d.png -c:v libx264 -r 30 -pix_fmt yuv420p new_merged_test.mp4'
    
    #uncomment to run ffmpeg
    #subprocess.check_call(ffmpeg_command, shell=True)
    #subprocess.call(ffmpeg_command, shell=True)

#
