# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import reverse

from main import views


def redirect_to_deals(request):
    return redirect(reverse('partner:deals'))


def redirect_to_churches(request):
    return redirect(reverse('db:churches'))

database_patterns = [
    url(r'^$', redirect_to_churches, name='main'),
    url(r'^people/$', views.people, name='people'),
    url(r'^churches/$', views.churches, name='churches'),
    url(r'^home_groups/$', views.home_groups, name='home_groups'),
]
partner_patterns = [
    url(r'^$', redirect_to_deals, name='main'),
    url(r'^list/$', views.partner, name='list'),
    url(r'^deals/$', views.deals, name='deals'),
    url(r'^stats/$', views.stats, name='stats'),
]
account_patterns = [
    url(r'^(\d+)/$', views.account, name='detail'),
    url(r'^(\d+)/edit/$', views.account_edit, name='edit'),
]
meeting_patterns = [
    url(r'^$', views.meeting_types, name='list'),  # meeting_type-list
    url(r'^(?P<code>[-_\w]+)/$', views.meeting_type_detail, name='detail'),  # meeting_type-detail
    url(r'^(?P<code>[-_\w]+)/report/$', views.meeting_report, name='report'),  # meeting-report
]
summit_patterns = [
    url(r'^$', views.summits, name='list'),
    url(r'^(\d+)/$', views.summit_info, name='detail'),
]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^entry/$', views.entry, name='entry'),

    url(r'^db/', include(database_patterns, namespace='db')),
    url(r'^account/', include(account_patterns, namespace='account')),
    url(r'^partner/', include(partner_patterns, namespace='partner')),
    url(r'^meeting_types/', include(meeting_patterns, namespace='meeting_type')),
    url(r'^summits/', include(summit_patterns, namespace='summit')),

    url(r'^churches/([0-9]+)/$', views.church_detail, name='church_detail'),
    url(r'^home_groups/([0-9]+)/$', views.home_group_detail, name='home_group_detail'),


    url(r'^password_view/(?P<activation_key>\w+)/$', views.edit_pass, name='password_view'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
