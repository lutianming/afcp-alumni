"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

from flaskext import wtf
from flaskext.wtf import validators
from wtforms.ext.appengine.ndb import model_form

from .models import ExampleModel


class ClassicExampleForm(wtf.Form):
    example_name = wtf.TextField('Name', validators=[validators.Required()])
    example_description = wtf.TextAreaField('Description', validators=[validators.Required()])

# App Engine ndb model form example
ExampleForm = model_form(ExampleModel, wtf.Form, field_args={
    'example_name': dict(validators=[validators.Required()]),
    'example_description': dict(validators=[validators.Required()]),
})

class LoginForm(wtf.Form):
    username = wtf.TextField('username',
                             validators=[validators.Required()])
    password = wtf.PasswordField('password',
                                 validators=[validators.Required()])
    remember = wtf.BooleanField('remember')
    
class MemberForm(wtf.Form):
    username = wtf.TextField('username', validators=[validators.Required()])
    password = wtf.PasswordField('password', validators=[validators.Required()])
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
    email = wtf.TextField('email', validators=[validators.Required(), validators.Email()])
    weibo = wtf.TextField('weibo')
    weixin = wtf.TextField('weixin')
    phone = wtf.TextField('phone')

    chineseUniversity = wtf.TextField('chinese university')
    paristechSchool = wtf.TextField('paristech shool')
    paristechEntranceYear = wtf.TextField('paristech entrance year')
    domainChina = wtf.TextField('domain in China')
    domainFrance = wtf.TextField('domain in France')

    employer = wtf.TextField('employer')
