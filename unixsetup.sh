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

chmod 755 db_start.py
chmod 755 tests.py
chmod 755 run.py
chmod 755 run.sh
chmod 755 app/hostcon.sh
chmod 755 firmwareman.sh
chmod 755 unixrun.sh

echo "Checking bluez package"
# download, unzip, configure, build and install bluez4.101
# if a dependancy error is output from the configure script
# that typically means that a particular apt-get package install
# failed.
dpkg -s bluez
if [ $? != 0 ]; then
    echo "Will download, unzip, configure, build and install bluez4.101"
    mkdir bluez && \
    cd bluez && \
    wget www.kernel.org/pub/linux/bluetooth/bluez-4.101.tar.xz && \
    unxz bluez-4.101.tar.xz && \
    tar xvf bluez-4.101.tar && \
    cd bluez-4.101 && \
    ./configure && \
    make && \
    make install
else
    bluezversion=$(dpkg -s bluez | grep -i version)
    echo "Bluez already installed: version $bluezversion"
fi

echo "Running firmware manager"
./firmwareman.sh
echo "Priming one HCI device on host"
./app/hostcon.sh -P