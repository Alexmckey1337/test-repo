from resources import *
from celery import Celery
from edem.celery import app


@app.task(name='generate')
def generate():
    make_table()
    return True

