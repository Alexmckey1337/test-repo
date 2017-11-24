#!/bin/sh
#make collectstatic
/usr/local/bin/gunicorn --bind 0.0.0.0:7000 main
