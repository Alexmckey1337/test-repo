from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from navigation.table_fields import payment_table


class PaymentPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'table_columns': payment_table(self.request.user),
            'results': data,
        })
