#!/usr/bin/env bash
# This should be run before unixrun as sudo
echo "Installing required packages"
apt-get update && apt-get install -y \
    python \
    python-dev \
    python-pip \
    usbutils \
    python-gobject \
    python-bluez \
    nano \
    picocom \
    arduino-mk \
    wget \
    ca-certificates \
    picocom \
    lsof \
    make \
    libusb-dev \
    libdbus-1-dev \
    libglib2.0-dev \
    libudev-dev \
    libical-dev \
    libreadline-dev \
  && apt-get clean

mkdir bluez && \
cd bluez && \
wget www.kernel.org/pub/linux/bluetooth/bluez-4.101.tar.xz && \
unxz bluez-4.101.tar.xz && \
tar xvf bluez-4.101.tar && \
cd bluez-4.101 && \
./configure && \
make && \
make install && \