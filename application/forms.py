"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

from flaskext import wtf
from flaskext.wtf import validators
from wtforms.ext.appengine.ndb import model_form


class LoginForm(wtf.Form):
    username = wtf.TextField('username',
                             validators=[validators.Required()])
    password = wtf.PasswordField('password',
                                 validators=[validators.Required()])
    remember = wtf.BooleanField('remember')


class ChangePasswordForm(wtf.Form):
    old_password = wtf.PasswordField('old password',
                                     validators=[validators.Required()])
    new_password = wtf.PasswordField('new password',
                                     validators=[validators.Required()])
    comfirm_password = wtf.PasswordField('comfirm new passowd',
                                         validators=[validators.Required()])


class MemberInfoForm(wtf.Form):
    sex = wtf.SelectField('sex',
                          choices=[('male', 'male'), ('female', 'female')],
                          validators=[validators.Required()])
    lastname = wtf.TextField('last name', validators=[validators.Required()])
    firstname = wtf.TextField('first name', validators=[validators.Required()])
    chinesename = wtf.TextField('chinese name')
    birthday = wtf.DateField('birthday',
                             validators=[validators.Optional()])
    country = wtf.SelectField('country', choices=[('china', 'china'),
                                                  ('france', 'france')],
                              validators=[validators.Required()])
    address = wtf.TextField('address')
    email = wtf.TextField('email',
                          validators=[validators.Required(), validators.Email()])
    weibo = wtf.TextField('weibo')
    weixin = wtf.TextField('weixin')
    phone = wtf.TextField('phone')

    chinese_university = wtf.TextField('chinese university')
    paristech_school = wtf.TextField('paristech shool')
    paristech_entrance_year = wtf.IntegerField('paristech entrance year')
    domain_china = wtf.TextField('domain in China')
    domain_france = wtf.TextField('domain in France')

    employer = wtf.TextField('employer')

class MemberForm(MemberInfoForm):
    role = wtf.SelectField('role', choices=[('ADMIN', 'ADMIN'),
                                            ('MEMBER', 'MEMBER')],
                           validators=[validators.Required()])
