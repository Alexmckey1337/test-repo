#!/bin/sh
#make collectstatic
/usr/local/bin/gunicorn edem.wsgi:application -c /app/gunicorn/conf.py
