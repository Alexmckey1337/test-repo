from django.contrib import admin
from models import Partnership, Deal


class PartnershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'value', 'responsible', )

    class Meta:
        model = Partnership

admin.site.register(Partnership, PartnershipAdmin)


class DealAdmin(admin.ModelAdmin):
    list_display = ('partnership', 'date', 'value', 'done', )

    class Meta:
        model = Deal

admin.site.register(Deal, DealAdmin)
