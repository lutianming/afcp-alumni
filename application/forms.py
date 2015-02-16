"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

from flaskext import wtf
from flaskext.wtf import validators


def validate_password(form, field):
    password = field.data
    if len(password) < 6:
        raise validators.ValidationError("password should have no less than 6 letters")

def validate_confirm_password(form, field):
    if form.new_password.data != field.data:
        raise validators.ValidationError("password not confirmed")

def validate_confirm_email(form, field):
    if form.new_email.data != field.data:
        raise validators.ValidationError("email not confirmed")

def validate_new_password(form, field):
    if form.old_password.data == field:
        raise validators.ValidationError("new password should not be the same as old password")

class LoginForm(wtf.Form):
    email = wtf.TextField('email',
                          validators=[validators.Required(),
                                      validators.Email()])
    password = wtf.PasswordField('password',
                                 validators=[validators.Required()])
    remember = wtf.BooleanField('remember')


class ForgetPasswordForm(wtf.Form):
    email = wtf.TextField('email',
                          validators=[validators.Email()])

class ResetPasswordForm(wtf.Form):
    new_password = wtf.PasswordField('new password',
                                     validators=[validators.Required(),
                                                 validate_password])
    confirm_password = wtf.PasswordField('comfirm new passowd',
                                         validators=[validators.Required(),
                                                     validate_confirm_password])

class SearchForm(wtf.Form):
    q = wtf.TextField('query', validators=[validators.Required()])


class ChangePasswordForm(wtf.Form):
    old_password = wtf.PasswordField('old password',
                                     validators=[validators.Required()])
    new_password = wtf.PasswordField('new password',
                                     validators=[validators.Required(),
                                                 validate_new_password,
                                                 validate_password])
    confirm_password = wtf.PasswordField('comfirm new passowd',
                                         validators=[validators.Required(),
                                                     validate_confirm_password])


class ChangeEmailForm(wtf.Form):
    new_email = wtf.TextField('new email',
                              validators=[validators.Email()])
    confirm_email = wtf.TextField('confirm email',
                                  validators=[validate_confirm_email])

class ActiveEmailForm(wtf.Form):
    old_email = wtf.TextField('email',
                              validators=[validators.Required(),
                                          validators.Email()])
    password = wtf.PasswordField('password',
                                 validators=[validators.Required()])

class MemberInfoForm(wtf.Form):
    sex = wtf.SelectField('sex',
                          choices=[('male', 'male'), ('female', 'female')],
                          validators=[validators.Required()])
    lastname = wtf.TextField('last name', validators=[validators.Required()])
    firstname = wtf.TextField('first name', validators=[validators.Required()])
    chinesename = wtf.TextField('chinese name')
    birthday = wtf.DateField('birthday',
                             description="format: YYYY-MM-DD",
                             validators=[validators.Optional()])
    country = wtf.SelectField('country', choices=[('china', 'china'),
                                                  ('france', 'france')],
                              validators=[validators.Required()])
    address = wtf.TextField('address')

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
    role = wtf.SelectField('role', choices=[('MEMBER', 'MEMBER'),
                                            ('ADMIN', 'ADMIN')],
                           validators=[validators.Required()])
