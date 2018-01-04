# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.navigation.models import Navigation, Table, ColumnType, Column
from apps.navigation.api.serializers import (
    NavigationSerializer, TableSerializer, ColumnTypeSerializer, ColumnSerializer, UpdateColumnSerializer,
    RedisTableSerializer)


class NavigationViewSet(viewsets.ModelViewSet):
    queryset = Navigation.objects.all()
    serializer_class = NavigationSerializer


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = (IsAuthenticated,)


class ColumnTypeViewSet(viewsets.ModelViewSet):
    queryset = ColumnType.objects.all()
    serializer_class = ColumnTypeSerializer
    permission_classes = (IsAuthenticated,)


class ColumnViewSet(viewsets.ModelViewSet):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = (IsAuthenticated,)


@api_view(['POST'])
def update_columns(request):
    '''POST: (id, number, active)'''
    column_ids = {str(data['id']): data for data in request.data}
    columns = Column.objects.filter(
        id__in=column_ids.keys(),
        table__user=request.user,
        columnType__editable=True)
    for column_obj in columns:
        column = UpdateColumnSerializer(column_obj, data=column_ids[str(column_obj.id)], partial=True)
        column.is_valid(raise_exception=True)
        column.save()

    response_dict = {
        'detail': 'Колонки успешно отредактированы',
        'status': True,
        'column_table': request.user.column_table
    }
    return Response(response_dict)


@api_view(['POST'])
def redis_update_columns(request):
    '''POST: (id, number, active)'''
    serializer = RedisTableSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.save(user_id=request.user.id)
    return Response(data)
