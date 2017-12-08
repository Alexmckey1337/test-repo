from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.navigation.table_fields import group_table


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
            'table_columns': group_table(self.request.user, self.category),
            'results': data,
        })


class ChurchPagination(PaginationMixin):
    category = 'churches'


class HomeGroupPagination(PaginationMixin):
    category = 'home_groups'


class GroupUsersPagination(PaginationMixin):
    category = 'group_users'


class ForSelectPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 50


class PotentialUsersPagination(PageNumberPagination):
    page_size = 5
