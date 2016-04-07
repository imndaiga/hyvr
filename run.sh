#!/usr/bin/env bash
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