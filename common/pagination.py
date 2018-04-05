from rest_framework.pagination import PageNumberPagination


class ForSelectPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100
