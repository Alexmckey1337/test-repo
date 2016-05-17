from django.contrib import admin
from models import Status


class StatusAdmin(admin.ModelAdmin):
    list_display = ('title', )

    class Meta:
        model = Status

admin.site.register(Status, StatusAdmin)
