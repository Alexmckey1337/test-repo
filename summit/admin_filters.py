from decimal import Decimal

from django.contrib import admin
from django.db.models import Sum
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
            ids = queryset.filter(emails__isnull=False).values_list('id', flat=True)
            return queryset.filter(id__in=ids)
        if self.value() == 'no':
            return queryset.filter(emails__isnull=True)


# TODO very slow
class PaidStatusListFilter(admin.SimpleListFilter):
    title = _('Paid?')

    parameter_name = 'paid'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
            ('partial', _('Partial')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            ids = [a.id for a in queryset if a.is_full_paid]
            return queryset.filter(id__in=ids)
        if self.value() == 'no':
            ids = [a.id for a in queryset if not a.is_full_paid]
            return queryset.filter(id__in=ids)
        if self.value() == 'partial':
            ids = [a.id for a in queryset.annotate(
                total_sum=Sum('payments__effective_sum')).filter(total_sum__gt=Decimal(0)) if not a.is_full_paid]
            return queryset.filter(id__in=ids)
