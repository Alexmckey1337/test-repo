from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from navigation.table_fields import summit_table, summit_statistics_table


class SummitPagination(PageNumberPagination):
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
            'user_table': summit_table(self.request.user),
            'common_table': OrderedDict(),
            'results': data
        })


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
            'user_table': summit_statistics_table(),
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
