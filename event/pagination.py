from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from group.pagination import PaginationMixin
from navigation.table_fields import meeting_table


class MeetingPagination(PageNumberPagination):
    category = 'meetings'
    page_size = 30
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'table_columns': meeting_table(self.request.user, self.category),
            'results': data,
        })


class ChurchReportPagination(PaginationMixin):
    category = 'church_reports'
