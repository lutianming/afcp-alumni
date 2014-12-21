"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
from google.appengine.api import search as gsearch
from google.appengine.ext import ndb
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from flask import request, render_template, flash, url_for, redirect

from flask_cache import Cache
import flask_login
from flask_login import current_user
from application import app
from decorators import login_required, admin_required
from forms import LoginForm, ChangePasswordForm, MemberInfoForm, SearchForm
from models import MemberModel
import datetime

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        email = form.username.data
        password = form.password.data
        remember = form.remember.data

        member = MemberModel.query(MemberModel.email == email,
                                   MemberModel.password == password).get()

        if member:
            flask_login.login_user(member, remember=remember)
            member.last_login = datetime.datetime.now()
            member.put()

    return redirect(url_for('home'))


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('home'))

@app.route('/personal')
@login_required
def personal():
    return render_template('personal.html')


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        oldpassword = form.old_password.data
        newpassword = form.new_password.data
        comfirm = form.comfirm_password.data
        if oldpassword == current_user.password and \
           newpassword == comfirm:
            current_user.password = newpassword
            current_user.put()
            flash('password changed')
        else:
            if oldpassword != current_user.password:
                flash('wrong password')
            if newpassword != comfirm:
                flash('new password not comfirmed')
    return render_template('change_password.html', form=form)


@app.route('/update_info', methods=['GET', 'POST'])
@login_required
def update_info():
    form = MemberInfoForm(request.form, obj=current_user)
    if request.method == 'POST' and form.validate():
        for field in form:
            setattr(current_user, field.name, field.data)
        current_user.put()
        flash('info updated')
    return render_template('update_info.html', form=form)

@app.route('/members/')
def members():
    page_size = 20
    page = int(request.args.get('page', 0))
    
    query = MemberModel.query()
    members = query.fetch(page_size, offset=page*page_size)
    num_pages = query.count() / page_size
    
    def pager_url(p):
        return url_for('members', page=p)
    
    return render_template('members.html', members=members,
                           page=page, num_pages=num_pages,
                           pager_url=pager_url)

@app.route('/member/<urlsafe>')
def member(urlsafe):
    key = ndb.Key(urlsafe=urlsafe)
    member = key.get()
    return render_template('member.html', member=member)


@app.route('/search')
def search():
    page_size = 20
    page = int(request.args.get('page', 0))

    q = request.args.get('q', '')
    index = gsearch.Index(name='members')

    options = gsearch.QueryOptions(
        limit=page_size,
        offset=page_size*page,
    )
    query = gsearch.Query(query_string=q, options=options)
    result = index.search(query)
    count = result.number_found

    num_pages = count / page_size
    
    def pager_url(p):
        return url_for('search', q=q, page=p)
    return render_template('search.html', results=result,
                           page=page,
                           num_pages=num_pages,
                           pager_url=pager_url,
                           q=q)

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route('/routes')
def routes():
    rules = []
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint)
            rules.append(rule.endpoint + ': ' + url)
    return '</br>'.join(rules)

@admin_required
def admin_only():
    """This view requires an admin account"""
    return 'Super-seekrit admin page.'


@app.route('/upload_member_file')
def upload_member_file():
    pass


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''

