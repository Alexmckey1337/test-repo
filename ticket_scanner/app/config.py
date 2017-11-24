# -*- coding: utf-8 -*-
import argparse
import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

# Startup Settings
parser = argparse.ArgumentParser()
parser.add_argument("--ip", default='0.0.0.0', type=str, help='IP to run'),
parser.add_argument("--port", default='7000', type=int, help='Port to listen'),

args = parser.parse_args()

# Application config:
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
bootstrap = Bootstrap(app)

# Database config:
USER = os.environ.get('DB_USER', 'crm_user')
PASSWORD = os.environ.get('DB_PASSWORD', 'crm_pass')
TABLE = os.environ.get('DB_TABLE', 'crm_db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://crm_user:crm_pass@localhost/crm_db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{0}:{1}@localhost:5432/{2}'.format(USER, PASSWORD, TABLE)
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)

# API config:
VISITORS_LOCATION_TOKEN = os.environ.get('VISITORS_LOCATION_TOKEN',
                                         '4ewfeciss6qdbmgfj9eg6jb3fdcxefrs4dxtcdrt10rduds2sn')
