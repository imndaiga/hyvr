#!/usr/bin/env bash

echo "Checking bluez package"
# download, unzip, configure, build and install bluez4.101
# if a dependancy error is output from the configure script
# that typically means that a particular apt-get package install
# failed.
# http://www.linuxfromscratch.org/blfs/view/7.4/general/bluez.html
dpkg -s bluez
if [ $? != 0 ]; then
    echo "Will download, unzip, configure, build and install bluez4.101"
    mkdir bluez && \
    cd bluez && \
    wget www.kernel.org/pub/linux/bluetooth/bluez-4.101.tar.xz && \
    # bootscripts not required since checkinstall manages all that
    # wget anduin.linuxfromscratch.org/BLFS/blfs-bootscripts/blfs-bootscripts-20150924.tar.bz2 && \
    # tar xvjpf blfs-bootscripts-20150924.tar.bz2 && \
    unxz bluez-4.101.tar.xz && \
    tar xvf bluez-4.101.tar && \
    cd bluez-4.101 && \
    ./configure --prefix=/usr       \
            --mandir=/usr/share/man \
            --sysconfdir=/etc       \
            --localstatedir=/var    \
            --libexecdir=/lib       \
            --enable-bccmd          \
            --enable-dfutool        \
            --enable-dund           \
            --enable-hid2hci        \
            --enable-hidd           \
            --enable-pand           \
            --enable-tools          \
            --enable-wiimote        && \
    make && \
    # using checkinstall to install the bluez package instead of make
    # as described by lfs
    checkinstall -y
    # for CONFFILE in audio input network serial ; do
    #     install -v -m644 ${CONFFILE}/${CONFFILE}.conf /etc/bluetooth/${CONFFILE}.conf
    # done
    # unset CONFFILE && \
    # install -v -m755 -d /usr/share/doc/bluez-4.101 && \
    # install -v -m644 doc/*.txt /usr/share/doc/bluez-4.101
    # cd ../blfs-bootscripts-20150924 && \
    # make install-bluetooth && \
    # make clean && \
    # make distclean && \
else
    bluezversion=$(dpkg -s bluez | grep -i version)
    echo "Bluez already installed: version $bluezversion"
fi

cd /webot

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