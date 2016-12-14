
# The Google App Engine python runtime is Debian Jessie with Python installed
# and various os-level packages to allow installation of popular Python
# libraries. The source is on github at:
#   https://github.com/GoogleCloudPlatform/python-docker
FROM gcr.io/google_appengine/python

# enable the following to install FFMPEG
RUN echo deb http://ftp.debian.org/debian jessie-backports main >>/etc/apt/sources.list
RUN apt-get update && apt-get install -y aptitude
RUN aptitude -t jessie-backports install -y ffmpeg
#

# enable the following to install libav
#RUN apt-get -y update && apt-get install -y libav-tools 
#

# Create a virtualenv for dependencies. This isolates these packages from system-level packages.
RUN virtualenv /env

# Setting these environment variables are the same as running
# source /env/bin/activate.
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# Copy the application's requirements.txt and run pip to install all
# dependencies into the virtualenv.
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ADD runavconv_with_cat.sh /usr/local/bin/runavconv.sh
ADD runffmpeg_with_cat.sh /usr/local/bin/runffmpeg.sh


# # Add the application source code.
ADD . /app

#CMD python /app/workergaston.py
CMD honcho start -f /app/procfile worker monitor
