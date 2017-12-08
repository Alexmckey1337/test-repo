from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from navigation.table_columns import get_table


class PartnershipPagination(PageNumberPagination):
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
            'table_columns': get_table('partner', self.request.user.id),
            'results': data
        })


class ChurchPartnerPagination(PageNumberPagination):
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
            'table_columns': get_table('church_partner', self.request.user.id),
            'results': data
        })


class DealPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 30

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('check_payment_permissions', self.request.user.can_create_partner_payments()),
            ('can_close_deal', self.request.user.can_close_partner_deals()),
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('table_columns', get_table('deal', self.request.user.id)),
            ('results', data)
        ]))


class ChurchDealPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 30

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('check_payment_permissions', self.request.user.can_create_church_partner_payments()),
            ('can_close_deal', self.request.user.can_close_church_partner_deals()),
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('table_columns', get_table('deal', self.request.user.id)),
            ('results', data)
        ]))


class DealDuplicatePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 5
