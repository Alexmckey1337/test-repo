from datetime import datetime

from django.http import HttpResponse
from import_export.formats import base_formats
from rest_framework import viewsets, mixins, exceptions
from rest_framework.decorators import list_route
from payment.tasks import generate_export
from rest_framework.response import Response


class ModelWithoutDeleteViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                                mixins.CreateModelMixin, viewsets.GenericViewSet):
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
        date_str = datetime.now().strftime('%Y-%m-%d')
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
            fields, resource_class, self.file_format, file_name])

        # data = resource_class().export(queryset, custom_export_fields=fields)
        # export_data = self.file_format.export_data(data, delimiter=';')
        # content_type = self.file_format.get_content_type()
        # response = HttpResponse(export_data, content_type=content_type)
        #
        # response['Content-Disposition'] = 'attachment; filename=%s' % (
        #     self.get_export_filename(self.file_format),
        # )
        # response['Content-Encoding'] = 'UTF-8'
        # return response
        return Response({'message': 'Successful task creating for generate export'})


class ExportViewSetMixin(BaseExportViewSetMixin):
    def _export(self, request, *args, **kwargs):
        fields = self.get_export_fields(request.data)
        queryset = self.get_export_queryset(request)

        return self.get_response(queryset, fields)

    @list_route(methods=['post'])
    def export(self, request, *args, **kwargs):
        return self._export(request, *args, **kwargs)
