# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import exceptions, permissions
from rest_framework.permissions import AllowAny
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator as BaseSchemaGenerator
from rest_framework.views import APIView
from rest_framework_swagger import renderers


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


schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    urlconf="edem.api_urls",
    # validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('rest-auth/', include('rest_auth.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    re_path(r'^swagger(?P<format>.json|.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),

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
