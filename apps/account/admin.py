from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportExportModelAdmin

from apps.account.models import CustomUser, UserMarker, MessengerType, UserMessenger, Token
from apps.account.resources import UserResource


class CustomUserAdmin(UserAdmin, ImportExportModelAdmin):
    list_display = ('fullname', 'username', 'email', 'date_joined',
                    'is_staff', 'is_active', 'can_login')
    list_display_links = ('fullname', 'username')
    list_editable = ('is_active', 'can_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'can_login', 'groups', 'departments',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'email', 'first_name', 'last_name', 'middle_name', 'search_name', 'master', 'departments', 'hierarchy',
            'spiritual_level', 'phone_number', 'extra_phone_numbers', 'skype', 'facebook', 'vkontakte', 'image',
            'born_date', 'country', 'region', 'city', 'district', 'address',
            'locality',
            'description', 'repentance_date', 'coming_date', 'marker',
        )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'can_login', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups',)}),
        (_('Home group'), {'fields': ('hhome_group', )})
    )
    readonly_fields = ('master',)
    autocomplete_fields = ('locality',)
    search_fields = ('first_name', 'last_name', 'middle_name')
    change_password_form = AdminPasswordChangeForm
    resource_class = UserResource


class UserMessengerAdmin(admin.ModelAdmin):
    list_display = ('user', 'messenger', 'value', 'display_position')
    list_editable = ('value', 'display_position')
    # readonly_fields = ('user',)
    autocomplete_fields = ('user',)


class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created')
    # readonly_fields = ('user',)


class MessengerTypeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'title', 'code', 'display_position')
    list_editable = ('title', 'code', 'display_position')


admin.site.unregister(User)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserMarker)
admin.site.register(UserMessenger, UserMessengerAdmin)
admin.site.register(MessengerType, MessengerTypeAdmin)
admin.site.register(Token, UserTokenAdmin)
