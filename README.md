# userapi #

A simple user api service.

## Docker setup ##

build a docker container:

~~~~
$ sudo docker build .

.. lots of stuff, lots of time ..

Successfully built <some image number>
~~~~

then run it, redirecting port 5000

~~~~
$ sudo docker run -p 5000:5000 <the image created>
~~~~

Endpoint will sit at port 5000.


## Manual Setup ##

Simplest manual run of the code would use pip and virtualenv, along
with the pip requirements listed in requirements.txt:

apt-get install -y python-pip python-virtualenv
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt

Next, create the empty database:

./manage.py -c ./userapi.conf.sample create_db

This will make a sqlite database in /tmp

Then run the app:

./manage.py -c ./userapi.conf.sample runserver

## Tests ##

tests can be run with `./run_tests.sh`

pep8/pyflakes can be checked with `./run_tests.sh pep8`
