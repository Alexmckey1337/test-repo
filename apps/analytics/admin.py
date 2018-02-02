from django.contrib import admin

from apps.analytics.models import LogRecord


class LogRecordAdmin(admin.ModelAdmin):
    autocomplete_fields = ('user',)


admin.site.register(LogRecord, LogRecordAdmin)
