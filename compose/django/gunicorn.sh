#!/bin/sh
#make collectstatic
/usr/local/bin/gunicorn edem.wsgi:application -w 4 -b 0.0.0.0:5000 --chdir=/app
