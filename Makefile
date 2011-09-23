#!/usr/bin/make
#

.PHONY: test clean cleanall

pybot_options = 

all: test

bin/python:
	virtualenv -p python2.6 --distribute --no-site-packages .

develop-eggs: bin/python bootstrap.py
	./bin/python bootstrap.py

bin/buildout: develop-eggs

bin/test: buildout.cfg bin/buildout 
	./bin/buildout -Nvt 5
	touch $@

bin/pybot: pybot.cfg buildout.cfg bin/buildout 
	./bin/buildout -Nvt 5 -c pybot.cfg
	touch $@

supervisord.pid:
	bin/supervisord --pidfile=$@

test: bin/test
	bin/test 

pybot: bin/pybot supervisord.pid
	bin/supervisorctl start all
	bin/pybot $(pybot_options)

clean: 
	test -e supervisord.pid && cat supervisord.pid | xargs kill -s TERM

cleanall: clean
	rm -fr bin develop-eggs downloads eggs parts .installed.cfg
