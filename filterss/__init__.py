from flask import Flask

app = Flask('filterss')
app.config.from_object('config')

from .views import site
app.register_blueprint(site)
