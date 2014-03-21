import urllib, urllib2
import urllib2
from xml.dom.minidom import parse
from flask import render_template, redirect, request, make_response
from app import app
from flask_wtf import Form
from forms import FilterForm

@app.route('/')
@app.route('/index')
def index():
    form = FilterForm()
    return render_template('form.html', form=form)

@app.route('/filter', methods=('GET', 'POST'))
def filter():
    form = FilterForm()
    if form.validate_on_submit():
        url_query = url_vars(form.rss_url.data,
            form.title_inc.data,
            form.title_exc.data,
            form.link_inc.data,
            form.link_exc.data)
        return redirect('/info?' + url_query)
    return render_template('form.html', form=form)

@app.route('/rss')
def rss():
    
    # load GET vars
    url = str(request.args.get("url"))
    t_inc = set_filter(request.args.get("title_inc"))
    t_exc = set_filter(request.args.get("title_exc"))
    l_inc = set_filter(request.args.get("link_inc"))
    l_exc = set_filter(request.args.get("link_exc"))
    
    # load orginal RSS (xml)
    try:
        doc = urllib2.urlopen(url)
        dom = parse(doc)
    except:
        return abort(404)

    # loop items
    for item in dom.getElementsByTagName('item'):
        
        # get title & link
        title = item.getElementsByTagName('title')[0].toxml()
        link = item.getElementsByTagName('link')[0].toxml()
        title = title[7:-8]
        link = link[6:-7]

        # test conditions
        cond1 = not t_inc or t_inc in title.lower()
        cond2 = not t_exc or t_exc not in title.lower()
        cond3 = not l_inc or l_inc in link.lower()
        cond4 = not l_exc or l_exc not in link.lower()

        # delete undesired nodes
        if not cond1 or not cond2 or not cond3 or not cond4:
            item.parentNode.removeChild(item)

    # print RSS (xml)
    filtered = dom.toxml()
    response= make_response(filtered)
    response.headers["Content-Type"] = "application/xml"    
    return response


@app.route('/info')
def info():

    # load GET vars
    url = str(request.args.get("url"))
    t_inc = set_filter(request.args.get("title_inc"))
    t_exc = set_filter(request.args.get("title_exc"))
    l_inc = set_filter(request.args.get("link_inc"))
    l_exc = set_filter(request.args.get("link_exc"))
    rss_url = request.url_root + 'rss?' + url_vars(url, t_inc, t_exc, l_inc, l_exc)
    rss_url_encoded = urllib.quote(rss_url)

    # load orginal RSS (xml)
    try:
        doc = urllib2.urlopen(url)
        dom = parse(doc)
    except:
        url_query = url_vars(url, t_inc, t_exc, l_inc, l_exc)
        return render_template('/error?' + url_query)

    # get title
    rss_title = dom.getElementsByTagName('title')[0].toxml()
    rss_title = rss_title[7:-8]
    rss_title = rss_title.strip()

    # loop items
    all_items = []
    filtered_items = []
    for item in dom.getElementsByTagName('item'):
        
        # get title & link
        title = item.getElementsByTagName('title')[0].toxml()
        link = item.getElementsByTagName('link')[0].toxml()
        date = item.getElementsByTagName('pubDate')[0].toxml()
        title = title[7:-8]
        link = link[6:-7]
        date = date[14:-25]

        # test conditions
        cond1 = not t_inc or t_inc in title.lower()
        cond2 = not t_exc or t_exc not in title.lower()
        cond3 = not l_inc or l_inc in link.lower()
        cond4 = not l_exc or l_exc not in link.lower()

        # sort nodes
        if cond1 and cond2 and cond3 and cond4:
            filtered_items.append([title, link, date])
        all_items.append([title, link, date])

    return render_template('info.html',
        url=url,
        rss_title=rss_title,
        rss_url=rss_url,
        rss_url_encoded=rss_url_encoded,
        all_items=all_items,
        filtered_items=filtered_items)


@app.route('/error')
def error():
    url = str(request.args.get("url"))
    return render_template('error.html', url=url)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def set_filter (value):
    if value:
        value = str(value)
        value = value.strip()
        return value.lower()
    return None


def url_vars(url, t_inc, t_exc, l_inc, l_exc):
    
    # insert values into a dictionary
    dic = { 'url' : url }
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
