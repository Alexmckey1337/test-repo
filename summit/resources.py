# -*- coding: utf-8
from __future__ import unicode_literals

from shutil import copyfile

from django.conf import settings
from import_export import resources

from hierarchy.models import Department
from .models import SummitAnket


class SummitAnketResource(resources.ModelResource):
    """For excel import/export"""

    class Meta:
        model = SummitAnket
        fields = (
            'id',
            'user__email', 'name', 'last_name', 'first_name', 'user__middle_name', 'user__born_date',
            'phone_number', 'code',
            'country', 'region', 'city', 'department', 'responsible', 'image',
            'pastor', 'bishop', 'sotnik', 'date',
        )
        export_order = (
            'id', 'user__email', 'name', 'last_name', 'first_name', 'user__middle_name',
            'user__born_date', 'phone_number', 'code',
            'country', 'region', 'city', 'department', 'responsible', 'image',
            'pastor', 'bishop', 'sotnik', 'date',
        )


def fill():
    i = 0
    ankets = SummitAnket.objects.filter(protected=False).all()
    for anket in ankets.all().order_by('id'):
        anket.name = anket.user.short
        summit_id = 4000000 + i
        summit_id_str = '0%i' % summit_id
        anket.code = summit_id_str
        anket.save()
        i += 1


def get_pastor(user):
    if user.hierarchy.level == 3:
        return user
        # print("%s, %s" % (user.short, user.hierarchy.level))
    if user.master:
        if user.master.hierarchy.level == 3:
            # print("got master %s, finish" % user.master.short)
            return user.master
        else:
            # print("got master %s, continue" % user.master.short)
            return get_pastor(user.master)
    else:
        # print("no master, stop")
        pass


def get_bishop(user):
    if user.hierarchy.level == 4:
        return user
    # print("%s, %s" % (user.short, user.hierarchy.level))
    if user.master:
        if user.master.hierarchy.level == 4:
            # print("got master %s, finish" % user.master.short)
            return user.master
        else:
            # print("got master %s, continue" % user.master.short)
            return get_bishop(user.master)
    else:
        # print("no master, stop")
        pass


def get_sot(user):
    if user.hierarchy.level == 2:
        return user
    # print("%s, %s" % (user.short, user.hierarchy.level))
    if user.master:
        if user.master.hierarchy.level == 2:
            # print("got master %s, finish" % user.master.short)
            return user.master
        else:
            # print("got master %s, continue" % user.master.short)
            return get_sot(user.master)
    else:
        return None


def find_pastor(anket):
    user = anket.user
    pastor = get_pastor(user)
    bishop = get_bishop(user)
    if pastor:
        anket.pastor = pastor.short
    else:
        anket.pastor = ""
    if bishop:
        anket.bishop = bishop.short
    else:
        anket.bishop = ""
    anket.date = user.date_joined
    anket.department = user.department.title
    anket.save()


def find_sot(anket):
    user = anket.user
    sot = get_sot(user)
    if sot:
        anket.sotnik = sot.short
    else:
        anket.sotnik = ''
    anket.save()


def get_fields(anket):
    d = Department.objects.get(id=2)
    anket.name = anket.user.short
    anket.country = anket.user.country
    anket.region = anket.user.region
    anket.phone_number = anket.user.phone_number
    anket.first_name = anket.user.first_name
    anket.last_name = anket.user.last_name
    anket.city = anket.user.city
    if not anket.code:
        summit_id = 4000000 + anket.id
        summit_id_str = '0%i' % summit_id
        anket.code = summit_id_str
    # print(anket.code)
    find_pastor(anket)
    find_sot(anket)
    if anket.pastor:
        anket.responsible = anket.pastor
    elif anket.sotnik:
        anket.responsible = anket.sotnik
    else:
        anket.responsible = anket.bishop
    if anket.user.department == d:
        anket.responsible = anket.bishop
    anket.image = "%s.jpg" % anket.code
    anket.save()


def doch():
    from hierarchy.models import Department
    d = Department.objects.get(id=2)
    ankets = SummitAnket.objects.filter(user__department=d).all()
    for anket in ankets:
        anket.responsible = anket.bishop
        anket.save()


def make_table():
    ankets = SummitAnket.objects.all()
    for anket in ankets.all().order_by('id'):
        get_fields(anket)
    print('OK')


def make_table_prt():
    ankets = SummitAnket.objects.filter(protected=True).all()
    for anket in ankets.all().order_by('id'):
        print(anket.code)
        find_pastor(anket)
        find_sot(anket)
        if anket.pastor:
            anket.responsible = anket.pastor
        elif anket.sotnik:
            anket.responsible = anket.sotnik
        else:
            anket.responsible = anket.bishop
        anket.image = "%s.jpg" % anket.code
        anket.save()
    print('OK')


def make_table_fix():
    ankets = SummitAnket.objects.all()
    for anket in ankets.all().order_by('id'):
        anket.name = anket.user.short
        anket.country = anket.user.country
        anket.region = anket.user.region
        anket.phone_number = anket.user.phone_number
        anket.save()
        print(anket.name)
    print('OK')


def check_images():
    ankets = SummitAnket.objects.all().order_by('id')[:2367]
    i = 0
    for anket in ankets.all():
        if not anket.user.image:
            i += 1
            print(anket.user.id)
    print(i)


def copy_images():
    ankets = SummitAnket.objects.all().order_by('id')
    destination_folder = '/summit_images/'
    for anket in ankets.all():
        if anket.user.image:
            path = anket.user.image.path
            if anket.code == '':
                pass
            else:
                destination = settings.MEDIA_ROOT + destination_folder + anket.code + '.jpg'
                copyfile(path, destination)
                print('copied %s' % anket.code)
