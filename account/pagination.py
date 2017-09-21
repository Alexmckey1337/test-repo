# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework.pagination import PageNumberPagination


class ShortPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10


class DashboardPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 50
