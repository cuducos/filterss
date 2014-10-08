# coding: utf-8
import sys
import urllib
from flask import render_template, redirect, request, make_response, abort
from filterss import app
from forms import FilterForm
from helpers import (
    connect_n_parse, format_date, get_filters, remove_tags, test_conditions,
    url_vars, word_wrap
)


reload(sys)
sys.setdefaultencoding('utf-8')


@app.route('/')
def index():
    return render_template('form.html',
                           js='init',
                           title=app.config['TITLE'],
                           form=FilterForm())


@app.route('/filter', methods=('GET', 'POST'))
def filter():
    form = FilterForm()
    if form.validate_on_submit():
        url_query = url_vars(get_filters(form))
        return redirect('/info?{}'.format(url_query))
    return render_template('form.html',
                           js='init',
                           title=app.config['TITLE'],
                           form=FilterForm())


@app.route('/info')
def info():

    # load GET vars
    values = get_filters(request)
    url_vars_encoded = url_vars(values)
    rss_url = '{}rss?{}'.format(request.url_root, url_vars_encoded)
    edit_url = '{}edit?{}'.format(request.url_root, url_vars_encoded)
    rss_url_encoded = urllib.quote(values['url'])

    # load orginal RSS (xml)
    try:
        dom = connect_n_parse(values['url'])
    except:
        return redirect('/error?{}'.format(url_vars_encoded))

    # get title
    rss_title = remove_tags(dom.getElementsByTagName('title')[0].toxml())

    # loop items
    all_items = []
    for item in dom.getElementsByTagName('item'):

        # get title & link
        title = item.getElementsByTagName('title')[0].toxml()
        link = item.getElementsByTagName('link')[0].toxml()
        date = item.getElementsByTagName('pubDate')[0].toxml()
        title = remove_tags(title)
        link = remove_tags(link)
        date = remove_tags(date)

        # test conditions
        conditions = test_conditions(values, title, link)

        # create item
        item = {'title': title,
                'title_wrap': word_wrap(title),
                'url': link,
                'date': format_date(date),
                'css_class': '' if conditions else 'skip'}
        all_items.append(item)

    return render_template(
        'info.html',
        js='info',
        title='#filterss {}'.format(rss_title),
        url=values['url'],
        rss_title=rss_title,
        rss_url=rss_url,
        rss_url_encoded=rss_url_encoded,
        edit_url=edit_url,
        all_items=all_items)


@app.route('/edit', methods=('GET', 'POST'))
def edit():

    # load GET vars
    values = get_filters(request)
    values['rss_url'] = values['url']

    # insert values into form
    form = FilterForm()
    for field in form:
        if field.name in values.keys():
            field.data = values[field.name]

    # render the form with loaded data
    return render_template('form.html',
                           js='init',
                           title=app.config['TITLE'],
                           form=form)


@app.route('/rss')
def rss():

    # load GET vars
    values = get_filters(request)

    # load orginal RSS (xml)
    try:
        dom = connect_n_parse(values['url'])
    except:
        return abort(500)

    # change title
    title_node = dom.getElementsByTagName('title')[0]
    rss_title = remove_tags(title_node.toxml())
    title_node.firstChild.replaceWholeText('#filterss {}'.format(rss_title))

    # loop items
    for item in dom.getElementsByTagName('item'):

        # get title & link
        title = remove_tags(item.getElementsByTagName('title')[0].toxml())
        link = remove_tags(item.getElementsByTagName('link')[0].toxml())

        # test conditions
        conditions = test_conditions(values, title, link)

        # delete undesired nodes
        if not conditions:
            item.parentNode.removeChild(item)

    # print RSS (xml)
    filtered = dom.toxml()
    response = make_response(filtered)
    response.headers["Content-Type"] = "application/xml"
    return response


@app.route('/robots.txt', methods=['GET'])
def sitemap():
    response = make_response(open('robots.txt').read())
    response.headers["Content-type"] = "text/plain"
    return response


@app.route('/error')
def error():
    url = str(request.args.get("url"))
    return render_template('error.html', url=url)


@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html'), 500
