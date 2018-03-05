from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.navigation.table_columns import get_table


class ForSelectPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100


class TablePageNumberPagination(PageNumberPagination):
    table_name = ''
    table_param_name = 'table_columns'
    page_size = 30
    page_size_query_param = 'page_size'

    def get_columns(self):
        return getattr(self.request, 'columns', get_table(self.table_name, self.request.user.id))

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            self.table_param_name: self.get_columns(),
            'results': data,
        })
