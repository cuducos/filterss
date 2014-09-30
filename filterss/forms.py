from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired, URL


class FilterForm(Form):
    rss_url = TextField('URL of your RSS', [
        DataRequired('No URL entered'),
        URL(True, 'Invalid URL')])
    title_inc = TextField('Title must contain')
    title_exc = TextField('Title cannot contain')
    link_inc = TextField('Link must contain')
    link_exc = TextField('Link cannot contain')
