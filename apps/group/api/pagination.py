from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.navigation.table_columns import get_table


class PaginationMixin(PageNumberPagination):
    category = None
    page_size = 30
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        assert self.category is not None, 'Not Category selected'
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'table_columns': getattr(self.request, 'columns', get_table(self.category, self.request.user.id)),
            'results': data,
        })


class ChurchPagination(PaginationMixin):
    category = 'church'


class HomeGroupPagination(PaginationMixin):
    category = 'home_group'


class GroupUsersPagination(PaginationMixin):
    category = 'group_user'


class ForSelectPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 50


class PotentialUsersPagination(PageNumberPagination):
    page_size = 5
