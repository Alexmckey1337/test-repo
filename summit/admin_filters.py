from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class HasTicketListFilter(admin.SimpleListFilter):
    title = _('Has ticket?')

    parameter_name = 'has_ticket'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(ticket__isnull=False)
        if self.value() == 'no':
            return queryset.filter(ticket__isnull=True)


class HasEmailListFilter(admin.SimpleListFilter):
    title = _('Has email?')

    parameter_name = 'has_email'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(emails__isnull=False)
        if self.value() == 'no':
            return queryset.filter(emails__isnull=True)
