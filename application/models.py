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
    username = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    role = ndb.StringProperty(required=True)
    
    sex = ndb.StringProperty(required=True)
    lastname = ndb.StringProperty(required=True)
    firstname = ndb.StringProperty(required=True)
    chinesename = ndb.StringProperty()
    birthday = ndb.DateProperty()
    country = ndb.StringProperty()
    address = ndb.StringProperty()
    email = ndb.StringProperty(required=True)
    weibo = ndb.StringProperty()
    weixin = ndb.StringProperty()
    phone = ndb.StringProperty()
    
    chineseUniversity = ndb.StringProperty(required=True)
    paristechSchool = ndb.StringProperty(required=True)
    paristechEntranceYear = ndb.StringProperty(required=True)
    domainChina = ndb.StringProperty()
    domainFrance = ndb.StringProperty()
    employer = ndb.StringProperty()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.key.id())
