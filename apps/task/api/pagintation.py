from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.navigation.table_fields import tasks_table


class TaskPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):

        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'table_columns': tasks_table(self.request.user),
            'results': data,
        })
