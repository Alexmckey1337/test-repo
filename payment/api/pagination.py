from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from navigation.table_columns import get_table
from django.db.models import Sum
from payment.models import Currency


class PaymentPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    payments_sum = {}

    category = 'deal_payment'

    def get_columns(self):
        return get_table(self.category, self.request.user)

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'table_columns': self.get_columns(),
            'results': data,
            'payments_sum': self.payments_sum,
        })

    def paginate_queryset(self, queryset, request, view=None):
        for currency in Currency.objects.all():
            self.payments_sum[str(currency.code)] = queryset.filter(
                currency_sum__code=currency.code).aggregate(sum=Sum('sum'))

        return super(PaymentPagination, self).paginate_queryset(queryset, request, view)


class ChurchReportPaymentPagination(PaymentPagination):
    category = 'report_payment'
