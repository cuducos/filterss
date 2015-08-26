from flask import Flask
from flask.ext.script import Manager

app = Flask('filterss')
app.config.from_object('config')
manager = Manager(app)

from .views import site
app.register_blueprint(site)
