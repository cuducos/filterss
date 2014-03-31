# -*- coding: utf-8 -*-
import textwrap
import urllib
import urllib2
import re
import rfc822
from xml.dom.minidom import parse


def set_filter(value):
    """
    Return filter as lower case string (for case-insensitive search) or
    return None for blank/False values
    """
    if value:
        value = str(value)
        value = value.strip()
        return value.lower()
    return None


def url_vars(url, t_inc, t_exc, l_inc, l_exc):
    """
    Returns a string with the URL GET vars encoded
    """

    # insert values into a dictionary
    dic = {'url': url}
    if t_inc is not None and t_inc is not False:
        dic['title_inc'] = str(t_inc)
    if t_exc is not None and t_exc is not False:
        dic['title_exc'] = str(t_exc)
    if l_inc is not None and l_inc is not False:
        dic['link_inc'] = str(l_inc)
    if t_exc is not None and l_exc is not False:
        dic['link_exc'] = str(l_exc)

    # list empty entries
    del_keys = []
    for key in dic:
        value = dic[key].strip()
        if value:
            dic[key] = value
        else:
            del_keys.append(key)

    # delete empty entries
    for k in del_keys:
        del dic[k]

    # url encode and return
    return urllib.urlencode(dic)


def connect_n_parse(url):
    """
    Connect to a given URL and return the parse of the result
    """
    try:
        ua = 'Mozilla/5.0'
        accept = 'application/rss+xml,application/xhtml+xml,application/xml'
        hdr = {'User-Agent': ua, 'Accept': accept}
        req = urllib2.Request(url, headers=hdr)
        doc = urllib2.urlopen(req)
    except:
        doc = urllib2.urlopen(url)
    return parse(doc)


def test_cond(condition, value, inclusive):
    """
    Separte multiple conditions separeted by commas (filters) and test them for
    a given value; the inclusive boolean var decide if it should or should not
    macth the be present in the given value. It always returns a boolean.
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
    tags_re = '(%s)' % '|'.join(tags)
    starttag_re = re.compile(r'<%s(/?>|(\s+[^>]*>))' % tags_re, re.U)
    endtag_re = re.compile('</%s>' % tags_re)
    string = starttag_re.sub('', string)
    string = endtag_re.sub('', string)
    string = string.replace('<![CDATA[', '')
    string = string.replace(']]>', '')
    return string.strip()


def word_wrap(txt, length=48):
    """
    Return a wrapped a paragraph adding elipse after the first word that
    appears after a given number of characters (length var)
    """
    if len(txt) <= length or length == 0:
        return txt
    new_txt = textwrap.wrap(txt, length)
    return new_txt[0] + u'…'


def format_date(string):
    """
    Return a date (dd/mm/yyyy) from a rfc822 string format
    """
    new_date = rfc822.parsedate_tz(string)
    y = str(new_date[0])
    m = str(new_date[1])
    d = str(new_date[2])
    if len(d) < 2:
        d = '0' + d
    if len(m) < 2:
        m = '0' + m
    return d + '/' + m + '/' + y


def test_url(url):
    """
    Test the URL and returns True, False or a string with a
    corrected URL value according to common errors
    """
    prefix_pattern = '(https?:?\/\/|feed:\/\/)'
    sufix_pattern = '([a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(\/\S*)?)'
    pattern = prefix_pattern + sufix_pattern
    url = str(url)
    test = re.search(pattern, url)
    if test:
        prefix = test.group(1)
        if prefix == 'feed://':
            return 'http://' + test.group(2)
        elif prefix == 'http//' or prefix == 'https//':
            new_prefix = prefix.replace('//', '://')
            return new_prefix + test.group(2)
        else:
            return True
    else:
        new_url = 'http://' + url
        new_test = re.match(pattern, new_url)
        if new_test:
            return new_url
        else:
            return False


def get_url(url):
    """
    Use test_url() to try to correct an URL according to common errors
    and return a string (the original URL or the corrected one)
    """
    url_tested = test_url(url)
    if test_url in ('True', 'False'):
        return url
    else:
        return url_tested
