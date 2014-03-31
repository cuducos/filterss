# -*- coding: utf-8 -*-
import textwrap
import urllib
import urllib2
import re
import rfc822
from xml.dom.minidom import parse
from flask import render_template, redirect, request, make_response, abort
from app import app
from forms import FilterForm
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


@app.route('/')
@app.route('/index')
def index():
    form = FilterForm()
    return render_template('form.html', form=form)


@app.route('/filter', methods=('GET', 'POST'))
def filter():
    form = FilterForm()
    if form.validate_on_submit():
        url = get_url(form.rss_url.data)
        url_query = url_vars(
            url,
            form.title_inc.data,
            form.title_exc.data,
            form.link_inc.data,
            form.link_exc.data)
        return redirect('/info?' + url_query)
    return render_template('form.html', form=form)


@app.route('/rss')
def rss():

    # load GET vars
    url = set_filter(request.args.get("url"))
    t_inc = set_filter(request.args.get("title_inc"))
    t_exc = set_filter(request.args.get("title_exc"))
    l_inc = set_filter(request.args.get("link_inc"))
    l_exc = set_filter(request.args.get("link_exc"))

    # load orginal RSS (xml)
    try:
        dom = connect_n_parse(url)
    except:
        return abort(404)

    # loop items
    for item in dom.getElementsByTagName('item'):

        # get title & link
        title = item.getElementsByTagName('title')[0].toxml()
        link = item.getElementsByTagName('link')[0].toxml()
        title = remove_tags(title)
        link = remove_tags(link)

        # test conditions
        cond1 = test_cond(t_inc, title, True)
        cond2 = test_cond(t_exc, title, False)
        cond3 = test_cond(l_inc, link, True)
        cond4 = test_cond(l_exc, link, False)

        # delete undesired nodes
        if not cond1 or not cond2 or not cond3 or not cond4:
            item.parentNode.removeChild(item)

    # print RSS (xml)
    filtered = dom.toxml()
    response = make_response(filtered)
    response.headers["Content-Type"] = "application/xml"
    return response


@app.route('/info')
def info():

    # load GET vars
    url = set_filter(request.args.get("url"))
    t_inc = set_filter(request.args.get("title_inc"))
    t_exc = set_filter(request.args.get("title_exc"))
    l_inc = set_filter(request.args.get("link_inc"))
    l_exc = set_filter(request.args.get("link_exc"))
    rss_url = request.url_root + 'rss?'
    rss_url = rss_url + url_vars(url, t_inc, t_exc, l_inc, l_exc)
    rss_url_encoded = urllib.quote(rss_url)

    # load orginal RSS (xml)
    try:
        dom = connect_n_parse(url)
    except:
        url_query = url_vars(url, t_inc, t_exc, l_inc, l_exc)
        return redirect('/error?' + url_query)

    # get title
    rss_title = dom.getElementsByTagName('title')[0].toxml()
    rss_title = remove_tags(rss_title)

    # loop items
    all_items = []
    filtered_items = []
    for item in dom.getElementsByTagName('item'):

        # get title & link
        title = item.getElementsByTagName('title')[0].toxml()
        link = item.getElementsByTagName('link')[0].toxml()
        date = item.getElementsByTagName('pubDate')[0].toxml()
        title = remove_tags(title)
        link = remove_tags(link)
        date = remove_tags(date)

        # test conditions
        cond1 = test_cond(t_inc, title, True)
        cond2 = test_cond(t_exc, title, False)
        cond3 = test_cond(l_inc, link, True)
        cond4 = test_cond(l_exc, link, False)

        # sort nodes
        item_class = 'normal'
        item = {'title': title,
                'title_wrap': word_wrap(title),
                'url': link,
                'date': format_date(date),
                'css_class': item_class}
        if cond1 and cond2 and cond3 and cond4:
            filtered_items.append(item)
            item['css_class'] = 'skip'
        all_items.append(item)

    return render_template(
        'info.html',
        url=url,
        rss_title=rss_title,
        rss_url=rss_url,
        rss_url_encoded=rss_url_encoded,
        all_items=all_items,
        filtered_items=filtered_items)


@app.route('/check_url', methods=['GET'])
def check_url():
    url = request.args.get('url')
    return str(test_url(url))


@app.route('/robots.txt', methods=['GET'])
def sitemap():
    response = make_response(open('robots.txt').read())
    response.headers["Content-type"] = "text/plain"
    return response


@app.route('/error')
def error():
    url = str(request.args.get("url"))
    return render_template('error.html', url=url)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


def set_filter(value):
    if value:
        value = str(value)
        value = value.strip()
        return value.lower()
    return None


def url_vars(url, t_inc, t_exc, l_inc, l_exc):

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
    if condition is None:
        return True
    condictons = condition.split(',')
    for c in condictons:
        c = c.strip()
        if c and c in value.lower():
            return inclusive
    return not inclusive


def remove_tags(string):
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
    if len(txt) <= length or length == 0:
        return txt
    new_txt = textwrap.wrap(txt, length)
    return new_txt[0] + u'…'


def format_date(string):
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
    url_tested = test_url(url)
    if test_url in ('True', 'False'):
        return url
    else:
        return url_tested
