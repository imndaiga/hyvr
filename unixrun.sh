#!/usr/bin/env bash
# This should be run after unixrun without sudo priviledges
# otherwise all pip packages will be installed to the global
# site packages directory.
echo "Setting up runtime environment"
pip install virtualenv
virtualenv flask --system-site-packages
flask/bin/pip install -r requirements.txt

echo "Creating and testing SQLAlchemy database"
flask/bin/python db_start.py
flask/bin/python tests.py

echo "Starting app"
sudo flask/bin/python run.py