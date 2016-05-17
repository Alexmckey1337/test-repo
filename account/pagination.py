from edem.settings import SHORT_PAGINATION, DEFAULT_PAGINATION
from rest_framework.pagination import PageNumberPagination


class ShortPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10