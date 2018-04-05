from django.contrib import admin

from apps.payment.models import Payment, Currency


class PaymentAdmin(admin.ModelAdmin):
    readonly_fields = ('effective_sum',)
    list_display = ('__str__', 'manager', 'sum', 'effective_sum', 'sent_date', 'created_at')
    search_fields = ('manager__last_name', 'sum')


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Currency)
