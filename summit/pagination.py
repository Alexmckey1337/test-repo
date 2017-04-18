from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from navigation.table_fields import summit_table, user_table


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
            'common_table': summit_table(),
            'user_table': user_table(self.request.user, prefix_ordering_title='user__'),
            'results': data
        })
