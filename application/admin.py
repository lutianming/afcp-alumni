from flask import request, flash, redirect, url_for, make_response
from flask_admin import expose
from flask_admin.model import BaseModelView
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_login import current_user
from google.appengine.ext import ndb
from google.appengine.api import search, mail
from forms import MemberForm
from models import MemberModel
from helpers import read_excel, write_excel
import random
import StringIO


def create_document(member):
    document = search.Document(
        doc_id=member.key.urlsafe(),
        fields=[
            search.TextField(name='name',
                             value=member.lastname+' '+member.firstname),
            search.TextField(name='chinesename',
                             value=member.chinesename),
            search.TextField(name='email',
                             value=member.email),
            search.TextField(name='chinese_university',
                             value=member.chinese_university),
            search.TextField(name='paristech_school',
                             value=member.paristech_school),
            search.NumberField(name='paristech_entrance_year',
                               value=member.paristech_entrance_year)
            ]
        )
    return document


def update_document(member):
    document = create_document(member)
    index = search.Index(name='members')
    index.put(document)

    
class NdbModelView(BaseModelView):
    can_create = True
    can_edit = True
    can_delete = True

    list_template = 'admin/model/member_list_template.html'
    column_list = ['email', 'lastname', 'firstname', 'chinesename',
                   'chinese_university', 'paristech_school',
                   'paristech_entrance_year',
                   'role', 'last_login']
    column_sortable_list = ['email', 'lastname', 'firstname',
                            'chinesename',
                            'chinese_university', 'paristech_school',
                            'paristech_entrance_year']
    column_searchable_list = ['lastname', 'firstname',
                              'chinesename', 'email',
                              'paristech_entrance_year']
    # column_filters = ('lastname', 'firstname')
    page_size = 20
    def is_accessible(self):
        return current_user.is_authenticated() and current_user.role == 'ADMIN'
    
    def get_pk_value(self, model):
        return model.key.urlsafe()

    def scaffold_sortable_columns(self):
        return None

    def scaffold_form(self):
        return MemberForm

    def init_search(self):
        return True
    
    def get_list(self, page, sort_column, sort_desc,
                 search_string, filters, execute=True):
        if sort_column:
            if sort_desc:
                direction = search.SortExpression.DESCENDING
            else:
                direction = search.SortExpression.ASCENDING
            expr = search.SortExpression(expression=sort_column,
                                         direction=direction)
            sort_options = search.SortOptions(expressions=[expr])
        else:
            sort_options = None
            
        if page is None:
            page = 0
        index = search.Index(name='members')
        options = search.QueryOptions(limit=self.page_size,
                                      offset=page*self.page_size,
                                      sort_options=sort_options,
                                      number_found_accuracy=1000)

        if search_string:
            query = search.Query(query_string=search_string,
                                 options=options)
        else:
            query = search.Query(query_string='',
                                 options=options)
        result = index.search(query)
        
        count = result.number_found
        keys = []

        for r in result.results:
            key = ndb.Key(urlsafe=r.doc_id)
            keys.append(key)

        members = ndb.get_multi(keys)
        print(count)
        return count, members

    def get_one(self, urlsafe):
        key = ndb.Key(urlsafe=urlsafe)
        return key.get()

    def create_model(self, form):
        member = MemberModel()
        return self.update_model(form, member)
    
    def update_model(self, form, model):
        for field in form:
            setattr(model, field.name, field.data)

        model.put()
        update_document(model)
        return True
    
    def delete_model(self, model):
        index = search.Index(name='members')
        index.delete(model.key.urlsafe())
        model.key.delete()
        return True

    @expose('/upload/', methods=['GET', 'POST'])
    def upload(self):
        for k, f in request.files.items():
            members = read_excel(f.read())
            ndb.put_multi(members)
            for member in members:
                update_document(member)

        flash('updated {0} members'.format(len(members)))
        return redirect(url_for('members.index_view'))

    @expose('/download/')
    def download(self):
        members = MemberModel.query()
        output = StringIO.StringIO()
        write_excel(list(members), output)

        filename = "members.xlsx"
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename={0}".format(filename)
        output.close()
        return response
    
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
        sender = 'lutianming1005@gmail.com'

        member.password = password
        member.put()
            
        message = mail.EmailMessage(sender=sender)
        message.to = member.email
        message.subject = "invitation from AFCP Alumni"
        message.body = """
        The site of AFCP Alumni(http://afcp-alumni.appspot.com/) is under testing.
        Please use the following usename and password to login
        username: {0}
        password: {1}
        If you have any advice or find any bug, contact me please.
        Thank you!

        Regards!
        Tianming
        """.format(member.email, password)
        message.send()
        return True

    @expose('/reindex')
    def reindex(self):
        members = MemberModel.query()
        for member in members:
            update_document(member)
        flash('all members reindexed')
        return redirect(url_for('members.index_view'))
    
def gen_password(length=6):
    password = ""
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    l = len(alphabet)
    for i in range(length):
        index = random.randrange(l)
        password += alphabet[index]
    return password
    
