from django.contrib import admin
from django.db.models import Sum, F
from django.utils.translation import ugettext_lazy as _


class PaidStatusFilter(admin.SimpleListFilter):
    title = _('Paid status')

    parameter_name = 'paid_status'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Paid')),
            ('partial', _('Partial paid')),
            ('no', _('Unpaid')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.annotate(s=Sum('payments__sum')).filter(payments__isnull=False, s__gte=F('value'))
        if self.value() == 'partial':
            return queryset.annotate(s=Sum('payments__sum')).filter(payments__isnull=False, s__lt=F('value'))
        if self.value() == 'no':
            return queryset.annotate(s=Sum('payments__sum')).filter(payments__isnull=True)
