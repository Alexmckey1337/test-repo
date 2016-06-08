from django.contrib import admin
from models import SummitAnket, Summit, SummitType
from import_export.admin import ImportExportModelAdmin
from resources import SummitAnketResource


class SummitAnketAdmin(ImportExportModelAdmin):
    list_display = ('user', 'summit', )
    list_filter = ('summit', )
    resource_class = SummitAnketResource

    class Meta:
        model = SummitAnket


admin.site.register(SummitAnket, SummitAnketAdmin)
admin.site.register(Summit)
admin.site.register(SummitType)
