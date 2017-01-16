# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin

from payment.models import Payment, Currency


class PaymentAdmin(admin.ModelAdmin):
    readonly_fields = ('effective_sum',)


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Currency)
