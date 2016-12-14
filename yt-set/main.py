
from flask import Flask, request, render_template,json

import os
import string
import random
import logging
from gcloud import storage, pubsub


#PROJECT_ID = 'yt-set'
#TOPIC = 'youtube-partners'

PROJECT_ID = 'set-cloud-gaston'
TOPIC = 'youtube_partners'

app = Flask(__name__)
app.config['SECRET_KEY']='test'
app.debug = True



# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/video/<name>')
def video(name):
  return render_template("video.html", name=name)

@app.route('/deliver')
def deliver():
  return render_template("deliver.html")

@app.route('/detect')
def detect():
  return render_template("detect.html")

@app.route('/intro')
def intro():
  return render_template("intro.html")

@app.route('/config')
def config():
  return render_template("config.html")

@app.route('/demo')
def demo():
  return render_template("main.html")


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return render_template("intro.html")
    
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404



@app.route('/signUp')
def signUp():
    return render_template('signUp.html')

@app.route('/signUpUser', methods=['POST'])
def signUpUser():
    print("main.signUpUser")
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
