from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from navigation.table_fields import meeting_table, meetings_summary_table


class MeetingPagination(PageNumberPagination):
    category = 'meetings'
    page_size = 30
    page_size_query_param = 'page_size'

    def get_columns(self):
        return meeting_table(self.request.user, self.category)

    def get_paginated_response(self, data):

        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'table_columns': self.get_columns(),
            'results': data,
        })


class ChurchReportPagination(MeetingPagination):
    category = 'church_report'


class MeetingVisitorsPagination(MeetingPagination):
    category = 'attends'


class MeetingSummaryPagination(MeetingPagination):
    category = 'meetings_summary'

    def get_columns(self):
        return meetings_summary_table(self.request.user, self.category)
