from django_filters import rest_framework
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.report.models import UserReport, WeekReport, MonthReport, YearReport
from apps.report.api.serializers import (
    UserReportSerializer, WeekReportSerializer, MonthReportSerializer, YearReportSerializer)


class UserReportViewSet(viewsets.ModelViewSet):
    queryset = UserReport.objects.all()
    serializer_class = UserReportSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter,)
    search_fields = ()
    filter_fields = []
    permission_classes = (IsAuthenticated,)


class WeekReportViewSet(viewsets.ModelViewSet):
    queryset = WeekReport.objects.all()
    serializer_class = WeekReportSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter,)
    search_fields = ()
    filter_fields = ['from_date', 'to_date', ]
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        master_queryset = WeekReport.objects.filter(user__user__master=request.user).all()
        disciples_queryset = WeekReport.objects.filter(user__user__master__master=request.user,
                                                       ).exclude(user__user__disciples=None).all()
        q = master_queryset | disciples_queryset
        queryset = self.filter_queryset(q)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MonthReportViewSet(viewsets.ModelViewSet):
    queryset = MonthReport.objects.all()
    serializer_class = MonthReportSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter,)
    permission_classes = (IsAuthenticated,)
    search_fields = ()
    filter_fields = ['date', ]

    def list(self, request, *args, **kwargs):
        master_queryset = MonthReport.objects.filter(user__user__master=request.user).all()
        disciples_queryset = MonthReport.objects.filter(user__user__master__master=request.user,
                                                        ).exclude(user__user__disciples=None).all()
        q = master_queryset | disciples_queryset
        queryset = self.filter_queryset(q)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class YearReportViewSet(viewsets.ModelViewSet):
    queryset = YearReport.objects.all()
    serializer_class = YearReportSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter,)
    search_fields = ()
    filter_fields = ['date', ]
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        master_queryset = YearReport.objects.filter(user__user__master=request.user).all()
        disciples_queryset = YearReport.objects.filter(user__user__master__master=request.user,
                                                       ).exclude(user__user__disciples=None).all()
        q = master_queryset | disciples_queryset
        queryset = self.filter_queryset(q)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
