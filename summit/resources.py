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
        #export_order = ('id', 'username', 'last_name', 'first_name', 'middle_name',
        #                'email', 'phone_number', 'skype', 'country', 'city', 'address',
        #                'born_date', 'facebook', 'vkontakte', 'description',
        #                'department', 'hierarchy', 'master')



def fill():
    ankets = SummitAnket.objects.all()
    for anket in ankets.all():
        anket.name = anket.user.short_fullname
        summit_id = 2000000 + anket.id
        summit_id_str = '0%i' % summit_id
        anket.code = summit_id_str
        anket.save()