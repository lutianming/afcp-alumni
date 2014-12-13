from flask import request
from flask_admin.model import BaseModelView
from google.appengine.ext import ndb
from forms import MemberForm
from models import MemberModel

class NdbModelView(BaseModelView):
    can_create = True
    can_edit = True
    can_delete = True
    
    def get_pk_value(self, model):
        return model.key.urlsafe()

    def scaffold_list_columns(self):
        return self.model._properties

    def scaffold_sortable_columns(self):
        return None

    def scaffold_form(self):
        return MemberForm
    
    def get_list(self, page, sort_column, sort_desc, search, filters,
                 execute=True):
        return 1, self.model.query()

    def get_one(self, urlsafe):
        key = ndb.Key(urlsafe=urlsafe)
        return key.get()

    def edit_form(self, obj=None):
        form = super(NdbModel, self).edit_form(obj)
        if request.method == 'GET':
            form.fr.title.data = obj.meta['fr']['title']
            form.fr.content.data = obj.meta['fr']['content']
            form.zh.title.data = obj.meta['zh']['title']
            form.zh.content.data = obj.meta['zh']['content']
        return form

    def create_model(self, form):
        member = MemberModel(
            username=form.username.data,
            password=form.password.data,
            role='MEMBER',
            sex=form.sex.data,
            lastname=form.lastname.data,
            firstname=form.firstname.data,
            chinesename=form.chinesename.data,
            birthday=form.birthday.data,
            country=form.country.data,
            address=form.address.data,
            email=form.email.data,
            weibo=form.weibo.data,
            weixin=form.weixin.data,

            chineseUniversity=form.chineseUniversity.data,
            paristechSchool=form.paristechSchool.data,
            paristechEntranceYear=form.paristechEntranceYear.data,
            domainChina=form.domainChina.data,
            domainFrance=form.domainFrance.data,
        )
        member.put()
        return True
    
    def update_model(self, form, model):
        model.username = form.username.data,
        model.password = form.password.data,
        model.sex = form.sex.data,
        model.lastname = form.lastname.data,
        model.firstname = form.firstname.data,
        model.chinesename = form.chinesename.data,
        model.birthday = form.birthday.data,
        model.country = form.country.data,
        model.address = form.address.data,
        model.email = form.email.data,
        model.weibo = form.weibo.data,
        model.weixin = form.weixin.data,

        model.chineseUniversity = form.chineseUniversity.data,
        model.paristechSchool = form.paristechSchool.data,
        model.paristechEntranceYear = form.paristechEntranceYear.data,
        model.domainChina = form.domainChina.data,
        model.domainFrance = form.domainFrance.data,
        model.put()
        return True
    
    def delete_model(self, model):
        model.key.delete()
        return True

    
