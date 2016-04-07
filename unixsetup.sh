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
    checkinstall \
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
echo "Running firmware manager"
./firmwareman.sh
echo "Priming one HCI device on host"
./app/hostcon.sh -P