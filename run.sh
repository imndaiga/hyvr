#!/usr/bin/env bash

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

echo "Restarting device bus and bluetooth services"
# service dbus restart
# service bluetooth restart
systemctl restart dbus
systemctl restart bluetooth

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