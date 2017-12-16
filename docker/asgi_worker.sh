#!/bin/sh
#make collectstatic
python manage.py runworker --threads 4
