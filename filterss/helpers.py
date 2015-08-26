import re
from .forms import FilterForm
from email.utils import parsedate_tz
from filterss import app
from flask import request
from textwrap import wrap
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from werkzeug.local import LocalProxy
from xml.dom.minidom import parse


def set_filter(value):
    """
    Return filter as lower case string (for case-insensitive search) or
    return None for blank/False values
    """
    if value:
        return str(value).strip().lower()
    return None


def get_filters(obj):
    """
    Gets an object (form, request, etc) and return a dictionary with the filter
    """

    # if it is a FilterForm object with keys
    if type(obj) is FilterForm:
        d = obj.data
        d['url'] = d['rss_url']

    # if it is a GET request
    elif type(obj) is LocalProxy:
        keys = app.config['FILTERS']
        d = dict(zip(keys, map((lambda k: request.args.get(k)), keys)))

    # error
    else:
        return False

    # return a dictionary without empty items
    return clean_filters(d)


def clean_filters(d):
    """
    Delete empty fields from the filters dictionary, strip and convert strings
    to lower case
    """
    return dict((k, set_filter(v)) for k, v in d.items() if v)


def url_vars(d):
    """
    Returns a string with the URL encoded (GET) vars
    """
    cleaned = clean_filters(d)
    cleaned.pop('rss_url', None)
    return urlencode(cleaned)


def connect_n_parse(url):
    """
    Connect to a given URL and return the parse of the result
    """
    try:
        ua = 'Mozilla/5.0'
        accept = 'application/rss+xml,application/xhtml+xml,application/xml'
        hdr = {'User-Agent': ua, 'Accept': accept}
        req = Request(url, headers=hdr)
        doc = urlopen(req)
    except:
        doc = urlopen(url)
    return parse(doc)


def test_conditions(d, title, link):
    """
    Gets a dicitonary with the filters and test them comparing to the values
    from the RSS (title and link)
    """
    # iterate through the filters
    for k in d.keys():

        # check if it is a title, link or none (skip)
        if k[0:1] == 't':
            rss_content = title
        elif k[0:1] == 'l':
            rss_content = link
        else:
            rss_content = False

        # test the conditions only for title and link
        if rss_content:
            inclusive = True if k[-3:] == 'inc' else False
            cond = test_single_condition(d[k], rss_content, inclusive)

            # return false if a match is found
            if not cond:
                return False

    # else, return true
    return True


def test_single_condition(condition, value, inclusive):
    """
    Separte multiple conditions separeted by commas (filters) and test them for
    a given value; the inclusive boolean var decide if it should or should not
    be present in the given value. It always returns a boolean.
    """
    if condition is None:
        return True
    condictons = condition.split(',')
    for c in condictons:
        c = c.strip()
        if c and c in value.lower():
            return inclusive
    return not inclusive


def remove_tags(string):
    """
    Return str with certaing html/xml tags removed (title, link and pubDate)
    """
    tags = ['title', 'link', 'pubDate']
    tags_re = '({})'.format('|'.join(tags))
    starttag_re = re.compile(r'<{}(/?>|(\s+[^>]*>))'.format(tags_re, re.U))
    endtag_re = re.compile('</{}>'.format(tags_re))
    string = starttag_re.sub('', string)
    string = endtag_re.sub('', string)
    string = string.replace('<![CDATA[', '')
    string = string.replace(']]>', '')
    return string.strip()


def word_wrap(txt, length=120):
    """
    Return a wrapped a paragraph adding elipse after the first word that
    appears after a given number of characters (length var)
    """
    if len(txt) <= length or length == 0:
        return txt
    new_txt = wrap(txt, length)
    return new_txt[0] + u'…'


def format_date(string):
    """
    Return a date & time (dd/mm/yyyy hh:mm) from a rfc822 string format
    """
    new_date = parsedate_tz(string)
    y = new_date[0]
    m = '{0:0>2}'.format(new_date[1])
    d = '{0:0>2}'.format(new_date[2])
    H = '{0:0>2}'.format(new_date[3])
    i = '{0:0>2}'.format(new_date[4])
    return '{}/{}/{} {}:{}'.format(d, m, y, H, i)
