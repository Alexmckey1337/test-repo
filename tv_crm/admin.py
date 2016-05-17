from django.contrib import admin
from models import LastCall, Synopsis


class LastCallAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', )

    class Meta:
        model = LastCall

admin.site.register(LastCall, LastCallAdmin)
admin.site.register(Synopsis)
