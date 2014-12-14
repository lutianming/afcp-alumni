from flask import request, flash
from flask_admin import BaseView, expose
from flask_admin.model import BaseModelView
from google.appengine.ext import ndb
from forms import MemberForm
from models import MemberModel
import xlrd


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
        form = super(NdbModelView, self).edit_form(obj)
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

            chinese_university=form.chinese_university.data,
            paristech_school=form.paristech_school.data,
            paristech_entrance_year=form.paristech_entrance_year.data,
            domain_china=form.domain_china.data,
            domain_france=form.domain_france.data,
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

    
class FileView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/file.html')

    @expose('/upload')
    def upload(self):
        file = request.files[0]
        data = xlrd.open_workbook(file)
        sheet = data.sheets()[0]
        columns = ['lastname', 'firstname', 'sex', 'chinesename',
                   'birthday', 'paristech_entrance_year',
                   'paristech_school', 'chinese_university',
                   'scholarship', 'domain_france', 'domain_china',
                   'other_diploma', 'diploma_school',
                   'first_employer_country', 'internship',
                   'first_employer', 'current_employer_country',
                   'employer', 'email', 'phone', 'address_plus',
                   'address', 'resident', 'weibo', 'weixin', 'remark']
        for i in range(1, sheet.nrows):
            row = sheet.row_values(i)
            member = MemberModel()
            for i, v in enumerate(columns):
                if hasattr(member, v):
                    setattr(member, v, row[i])
            member.put()
        flash('uploaded')
        return self.render('admin/file.html')
        
