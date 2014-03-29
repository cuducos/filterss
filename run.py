#!venv/bin/python
from app import app
import os
app.debug = True
basedir = os.path.abspath(os.path.dirname(__file__))
if not app.debug:
    import logging
    from logging.handlers import SysLogHandler
    handler = SysLogHandler()
    handler.setLevel(logging.INFO)
app.run()
