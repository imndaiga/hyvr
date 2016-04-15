#!/usr/bin/env bash
# This should be run before unixrun as sudo
echo "Installing required packages"
apt-get update && apt-get install -y \
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

chmod 755 db_start.py
chmod 755 tests.py
chmod 755 run.py
chmod 755 run.sh
chmod 755 app/hostcon.sh
chmod 755 firmwareman.sh
chmod 755 unixrun.sh

echo "Checking bluez package"
# download, unzip, configure, build and install bluez5.32
# if a dependancy error is output from the configure script
# that typically means that a particular apt-get package install
# failed.
# Following a number of tutorials to install bluez to set up with bluepy:
# - https://learn.adafruit.com/pibeacon-ibeacon-with-a-raspberry-pi/setting-up-the-pi
# - http://www.elinux.org/RPi_Bluetooth_LE
# Using checkinstall instead to ensure that the bluez package is registered with apt package manager
# By default, bluez is set to not install i.e bluezinstallflag=0
bluezinstallflag=0
bluezversion=$(dpkg -s bluez | grep Version | cut -f2- -d' ')
if [ -z $bluezversion ]; then
    echo "Bluez not installed"
    bluezinstallflag=1
else
    echo "Bluez already installed"
    if [[ "$bluezversion" != *'5.32'* ]]; then
        echo "Purging bluez version $bluezversion"
        apt-get purge bluez && \
        bluezinstallflag=1
    else
        echo "Correct bluez version installed"
    fi
fi

if [ $bluezinstallflag -eq 1 ]; then
    echo "Will download, unzip, configure, build and install bluez version 5.32"
    if [ -f bluez ]; then
        rm -rf bluez
    fi
    mkdir bluez && \
    cd bluez && \
    wget www.kernel.org/pub/linux/bluetooth/bluez-5.32.tar.xz && \
    unxz bluez-5.32.tar.xz && \
    tar xvf bluez-5.32.tar && \
    cd bluez-5.32 && \
    ./configure --prefix=/usr           \
                --mandir=/usr/share/man \
                --sysconfdir=/etc       \
                --localstatedir=/var && \
    make && \
    # make install
    # fstrans switch fixes checkinstalls mkdir bug
    # (https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=717778)
    checkinstall --fstrans=no -y
    echo "Will now pull the bluepy pip package and install it"
    cd /webot
fi

echo "Running firmware manager"
./firmwareman.sh
echo "Priming one HCI device on host"
./app/hostcon.sh -P