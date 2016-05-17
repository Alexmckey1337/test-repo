# -*- coding: utf-8
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from models import CustomUser
from django.contrib.auth.forms import AdminPasswordChangeForm
from import_export.admin import ImportExportModelAdmin
from resources import UserResource


class CustomUserAdmin(UserAdmin, ImportExportModelAdmin):

    list_display = ('username', 'date_joined',
                    'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'email', 'first_name', 'last_name', 'middle_name', 'master', 'department', 'hierarchy',
            'phone_number', 'skype', 'facebook', 'vkontakte', 'image', 'born_date',
            'country', 'region', 'city', 'district', 'address',
            'description', 'repentance_date', 'coming_date', 'hierarchy_order',
            )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups',)}),
    )
    change_password_form = AdminPasswordChangeForm
    resource_class = UserResource

admin.site.unregister(User)
admin.site.register(CustomUser, CustomUserAdmin)

