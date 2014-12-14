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
from forms import LoginForm, ChangePasswordForm, MemberInfoForm
from models import MemberModel


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


def home():
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
            flask_login.login_user(member, remember=remember)
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

@app.route('/members')
def members():
    members = MemberModel.query()
    return render_template('members.html', members=members)

@app.route('/member/<urlsafe>')
def member(urlsafe):
    key = ndb.Key(urlsafe=urlsafe)
    member = key.get()
    return render_template('member.html', member=member)


@app.route('/search')
def search():
    q = request.args.get('q', '')
    members = MemberModel.query(ndb.OR(MemberModel.lastname == q,
                                       MemberModel.firstname == q))
    return render_template('index.html', members=members)


def say_hello(username):
    """Contrived example to demonstrate Flask's url routing capabilities"""
    return 'Hello %s' % username


@admin_required
def admin_only():
    """This view requires an admin account"""
    return 'Super-seekrit admin page.'


@app.route('/upload_member_file')
def upload_member_file():
    pass


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

