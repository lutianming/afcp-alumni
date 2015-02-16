"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
from google.appengine.api import search as gsearch, mail
from google.appengine.ext import ndb
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from flask import request, render_template, flash, url_for, redirect

from flask_cache import Cache
import flask_login
from flask_login import current_user
from application import app
from decorators import login_required, admin_required
from forms import LoginForm, ChangePasswordForm, MemberInfoForm, SearchForm, ForgetPasswordForm, ResetPasswordForm, ChangeEmailForm, ActiveEmailForm
from models import MemberModel, ResetPasswordModel, ChangeEmailModel
from admin import update_document
import datetime

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


def home():
    form = LoginForm(request.form)
    return render_template('index.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if current_user.is_authenticated():
        return redirect(url_for('home'))

    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data

        member = MemberModel.query(MemberModel.email == email,
                                   MemberModel.password == password).get()

        if member:
            flask_login.login_user(member, remember=remember)
            member.last_login = datetime.datetime.now()
            member.put()

            # flash('log in', category="success")
            return redirect(url_for('home'))
        flash('login failed, wrong email or password', category="danger")
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('home'))

@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    form = ForgetPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        time = datetime.datetime.now() + datetime.timedelta(days=1)
        model = ResetPasswordModel(
            email=email,
            expire_time=time
        )
        model.put()

        link = url_for('reset_password', id=model.key.urlsafe())
        sender = "admin@afcp-alumni.com"
        message = mail.EmailMessage(sender=sender)
        message.to = email
        message.subject = "reset password"
        message.body = """
        reset your password by the following link:
        {0}
        """.format(link)
        message.send()

        flash(link)
    return render_template('forget_password.html', form=form)


@app.route('/change_email', methods=['GET', 'POST'])
def change_email():
    form = ChangeEmailForm(request.form)
    if request.method == 'POST' and form.validate():
        new_email = form.new_email.data

        #test if new email is already used by others
        exist = MemberModel.query(MemberModel.email==new_email).get()
        if exist:
            flash("this email address is already used by others")
        else:
            old_email = current_user.email
            time = datetime.datetime.now() + datetime.timedelta(days=1)

            model = ChangeEmailModel(
                email=old_email,
                new_email=new_email,
                expire_time=time
            )
            model.put()
            link = url_for('active_email', id=model.key.urlsafe())
            sender = app.config["SENDER"]
            message = mail.EmailMessage(sender=sender)
            message.to = new_email
            message.subject = "change email"
            message.body = """
            change your email by clicking the following link:
            {0}
                       """.format(link)
            message.send()
            flash("mail sent, please follow the instuction in your mail to change your mail")
            return redirect(url_for('account'))
    return render_template('change_email.html', form=form)


@app.route('/active_email', methods=['GET', 'POST'])
def active_email():
    form = LoginForm(request.form)
    id = request.args.get('id', '')
    key = ndb.Key(urlsafe=id)
    r = key.get()
    if not r or r.expire_time < datetime.datetime.now():
        flash("not valided link")
        return redirect(url_for('home'))
    if request.method == 'POST' and form.validate():
        old_email = form.email.data
        password = form.password.data
        new_email = r.new_email
        member = MemberModel.query(MemberModel.email==old_email,
                                   MemberModel.password==password).get()
        if member:
            member.email = new_email
            member.put()
            update_document(member)
            flash('email updated')

            key.delete()
            return redirect(url_for('account'))
        else:
            flash('old email or password not validated')
    return render_template('active_email.html', form=form, id=id)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm(request.form)

    urlsafe = request.args.get('id', '')
    key = ndb.Key(urlsafe=urlsafe)
    r = key.get()
    if not r or r.expire_time < datetime.datetime.now():
        flash('not valide URL')
        return redirect(url_for('home'))

    if request.method == 'POST' and form.validate():
        password = form.new_password.data
        member = MemberModel.query(MemberModel.email==r.email).get()
        member.password = password

        flask_login.login_user(member)
        member.last_login = datetime.datetime.now()
        member.put()
        #delete reset request model after change
        key.delete()

        flash('password changed')
        return redirect(url_for('home'))
    return render_template('reset_password.html', form=form, id=urlsafe)

@app.route('/account')
@login_required
def account():
    return render_template('personal.html')


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        oldpassword = form.old_password.data
        newpassword = form.new_password.data
        if oldpassword == current_user.password:
            current_user.password = newpassword
            current_user.put()
            flash('password changed')

            return redirect(url_for('account'))
        else:
            flash('wrong password')

    return render_template('change_password.html', form=form)


@app.route('/update_info', methods=['GET', 'POST'])
@login_required
def update_info():
    form = MemberInfoForm(request.form, obj=current_user)
    if request.method == 'POST' and form.validate():
        for field in form:
            #need to comfirn that the field is not email or password
            #which should be changed by other methods
            if field.name == 'email' or field.name == 'password':
                continue
            setattr(current_user, field.name, field.data)
        current_user.put()
        update_document(current_user)
        flash('info updated')
        return redirect(url_for('account'))

    return render_template('update_info.html', form=form)

@app.route('/members/')
@login_required
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
@login_required
def member(urlsafe):
    key = ndb.Key(urlsafe=urlsafe)
    member = key.get()
    return render_template('member.html', member=member)


@app.route('/search')
@login_required
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
