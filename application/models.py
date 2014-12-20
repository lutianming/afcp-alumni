"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb


class MemberModel(ndb.Model):
    password = ndb.StringProperty()
    role = ndb.StringProperty()
    last_login = ndb.DateTimeProperty()
    
    sex = ndb.StringProperty()
    lastname = ndb.StringProperty()
    firstname = ndb.StringProperty()
    chinesename = ndb.StringProperty()
    birthday = ndb.DateProperty()
    country = ndb.StringProperty()
    address = ndb.StringProperty()
    email = ndb.StringProperty()
    weibo = ndb.StringProperty()
    weixin = ndb.StringProperty()
    phone = ndb.StringProperty()
    
    chinese_university = ndb.StringProperty()
    paristech_school = ndb.StringProperty()
    paristech_entrance_year = ndb.IntegerProperty()
    domain_china = ndb.StringProperty()
    domain_france = ndb.StringProperty()
    employer = ndb.StringProperty()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.key.id())
