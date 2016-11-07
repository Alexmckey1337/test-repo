# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin

from .models import Partnership, Deal


class PartnershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'value', 'responsible',)
    search_fields = ('user__first_name', 'user__last_name', 'user__middle_name')

    class Meta:
        model = Partnership


admin.site.register(Partnership, PartnershipAdmin)


class DealAdmin(admin.ModelAdmin):
    list_display = ('partnership', 'date_created', 'date', 'value', 'done',)
    search_fields = ('partnership__user__first_name', 'partnership__user__last_name', 'partnership__user__middle_name')
    readonly_fields = ('date_created',)
    list_editable = ('done', 'value')

    class Meta:
        model = Deal


admin.site.register(Deal, DealAdmin)
