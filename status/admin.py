from django.contrib import admin
from models import Status, Division


class StatusAdmin(admin.ModelAdmin):
    list_display = ('title', )

    class Meta:
        model = Status

admin.site.register(Status, StatusAdmin)


class DivisionAdmin(admin.ModelAdmin):
    list_display = ('title', )

    class Meta:
        model = Division

admin.site.register(Division, DivisionAdmin)