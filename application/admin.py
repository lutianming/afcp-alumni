from flask import request, flash, redirect, url_for
from flask_admin import BaseView, expose
from flask_admin.model import BaseModelView
from flask_admin.model.helpers import get_mdict_item_or_list
from google.appengine.ext import ndb
from google.appengine.api import search, mail
from forms import MemberForm
from models import MemberModel
import xlrd
import datetime
import re
import random


def create_document(member):
    document = search.Document(
        doc_id=member.key.urlsafe(),
        fields=[
            search.TextField(name='name',
                             value=member.lastname+' '+member.firstname),
            search.TextField(name='chinesename',
                             value=member.chinesename),
            search.TextField(name='email',
                             value=member.email)
            ]
        )
    return document


def update_member(member):
    member.put()
    document = create_document(member)
    index = search.Index(name='members')
    index.put(document)

    
class NdbModelView(BaseModelView):
    can_create = True
    can_edit = True
    can_delete = True

    list_template = 'admin/model/member_list_template.html'
    column_list = ['email', 'lastname', 'firstname', 'chinesename', 'role', 'last_login']
    column_searchable_list = ('lastname', 'firstname',
                              'chinesename', 'email')
    # column_filters = ('lastname', 'firstname')
    page_size = 20
    
    def get_pk_value(self, model):
        return model.key.urlsafe()

    def scaffold_sortable_columns(self):
        return None

    def scaffold_form(self):
        return MemberForm

    def init_search(self):
        return True
    
    def get_list(self, page, sort_column, sort_desc, search, filters,
                 execute=True):
        print(page, sort_column, sort_desc, search, filters)
        if search:
            query = self.model.query(ndb.OR(self.model.lastname == search,
                                            self.model.firstname == search,
                                            self.model.email == search))
        else:
            query = self.model.query()
            
        if page is not None:
            result = query.fetch(self.page_size,
                                 offset=page*self.page_size)
        else:
            result = query.fetch(self.page_size)
            
        return query.count(), result

    def get_one(self, urlsafe):
        key = ndb.Key(urlsafe=urlsafe)
        return key.get()

    def create_model(self, form):
        member = MemberModel(
            role=form.role.data,
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
        update_member(member)
        return True
    
    def update_model(self, form, model):
        model.role = form.role.data
        model.sex = form.sex.data
        model.lastname = form.lastname.data
        model.firstname = form.firstname.data
        model.chinesename = form.chinesename.data
        model.birthday = form.birthday.data
        model.country = form.country.data
        model.address = form.address.data
        model.email = form.email.data
        model.weibo = form.weibo.data
        model.weixin = form.weixin.data

        model.chinese_university = form.chinese_university.data
        model.paristech_school = form.paristech_school.data
        model.paristech_entrance_year = form.paristech_entrance_year.data
        model.domain_china = form.domain_china.data
        model.domain_france = form.domain_france.data
        update_member(model)
        return True
    
    def delete_model(self, model):
        index = search.Index(name='members')
        index.delete(model.key.urlsafe())
        model.key.delete()
        return True

    @expose('/upload/', methods=['GET', 'POST'])
    def upload(self):
        for k, f in request.files.items():
            book = xlrd.open_workbook(file_contents=f.read())
            sheet = book.sheets()[0]
            columns = ['lastname', 'firstname', 'sex', 'chinesename',
                       'birthday', 'paristech_entrance_year',
                       'paristech_school', 'chinese_university',
                       'scholarship', 'domain_france', 'domain_china',
                       'other_diploma', 'diploma_school',
                       'first_employer_country', 'internship',
                       'first_employer', 'current_employer_country',
                       'employer', 'email', 'phone', 'address_plus',
                       'address', 'resident', 'weibo', 'weixin', 'remark']
            count = 0
            for i in range(1, sheet.nrows):
                print(i)
                row = sheet.row_values(i)
                #avoid duplicated user
                email = row[columns.index('email')]
                if isinstance(email, float):
                    email = str(int(email))

                if not email or MemberModel.query(MemberModel.email == email).get():
                    continue

                member = MemberModel()
                for j, column in enumerate(columns):
                    if hasattr(member, column):
                        data = row[j]
                        print(column, data)
                        
                        if not data:
                            continue
                        
                        if column == 'birthday':
                            try:
                                if isinstance(data, float):
                                    t = xlrd.xldate_as_tuple(data, book.datemode)
                                    date = datetime.date(t[0], t[1], t[2])
                                else:
                                    tokens = re.findall('[0-9]+', data)
                                    if len(tokens) < 3:
                                        continue
                                        day = int(tokens[0])
                                        month = int(tokens[1])
                                        year = int(tokens[2])
                                        date = datetime.date(year, month, day)
                                        setattr(member, column, date)
                            except Exception as e:
                                pass
                        elif column == 'paristech_entrance_year':
                            setattr(member, column, int(data))
                        elif column == 'phone':
                            if isinstance(data, float):
                                setattr(member, column, str(int(data)))
                            else:
                                setattr(member, column, data)
                        elif column == 'weixin':
                            if isinstance(data, float):
                                setattr(member, column, str(int(data)))
                            else:
                                setattr(member, column, data)
                        elif column == 'address':
                            if isinstance(data, float):
                                setattr(member, column, str(int(data)))
                            else:
                                setattr(member, column, data)
                        elif column == 'email':
                            if isinstance(data, float):
                                setattr(member, column, str(int(data)))
                            else:
                                setattr(member, column, data)
                        else:
                            setattr(member, column, data)
                update_member(member)
                count += 1
        flash('imported {0} members'.format(count))
        return redirect(url_for('members.index_view'))

    @expose('/invite/', methods=('GET', 'POST'))
    def invite(self):
        id = get_mdict_item_or_list(request.args, 'id')
        member = self.get_one(id)
        self._invite(member)

        flash('invitation sent')
        return redirect(url_for('members.index_view'))


    @expose('/inviteall')
    def inviteall(self):
        members = MemberModel.query(MemberModel.last_login == None)
        for member in members:
            self._invite(member)
        flash('invitations sent')
        
        return redirect(url_for('members.index_view'))
        
    def _invite(self, member):
        password = gen_password()
        print(password)
        sender = 'admin@afcp-alumni.com'

        member.password = password
        member.put()
            
        message = mail.EmailMessage(sender=sender)
        message.to = member.email
        message.subject = "invitation of AFCP Alumni"
        message.body = """
        username: {0}
        password: {1}
        """.format(member.email, password)
        message.send()
        return True

    
def gen_password(length=6):
    password = ""
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    l = len(alphabet)
    for i in range(length):
        index = random.randrange(l)
        password += alphabet[index]
    return password
    
