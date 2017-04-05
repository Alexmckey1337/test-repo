from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from navigation.table_fields import partner_table, user_table
from partnership.permissions import CanCreatePartnerPayment, CanClosePartnerDeal


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
            'common_table': partner_table(self.request.user),
            'user_table': user_table(self.request.user, prefix_ordering_title='user__'),
            'results': data
        })


class DealPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 30

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('check_payment_permissions', CanCreatePartnerPayment().has_permission(self.request, None)),
            ('can_close_deal', CanClosePartnerDeal().has_permission(self.request, None)),
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))