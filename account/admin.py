# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from mptt.admin import MPTTModelAdmin

from .models import CustomUser
from .resources import UserResource


class CustomUserAdmin(UserAdmin, MPTTModelAdmin, ImportExportModelAdmin):
    list_display = ('fullname', 'username', 'email', 'date_joined',
                    'is_staff', 'is_active')
    list_display_links = ('fullname', 'username')
    list_editable = ('is_active',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'departments',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'email', 'first_name', 'last_name', 'middle_name', 'search_name', 'master', 'departments', 'hierarchy',
            'phone_number', 'extra_phone_numbers', 'skype', 'facebook', 'vkontakte', 'image', 'born_date',
            'country', 'region', 'city', 'district', 'address',
            'description', 'repentance_date', 'coming_date',
        )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups',)}),
    )
    change_password_form = AdminPasswordChangeForm
    resource_class = UserResource


admin.site.unregister(User)
admin.site.register(CustomUser, CustomUserAdmin)
