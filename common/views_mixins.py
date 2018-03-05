from django.utils import timezone
from import_export.formats import base_formats
from rest_framework import viewsets, mixins, exceptions
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView

from apps.navigation.table_columns import get_table
from apps.payment.tasks import generate_export
from rest_framework.response import Response

from common.pagination import TablePageNumberPagination


class ModelWithoutDeleteViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                                mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class ModelWithoutListViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                              mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class URCViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class BaseExportViewSetMixin(object):
    resource_class = None
    queryset = None
    file_format = base_formats.CSV()

    def get_queryset(self):
        raise NotImplementedError(".get_queryset() must be overridden.")

    def filter_queryset(self, qs):
        raise NotImplementedError(".filter_queryset() must be overridden.")

    def get_export_filename(self, file_format):
        date_str = timezone.now().strftime('%Y-%m-%d')
        filename = "%s-%s.%s" % (self.queryset.model.__name__,
                                 date_str,
                                 file_format.get_extension())
        return filename

    @staticmethod
    def str_to_list_by_comma(string):
        if not string.strip():
            return []
        return list(map(lambda d: d.strip(), string.split(',')))

    def get_export_fields(self, data):
        return self.str_to_list_by_comma(data.get('fields', '')) or None

    def get_ids(self, data):
        return self.str_to_list_by_comma(data.get('ids', '')) or None

    def get_export_queryset(self, request):
        ids = self.get_ids(request.data)
        qs = self.get_queryset()
        if ids:
            return qs.filter(id__in=ids)
        return self.filter_queryset(qs)

    def get_resource_class(self):
        return self.resource_class

    def get_response(self, queryset, fields, resource_class=None):
        resource_class = resource_class or self.get_resource_class()
        file_name = self.request.query_params.get('file_name')
        if not file_name:
            raise exceptions.ValidationError({'message': 'Parameter {file_name} must be passed'})
        generate_export.apply_async(args=[
            self.request.user.id, queryset.model, list(queryset.values_list('id', flat=True)),
            list(fields), resource_class, self.file_format, file_name])

        return Response({'message': 'Successful task creating for generate export'})


class ExportViewSetMixin(BaseExportViewSetMixin):
    def _export(self, request, *args, **kwargs):
        fields = self.get_export_fields(request.data)
        queryset = self.get_export_queryset(request)

        return self.get_response(queryset, fields)

    @action(detail=False, methods=['post'])
    def export(self, request, *args, **kwargs):
        return self._export(request, *args, **kwargs)


class TableViewMixin(GenericAPIView):
    table_name = ''
    pagination_class = TablePageNumberPagination

    _columns = None

    def get(self, request, *args, **kwargs):
        request.columns = self.columns
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @property
    def columns(self):
        if self._columns is None:
            self._columns = get_table(self.table_name, self.request.user.id)
        return self._columns

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        extra = {
            'extra_fields': self.request.query_params.getlist('extra_fields'),
            'columns': self.columns,
        }
        ctx.update(extra)

        return ctx