# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin

from .models import Partnership, Deal


class PartnershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'value', 'responsible',)
    search_fields = ('user__first_name', 'user__last_name', 'user__middle_name')
    readonly_fields = ('user',)
    list_filter = ('level', 'responsible')

    class Meta:
        model = Partnership


admin.site.register(Partnership, PartnershipAdmin)


class DealAdmin(admin.ModelAdmin):
    list_display = ('partnership', 'date_created', 'date', 'value', 'done',)
    search_fields = ('partnership__user__first_name', 'partnership__user__last_name', 'partnership__user__middle_name')
    readonly_fields = ('date_created', 'partnership')
    list_editable = ('done', 'value')
    list_filter = ('done', 'expired', 'date_created', 'partnership__responsible')

    class Meta:
        model = Deal


admin.site.register(Deal, DealAdmin)
