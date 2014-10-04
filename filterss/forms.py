from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired, URL


class FilterForm(Form):
    rss_url = TextField('URL of your RSS', [
        DataRequired('No URL entered'),
        URL(True, 'Invalid URL')])
    t_inc = TextField('Title must contain')
    t_exc = TextField('Title cannot contain')
    l_inc = TextField('Link must contain')
    l_exc = TextField('Link cannot contain')
