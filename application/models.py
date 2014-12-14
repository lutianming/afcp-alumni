"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb


class ExampleModel(ndb.Model):
    """Example Model"""
    example_name = ndb.StringProperty(required=True)
    example_description = ndb.TextProperty(required=True)
    added_by = ndb.UserProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)


class MemberModel(ndb.Model):
    username = ndb.StringProperty()
    password = ndb.StringProperty()
    role = ndb.StringProperty()
    
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
    paristech_entrance_year = ndb.StringProperty()
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
