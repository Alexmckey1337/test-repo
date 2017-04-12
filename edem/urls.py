# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from filebrowser.sites import site
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='CRM API')

urlpatterns = [
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^api/$', schema_view),
    url(r'^api/', include('account.urls')),
    url(r'^api/', include('event.urls')),
    url(r'^api/', include('hierarchy.urls')),
    url(r'^api/', include('location.urls')),
    url(r'^api/', include('navigation.urls')),
    url(r'^api/', include('notification.urls')),
    url(r'^api/', include('partnership.urls')),
    url(r'^api/', include('payment.urls')),
    url(r'^api/', include('report.urls')),

    url(r'^api/', include('group.urls')),

    url(r'^api/', include('status.urls')),
    url(r'^api/', include('summit.urls')),

    url(r'^', include('main.urls')),
    url(r'^', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass

if not settings.DEBUG:
    handler404 = 'common.errors_views.page_not_found'
    handler403 = 'common.errors_views.permission_denied'
    handler400 = 'common.errors_views.bad_request'
