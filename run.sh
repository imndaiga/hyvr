#!/usr/bin/env bash

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

echo "Will now globally pip install bluepy"
pip install bluepy


echo "Restarting device bus and bluetooth services"
# service dbus restart
# service bluetooth restart
systemctl start dbus
systemctl start bluetooth

echo "Validating for database instantiation"
if [ ! -f "../data/app.db" ]; then
	echo "Instatiating app database"
	python db_start.py
	echo "Running first database tests"
	python tests.py
else
	echo "App database already instatiated"
	echo "Validating for first database test"
	if [ ! -f "../data/test.db" ]; then
		echo "Running first database tests"
		python tests.py
	else
		echo "First database test already run"
	fi
fi

echo "Checking for firmware updates"
./firmwareman.sh
echo "Priming one HCI device on host"
./app/hostcon.sh -P
echo "Starting app"
python run.py