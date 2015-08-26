from os import getenv

CSRF_ENABLED = True
SECRET_KEY = getenv('SECRET_KEY', 't8SUHN4727Q29XZU9BNkLNd0eRlvSEzp1Rs9PgWm')
TITLE = 'Filterss: More power over your feeds'
FILTERS = ['url', 'title_inc', 'title_exc', 'link_inc', 'link_exc']
