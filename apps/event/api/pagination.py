from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.navigation.table_fields import meeting_table, meetings_summary_table, reports_summary_table


class MeetingPagination(PageNumberPagination):
    category = 'meetings'
    page_size = 30
    page_size_query_param = 'page_size'
    statistics = {}

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
    category = 'attends'


class MeetingSummaryPagination(MeetingPagination):
    category = 'meetings_summary'

    def get_columns(self):
        return meetings_summary_table(self.request.user, self.category)


class ReportsSummaryPagination(MeetingPagination):
    category = 'reports_summary'

    def get_columns(self):
        return reports_summary_table(self.request.user, self.category)
