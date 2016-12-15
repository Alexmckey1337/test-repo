# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from main import views

urlpatterns = [
    url(r'^entry/$', views.entry, name='entry'),
    url(r'^events/$', views.events, name='events'),
    url(r'^deals/$', views.deals, name='deals'),
                  url(r'^partners/stats/$', views.partner_stats, name='partner_stats'),
    url(r'^account/([0-9]+)/$', views.account, name='account'),
    url(r'^account_edit/([0-9]+)/$', views.account_edit, name='account_edit'),
    url(r'^reports/$', views.reports, name='reports'),
    url(r'^summits/$', views.summits, name='summits'),
    url(r'^summit_info/([0-9]+)/$', views.summit_info, name='summit_info'),
    url(r'^$', views.index, name='index'),
    url(r'^event_info/$', views.event_info, name='event_info'),
    url(r'^password_view/(?P<activation_key>\w+)/$', views.edit_pass, name='password_view'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
