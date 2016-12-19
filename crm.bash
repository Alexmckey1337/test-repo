#!/bin/bash
 
NAME="crm"                                  # Name of the application
DJANGODIR=/projects/crm/project/            # Django project directory
SOCKFILE=/projects/crm/socket/crm.sock
USER=avrama                                       # the user to run as
                                    # the group to run as
NUM_WORKERS=3                                     # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=edem.settings.production             # which settings file should Django use
DJANGO_WSGI_MODULE=edem.wsgi                     # WSGI module name
 
echo "Starting $NAME as `whoami`"
 
# Activate the virtual environment
cd $DJANGODIR
source /projects/crm/venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
 
# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec /projects/crm/venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER \
  --bind=unix:$SOCKFILE \
  --log-level=error \
  --log-file=-
  --timeout=90
  --graceful-timeout=10

