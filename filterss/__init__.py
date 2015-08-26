from flask import Flask
from flask.ext.script import Manager

# init app
app = Flask('filterss')
app.config.from_object('config')
manager = Manager(app)
from filterss import views
