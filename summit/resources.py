# -*- coding: utf-8
from import_export import resources
from account.models import CustomUser as User
from models import SummitAnket


class SummitAnketResource(resources.ModelResource):
    """For excel import/export"""
    class Meta:
        model = SummitAnket
        #fields = ('id', 'username', 'last_name', 'first_name', 'middle_name',
        #          'email', 'phone_number', 'skype', 'country', 'city', 'address',
        #          'born_date', 'facebook', 'vkontakte', 'description',
        #          'department', 'hierarchy', 'master')
        exclude = ('id', 'user', 'summit', 'value', 'description', )
        export_order = ('last_name', 'first_name', 'code', 'pastor', 'bishop', 'date', 'department', )
        #                'email', 'phone_number', 'skype', 'country', 'city', 'address',
        #                'born_date', 'facebook', 'vkontakte', 'description',
        #                'department', 'hierarchy', 'master')



def fill():
    i = 0
    ankets = SummitAnket.objects.all()
    for anket in ankets.all().order_by('id'):
        anket.name = anket.user.short
        summit_id = 2000000 + i
        summit_id_str = '0%i' % summit_id
        anket.code = summit_id_str
        anket.save()
        i += 1

def get_pastor(user):
    if user.hierarchy.level == 3:
        return user      
    #print "%s, %s" % (user.short, user.hierarchy.level)
    if user.master:
        if user.master.hierarchy.level == 3:
            #print "got master %s, finish" % user.master.short
            return user.master
        else:
            #print "got master %s, continue" % user.master.short
            return get_pastor(user.master)
    else:
        #print "no master, stop"
        pass


def get_bishop(user):
    if user.hierarchy.level == 4:
        return user
    #print "%s, %s" % (user.short, user.hierarchy.level)
    if user.master:
        if user.master.hierarchy.level == 4:
            #print "got master %s, finish" % user.master.short
            return user.master
        else:
            #print "got master %s, continue" % user.master.short
            return get_bishop(user.master)
    else:
        #print "no master, stop"
        pass




def find_pastor(anket):
    user = anket.user
    pastor = get_pastor(user)
    bishop = get_bishop(user)
    if pastor:
        anket.pastor = pastor.short
    if bishop:
        anket.bishop = bishop.short
    anket.date = user.date_joined
    anket.department = user.department.title
    anket.save()


def make_table():
    i = 0
    ankets = SummitAnket.objects.all()
    for anket in ankets.all().order_by('id'):
        anket.name = anket.user.short
        anket.first_name = anket.user.first_name
        anket.last_name = anket.user.last_name
        summit_id = 2000000 + i
        summit_id_str = '0%i' % summit_id
        i += 1
        anket.code = summit_id_str
        find_pastor(anket) 
    print 'OK'  



from shutil import copyfile
from edem.settings import MEDIA_ROOT

def check_images():
    ankets = SummitAnket.objects.all().order_by('id')[:1000]
    i = 0
    for anket in ankets.all():
        if not anket.user.image:
            i += 1
            print anket.user.id
    print i
            


def copy_images():
    ankets = SummitAnket.objects.all().order_by('id')[:1000]
    destination_folder = '/summit_images/'
    for anket in ankets.all():
        if anket.user.image: 
            path = anket.user.image.path
            destination = MEDIA_ROOT + destination_folder + anket.code + '.jpg'
            copyfile(path, destination)
            print 'copied %s' % anket.code
