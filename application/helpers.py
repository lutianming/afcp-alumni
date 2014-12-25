from models import MemberModel
import xlrd
import xlwt
import datetime
import re


columns = ['lastname', 'firstname', 'sex', 'chinesename',
           'birthday', 'paristech_entrance_year',
           'paristech_school', 'chinese_university',
           'scholarship', 'domain_france', 'domain_china',
           'other_diploma', 'diploma_school',
           'first_employer_country', 'internship',
           'first_employer', 'current_employer_country',
           'employer', 'email', 'phone', 'address_plus',
           'address', 'resident', 'weibo', 'weixin', 'remark']

def read_excel(content):
    book = xlrd.open_workbook(file_contents=content)
    members = []
    sheet = book.sheets()[0]

    china = set()
    paris = set()
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        #avoid duplicated user
        email = row[columns.index('email')]
        c = row[columns.index('chinese_university')]
        china.add(c)
        p = row[columns.index('paristech_school')]
        paris.add(p)
        if isinstance(email, float):
            email = str(int(email))

        if not email:
            continue

        #if member already exists, it will be overwrited
        member = MemberModel.query(MemberModel.email == email).get()
        if not member:
            member = MemberModel()
        if not member.role:
            member.role = 'MEMBER'
            
        for j, column in enumerate(columns):
            if hasattr(member, column):
                data = row[j]
                if not data:
                    continue
                set_column(member, column, data, book)
        members.append(member)
    return members


def write_excel(members, stream):
    book = xlwt.Workbook(encoding="utf8")
    sheet = book.add_sheet("members")

    date_style = xlwt.XFStyle()
    date_style.num_format_str = "dd/mm/yy"
    for i, col in enumerate(columns):
        row = 0
        sheet.write(row, i, col)
        for j, m in enumerate(members):
            if not hasattr(m, col):
                continue
            data = getattr(m, col)
            if col == "birthday":
                sheet.write(j+1, i, data, date_style)
            else:
                sheet.write(j+1, i, data)
    book.save(stream)
    return True
        
def set_column(member, column, data, book):
    if column == 'birthday':
        try:
            if isinstance(data, float):
                t = xlrd.xldate_as_tuple(data, book.datemode)
                date = datetime.date(t[0], t[1], t[2])
            else:
                tokens = re.findall('[0-9]+', data)
                if len(tokens) < 3:
                    return False
                day = int(tokens[0])
                month = int(tokens[1])
                year = int(tokens[2])
                date = datetime.date(year, month, day)
            setattr(member, column, date)
        except Exception as e:
            pass
    elif column == 'paristech_entrance_year':
        setattr(member, column, int(data))
    elif column in ['phone', 'weixin', 'address', 'email']:
        if isinstance(data, float):
            setattr(member, column, str(int(data)))
        else:
            setattr(member, column, data)
    else:
        setattr(member, column, data)
    return True
