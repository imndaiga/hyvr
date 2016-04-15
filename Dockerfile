################################################
# Dockerfile to build panyabot container images
# Based on raspbian
################################################
#Set the base image to raspbian
FROM resin/raspberrypi-systemd:jessie

# File Author / Maintainer
MAINTAINER Wachira Ndaiga

# Create environment variables
ENV INITSYSTEM on
ENV XDG_RUNTIME_DIR /run/user/%I

# Update the repository sources list and install dependancies
RUN sudo apt-get update \
  && apt-get install -y \
    python \
    python-dev \
    python-pip \
    usbutils \
    nano \
    arduino-mk \
    wget \
    ca-certificates \
    picocom \
    lsof \
    make \
    dbus \
    checkinstall \
    # the following packages were installed according to the following instructions by K-Town
    # https://learn.adafruit.com/pibeacon-ibeacon-with-a-raspberry-pi/setting-up-the-pi
    # python-dbus and python-gobject are additionally required to get the bluez test functions to work
    libusb-dev \
    libdbus-1-dev \
    libglib2.0-dev \
    libudev-dev \
    libical-dev \
    libreadline-dev \
    python-dbus \
    python-gobject \
    # the following dependancy is defined by http://www.elinux.org/RPi_Bluetooth_LE
    libdbus-glib-1-dev \
  && apt-get clean

# Set application directory
RUN mkdir /webot
WORKDIR /webot

# we install requirements first to benefit from docker layers caching
ADD ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# copy the entire source code
ADD . ./

# set permissions
RUN chmod 755 db_start.py tests.py run.py run.sh app/hostcon.sh firmwareman.sh

# Start the web app
CMD ["/bin/bash", "run.sh"]