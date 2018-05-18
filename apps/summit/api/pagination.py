from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.navigation.table_columns import get_table
from apps.payment.api.permissions import PaymentPermission
from apps.payment.api.serializers import CurrencySerializer
from apps.summit.models import Summit, SummitAnket


class SummitPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 30

    summit: Summit = None

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'table_columns': get_table('summit', self.request.user),
            'summit_currency': CurrencySerializer(self.summit.currency).data,
            'can_create_payment': PaymentPermission().has_object_permission(
                type('Request', (), {'user': self.request.user, 'method': 'POST'}),
                type('View', (), {'get_queryset': lambda: type('Queryset', (), {'model': SummitAnket})}),
                self.summit
            ),
            'summit_cost': {'full': self.summit.full_cost, 'special': self.summit.special_cost},
            'common_table': OrderedDict(),
            'results': data
        })

    def paginate_queryset(self, queryset, request, view=None):
        self.summit = view.summit
        return super().paginate_queryset(queryset, request, view)


class SummitStatisticsPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 30

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'table_columns': get_table('summit_stats', self.request.user),
            'common_table': OrderedDict(),
            'results': data
        })


class SummitTicketPagination(PageNumberPagination):
    page_size = 20000
    page_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'ticket_count': self.page.paginator.count,
            'ticket_codes': data
        })


class SummitSearchPagination(PageNumberPagination):
    page_size = 5
