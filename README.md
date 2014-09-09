# userapi #

A simple user api service.

## Manual Setup ##

Simplest manual run of the code would use pip and virtualenv, along
with the pip requirements listed in requirements.txt:

apt-get install -y python-pip python-virtualenv
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt

Next, create the empty database:

./manage.py -c ./userapi.conf.sample db_create

This will make a sqlite database in /tmp

Then run the app:

./manage.py -c ./userapi.conf.sample runserver
