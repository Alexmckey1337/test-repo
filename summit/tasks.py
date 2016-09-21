# -*- coding: utf-8
from __future__ import unicode_literals

from edem.celery import app
from .resources import make_table


@app.task(name='generate')
def generate():
    make_table()
    return True
