from django.contrib import admin
from models import Notification, NotificationTheme


class NotificationThemeAdmin(admin.ModelAdmin):
    list_display = ('title', )

    class Meta:
        model = NotificationTheme

admin.site.register(NotificationTheme, NotificationThemeAdmin)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('theme', 'date', 'user', 'system', 'common', )

    class Meta:
        model = Notification

admin.site.register(Notification, NotificationAdmin)
