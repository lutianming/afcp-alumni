"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect

from flask_cache import Cache
import flask_login
from flask_login import current_user
from application import app
from decorators import login_required, admin_required
from forms import LoginForm
from models import MemberModel


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


def home():
    print(current_user)
    members = MemberModel.query()
    return render_template('index.html', members=members)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        username = form.username.data
        password = form.password.data
        remember = form.remember.data

        member = MemberModel.query(MemberModel.username == username,
                                   MemberModel.password == password).get()

        if member:
            result = flask_login.login_user(member, remember=remember)
            print(result)
    return redirect(url_for('home'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    flask_login.logout_user()
    return redirect(url_for('home'))

@app.route('/member/<urlsafe>')
def member(urlsafe):
    key = ndb.Key(urlsafe=urlsafe)
    member = key.get()
    return render_template('member.html', member=member)


@app.route('/search', methods=['GET', 'POST'])
def search():
    return redirect(url_for('home'))

def say_hello(username):
    """Contrived example to demonstrate Flask's url routing capabilities"""
    return 'Hello %s' % username


@admin_required
def admin_only():
    """This view requires an admin account"""
    return 'Super-seekrit admin page.'


@cache.cached(timeout=60)
def cached_examples():
    """This view should be cached for 60 sec"""
    examples = ExampleModel.query()
    return render_template('list_examples_cached.html', examples=examples)


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''

