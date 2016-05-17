# -*- coding: utf-8
from models import Navigation, Table, ColumnType, Column
from rest_framework import viewsets, filters
from serializers import NavigationSerializer, TableSerializer, ColumnTypeSerializer, ColumnSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

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
    response_dict = dict()
    table = None
    if request.method == 'POST':
        for data in request.data:
            try:
                object = Column.objects.get(id=data['id'])
                table = object.table
                for key, value in data.iteritems():
                    if key == 'active' and not object.columnType.editable:
                        pass
                    else:
                        setattr(object, key, value)
                object.save()
                #serializer = ColumnSerializer(object, context={'request': request})
                #response_dict['data'] = serializer.data
            except Column.DoesNotExist:
                pass
    response_dict['message'] = u"Колонки успешно отредактирована"
    response_dict['status'] = True
    response_dict['column_table'] = table.user.column_table
    return Response(response_dict)
