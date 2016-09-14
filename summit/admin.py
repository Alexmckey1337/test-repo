from django.contrib import admin
from models import SummitAnket, Summit, SummitType
from import_export.admin import ImportExportModelAdmin
from resources import SummitAnketResource


class SummitAnketAdmin(ImportExportModelAdmin):
    list_display = ('name', 'user', 'summit', 'code', )
    list_filter = ('summit', 'user__department', 'protected', )
    search_fields = ['code', 'user__last_name', ]
    resource_class = SummitAnketResource

    class Meta:
        model = SummitAnket


admin.site.register(SummitAnket, SummitAnketAdmin)
admin.site.register(Summit)
admin.site.register(SummitType)
