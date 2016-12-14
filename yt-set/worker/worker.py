import os
import subprocess
from gcloud import storage, pubsub
from flask import Flask, request, render_template,json
import sys
import logging
import pprint
import shlex
import json


PROJECT_ID = 'set-cloud-gaston'
TOPIC = 'projects/{}/topics/youtube_partners'.format(PROJECT_ID)
#VIDEO_NAME = 'anim_card_flip.mp4'

def trim_blacks_reencoding_command(file_name, content_segments):
    ffmpeg_command = ""
    trim_parameters = ""
    atrim_parameters = ""
    trim_streams = ""
    file_name_parts = file_name.split( '.' )
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
    ffmpeg_command +=  "/usr/bin/ffmpeg" 
    ffmpeg_command += " -i " + "/tmp/" + file_name + " -loglevel debug -strict -2 -y -filter_complex \""
    ffmpeg_command += trim_parameters + atrim_parameters  + trim_streams +  " " 
    ffmpeg_command += "concat=n=" + str( len( content_segments )  ) + ":v=1:a=1[out] \""
    ffmpeg_command += " -map \"[out]\" "
    ffmpeg_command += "/tmp/" + file_name_parts[0] + "_edited." + file_name_parts[1] 
    return ffmpeg_command

def useFFMPEGCat(message_id, fileName,  segmentForLibAB):
    print('inside testRunAVConv(messageAsString)')
    avconvCommand = "/usr/local/bin/runffmpeg.sh -filename " + fileName + " -segments " + "'" + segmentForLibAB + "'"
    print("about to call")
    print(avconvCommand)
    ret = os.system(avconvCommand)
    if ret:
        sys.stderr.write("FAILED")
        print('avconvCommand OS command failed')
        return "Failed"
    print('OS command finished successfully 1') 
    return "SUCCESS"


def useAVCONV(message_id, fileName,  segmentForLibAB):
    print('inside testRunAVConv(messageAsString)')
    avconvCommand = "/usr/local/bin/runavconv.sh -filename " + fileName + " -segments " + "'" + segmentForLibAB + "'"
    print("about to call")
    print(avconvCommand)
    ret = os.system(avconvCommand)
    if ret:
        sys.stderr.write("FAILED")
        print('avconvCommand OS command failed')
        return "Failed"
    print('OS command finished successfully 1') 
    return "SUCCESS"

def uploadFileFromGCS(message_id, fileName):
    client = storage.Client('set-cloud-gaston')
    bucket = client.bucket('set-cloud-gaston.appspot.com')
    fileNameParts = fileName.split(".")
    newFileName = fileNameParts[0] + "_edited." + fileNameParts[1]
    blob = bucket.blob(newFileName)
    tmpPath = '/tmp/' + newFileName
    blob.upload_from_file(open(tmpPath))
    sys.stdout.write("SUCCESS")

def downloadFileFromGCS(message_id, fileName):
    client = storage.Client('set-cloud-gaston')
    bucket = client.bucket('set-cloud-gaston.appspot.com')
    blob = bucket.blob(fileName)
    tempFile = "/tmp/" + fileName
    with open(tempFile, 'w') as f:
        print("about to download {}".format(tempFile))
        ret = blob.download_to_file(f)
        print("blob.download_to_file(f)")
        print(ret)
        print("{} downloaded".format(tempFile))

def transcode(message_id, fileName, encoder, pythonSegments, segmentForLibAB):
    print('inside worker.transcode()')
    print('pythonSegments:')
    print(pythonSegments)
    print('segmentForLibAB:')
    print(segmentForLibAB)
    downloadFileFromGCS(message_id, fileName)
    if encoder == 'ffmpeg':
        ret = useFFMPEG(message_id, fileName, pythonSegments)
    if encoder == 'libav':
        ret = useAVCONV(message_id, fileName,  segmentForLibAB)
    if encoder == 'ffmpeg_cat':   
        ret = useFFMPEGCat(message_id, fileName, segmentForLibAB)
         
    print("ret from ret = testRunAVConv(messageAsString)")
    print(ret)
    uploadFileFromGCS(message_id, fileName)
    return "SUCCESS"

def useFFMPEG(message_id, fileName, segmentsString):
    #segments = [[ 10 , 25 ],[ 30 , 40 ],[ 50 , 55 ]]#,[ 65 , 75 ],[ 80 , 90 ] ]
    parts  = segmentsString.split("=")
    segments = json.loads(parts[1])
    ffmpegCommand = trim_blacks_reencoding_command(fileName, segments)
   
    print("calling ffmpeg with: {} ".format(ffmpegCommand))
    #subprocess.call(ffmpeg_command, shell=True) 
    #print("ffmpeg call finished is{}".format(ffmpeg_command))
    ret = subprocess.call(ffmpegCommand, shell=True)
    if ret:
        sys.stderr.write("FAILED")
        print('useFFMPEG OS command failed')
        return "Failed"
    print('useFFMPEG OS command succedded') 
    return "SUCCESS"

if __name__ == '__main__':    
    pubsub_client = pubsub.Client(PROJECT_ID)
    topic = pubsub_client.topic("youtube_partners")
    subscription = topic.subscription("set_videos")
    print("worker.main Polling the topic...\n")
    while True:
        results = subscription.pull(return_immediately=True, max_messages=1)
        if results:
            print("worker.main received {} messages.".format(len(results)))
            for ack_id, message in results:
                print("worker.main message received in loop is {}: {}, {}".format(message.message_id, message.data, message.attributes))
                subscription.acknowledge([ack_id for ack_id, message in results])
                print("worker.main Aknowledged {}: ".format(message.message_id))
                print("worker.main message.data: \n")
                print(message.data)
                messageAsString = message.data.decode('utf-8')
                messageObject = json.loads(messageAsString)
                fileName = messageObject['fileName']
                encoder = messageObject['encoder']                
                segmentForFFMPEG = messageObject['segmentForFFMPEG']
                segmentForLibAB = messageObject['segmentForLibAB']
                print("     worker.main worker.main calling transcode for encoder {} ".format(encoder))
                print(messageAsString)
                ret = transcode(message.message_id, fileName, encoder, segmentForFFMPEG, segmentForLibAB)
                print("     worker.main worker.main transcode finished with code {} ".format(ret))
                

