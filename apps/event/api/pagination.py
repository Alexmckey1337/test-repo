from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.navigation.table_columns import get_table


class MeetingPagination(PageNumberPagination):
    category = 'meeting'
    page_size = 30
    page_size_query_param = 'page_size'
    statistics = {}

    def get_columns(self):
        return get_table(self.category, self.request.user.id)

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


class MeetingWithoutColumnPagination(PageNumberPagination):
    category = 'meeting'
    page_size = 30
    page_size_query_param = 'page_size'
    statistics = {}
    def get_paginated_response(self, data):

        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data,
        })


class ChurchReportPagination(MeetingPagination):
    category = 'church_report'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'check_report_permissions': self.request.user.can_create_partner_payments(),
            'count': self.page.paginator.count,
            'table_columns': self.get_columns(),
            'results': data,
        })


class MeetingVisitorsPagination(MeetingPagination):
    category = 'attend'
    page_size = 1000


class MeetingSummaryPagination(MeetingPagination):
    category = 'meeting_summary'


class ReportsSummaryPagination(MeetingPagination):
    category = 'report_summary'
