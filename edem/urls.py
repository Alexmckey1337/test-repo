# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator as BaseSchemaGenerator
from rest_framework_swagger import renderers
from rest_framework.permissions import AllowAny
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.views import APIView


class SchemaGenerator(BaseSchemaGenerator):
    def __init__(self, title=None, url=None, description=None, patterns=None, urlconf=None):
        super().__init__(title=title, url=url, description=description, patterns=patterns, urlconf=urlconf)

    def has_view_permissions(self, path, method, view):
        return True


class SwaggerSchemaView(APIView):
    _ignore_model_permissions = True
    exclude_from_schema = True
    permission_classes = [AllowAny]
    renderer_classes = [
        CoreJSONRenderer,
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer
    ]

    def get(self, request):
        generator = SchemaGenerator(title="CRM API", url='/api/', urlconf="edem.api_urls")
        schema = generator.get_schema(request=request)

        if not schema:
            raise exceptions.ValidationError(
                'The schema generator did not return a schema Document'
            )

        return Response(schema)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('rest-auth/', include('rest_auth.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('api/', SwaggerSchemaView.as_view()),
    path('api/', include('edem.api_urls')),
    path('api/v1.0/', include('edem.api_urls')),
    path('api/v1.1/', include('edem.api_urls')),
    path('', include('main.urls')),
    path('', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass

if not settings.DEBUG:
    handler404 = 'common.errors_views.page_not_found'
    handler403 = 'common.errors_views.permission_denied'
    handler400 = 'common.errors_views.bad_request'
