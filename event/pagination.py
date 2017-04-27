from group.pagination import PaginationMixin


class MeetingPagination(PaginationMixin):
    category = 'meetings'


class MeetingAttendPagination(PaginationMixin):
    category = 'attends'


class ChurchReportPagination(PaginationMixin):
    category = 'church_reports'
