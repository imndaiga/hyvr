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
    # the following packages were installed to allow for beacon support 
    # https://learn.adafruit.com/pibeacon-ibeacon-with-a-raspberry-pi/setting-up-the-pi
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
armflag=$(uname -m | grep -o arm)
if [ ! -z "$armflag" ]; then
    # download, unzip, configure, build and install bluez5.11
    # if a dependancy error is output from the configure script
    # that typically means that a particular apt-get package install
    # failed.
    # https://learn.adafruit.com/pibeacon-ibeacon-with-a-raspberry-pi/setting-up-the-pi
    # Using checkinstall instead to ensure that the bluez package is registered with apt package manager
    dpkg -s bluez
    if [ $? != 0 ]; then
        echo "Will download, unzip, configure, build and install bluez5.11"
        if [ -f bluez ]; then
            rm -rf bluez
        fi
        mkdir bluez && \
        cd bluez && \
        wget www.kernel.org/pub/linux/bluetooth/bluez-5.11.tar.xz && \
        unxz bluez-5.11.tar.xz && \
        tar xvf bluez-5.11.tar && \
        cd bluez-5.11 && \
        ./configure --prefix=/usr           \
                    --mandir=/usr/share/man \
                    --sysconfdir=/etc       \
                    --localstatedir=/var && \
        make && \
        # make install
        # fstrans switch fixes checkinstalls mkdir bug
        # (https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=717778)
        checkinstall --fstrans=no
    else
        bluezversion=$(dpkg -s bluez | grep -i version)
        echo "bluez package already installed: version $bluezversion"
    fi

    cd /webot
fi
x86flag=$(uname -m | grep -o x86)
if [ ! -z "$x86flag" ]; then
    sudo apt-get install bluez
fi

echo "Running firmware manager"
./firmwareman.sh
echo "Priming one HCI device on host"
./app/hostcon.sh -P