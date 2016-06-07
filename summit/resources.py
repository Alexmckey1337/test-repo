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
        exclude = ('user_ptr', 'password', 'last_login', 'is_superuser', 'groups', 'user_permissions', 'is_staff',
                   'is_active', 'date_joined', 'image', 'hierarchy_order',)
        #export_order = ('id', 'username', 'last_name', 'first_name', 'middle_name',
        #                'email', 'phone_number', 'skype', 'country', 'city', 'address',
        #                'born_date', 'facebook', 'vkontakte', 'description',
        #                'department', 'hierarchy', 'master')
