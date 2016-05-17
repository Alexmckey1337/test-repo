# -*- coding: utf-8
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import ugettext_lazy as _
from models import CustomUser
from django.contrib.auth.forms import AdminPasswordChangeForm
from import_export.admin import ImportExportModelAdmin
from resources import UserResource


class CustomUserChangeForm(UserChangeForm):
    password = ReadOnlyPasswordHashField(label=_("Password"))

    def clean_password(self):
        return self.initial["password"]

    class Meta:
        model = CustomUser
        fields = "__all__"


class CustomUserAdmin(UserAdmin, ImportExportModelAdmin):
    form = CustomUserChangeForm
    list_display = ('username', 'date_joined',
                    'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'email', 'first_name', 'last_name', 'middle_name', 'master', 'department', 'hierarchy',
            'phone_number', 'skype', 'facebook', 'vkontakte', 'image', 'born_date',
            'country', 'city', 'address',
            'description',
            )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups',)}),
    )
    change_password_form = AdminPasswordChangeForm
    resource_class = UserResource

admin.site.unregister(User)
admin.site.register(CustomUser, CustomUserAdmin)

