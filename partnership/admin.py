# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from partnership.admin_filters import PaidStatusFilter
from .models import Partnership, Deal, PartnerGroup


class PartnershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'value', 'responsible',)
    search_fields = ('user__first_name', 'user__last_name', 'user__middle_name')
    readonly_fields = ('user',)
    list_filter = ('responsible',)

    class Meta:
        model = Partnership


admin.site.register(Partnership, PartnershipAdmin)


class DealAdmin(admin.ModelAdmin):
    list_display = ('id', 'partnership', 'date_created', 'date', 'value', 'done',)
    search_fields = ('partnership__user__first_name', 'partnership__user__last_name', 'partnership__user__middle_name')
    readonly_fields = ('date_created', 'partnership')
    list_editable = ('done', 'value')
    list_filter = ('done', 'expired', 'date_created', 'partnership__responsible', PaidStatusFilter)

    actions = ['close', 'open']

    class Meta:
        model = Deal

    def close(self, request, queryset):
        queryset.update(done=True)

    close.short_description = _("Close selected deals")

    def open(self, request, queryset):
        queryset.update(done=False)

    open.short_description = _("Open selected deals")


admin.site.register(Deal, DealAdmin)
admin.site.register(PartnerGroup)
