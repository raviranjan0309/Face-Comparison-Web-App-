FROM ubuntu:16.04
FROM python:3
 
# Update OS
RUN sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install libboost-all-dev --assume-yes
 
# Install Python
RUN apt-get install -y python3-pip
 
# Create app directory
ADD . /webapp
 
# Set the default directory for our environment
ENV HOME /webapp
WORKDIR /webapp

# Get python version
RUN which python

# Install uwsgi Python web server
RUN pip install uwsgi

# Install boost python package
RUN pip install boost

# Installcmake python package
RUN pip install cmake

# Installdlib python package
RUN pip install dlib

# Install app requirements
RUN pip install --upgrade -r requirements.txt
 

ENTRYPOINT ["python"]
CMD ["app.py"]