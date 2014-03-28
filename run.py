#!venv/bin/python
from app import app
app.debug = True
if not app.debug:
    import logging
    from logging.handlers import FileHandler
    file_handler = FileHandler('log.txt')
    file_handler.setLevel(logging.INFO)
app.run()
