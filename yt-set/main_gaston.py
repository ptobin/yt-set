# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask, request, render_template,json
import os
import string
import random
import logging
from gcloud import storage, pubsub

PROJECT_ID = 'set-cloud-gaston'
TOPIC = 'youtube_partners'
DEFAULT_VIDEO = 'anim_card_flip.mp4'

app = Flask(__name__)
app.config['SECRET_KEY']='test'
app.debug = True

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/signUp')
def signUp():
    return render_template('signUp.html')

@app.route('/signUpUser', methods=['POST'])
def signUpUser():
    print("main.signUpUser")
    logging.debug("this one goes to the log - main.signUpUser")
    contentJSON = request.json
    print("main.signUpUser request.json")
    print(contentJSON)
    content = json.dumps(contentJSON)
    print("main.signUpUser json.dumps(contentJSON)")
    print(content)
    #content.encode("utf-8")
    print("main.signUpUser exclusions")
    print(contentJSON['exclusions'])
    
    pubsub_client = pubsub.Client(PROJECT_ID)
    topic = pubsub_client.topic(TOPIC)
    message_id = topic.publish(content.encode("utf-8"))
    print("main.signUpUser published message{}".format(message_id))
    print(content)
    
    return json.dumps({
        'received_exclusions':contentJSON['exclusions'],
        'received_python_segments':contentJSON['segmentForFFMPEG'],
        'received_file':contentJSON['fileName'],
        'message_id':message_id
    });


@app.route('/transcode')
def transcode():
    message_string = request.args.get('video', None)
    if message_string:
        print("main.transcode video received in URL is :{}".format(message_string))
        message_string = message_string + ".mp4"
        message_var = message_string.encode("utf-8")
    else:
        message_var = DEFAULT_VIDEO.encode("utf-8")
    
    pubsub_client = pubsub.Client(PROJECT_ID)
    topic = pubsub_client.topic(TOPIC)
    print("main.transcode about to publish message '{}' to youtube_partners: ".format(message_var))
    
    message_id = topic.publish(message_var)
    print("main.transcode Message {} published to youtube_partners.".format(message_id))
    return message_var


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
