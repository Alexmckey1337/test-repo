# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse

from main import views


def redirect_to_deals(request):
    if request.user.can_see_deals():
        return redirect(reverse('partner:deals'))
    if request.user.can_see_partners():
        return redirect(reverse('partner:list'))
    if request.user.can_see_partner_stats():
        return redirect(reverse('partner:stats'))
    if request.user.can_see_deal_payments():
        return redirect(reverse('partner:payments'))
    raise PermissionDenied


def redirect_to_churches(request):
    if not request.user.can_see_churches():
        return redirect(reverse('db:people'))
    return redirect(reverse('db:churches'))

database_patterns = [
    url(r'^$', login_required(redirect_to_churches, login_url='entry'), name='main'),
    url(r'^people/$', views.PeopleListView.as_view(), name='people'),
    url(r'^churches/$', views.ChurchListView.as_view(), name='churches'),
    url(r'^home_groups/$', views.HomeGroupListView.as_view(), name='home_groups'),
]
partner_patterns = [
    url(r'^$', login_required(redirect_to_deals, login_url='entry'), name='main'),
    url(r'^list/$', views.PartnerListView.as_view(), name='list'),
    url(r'^deals/$', views.DealListView.as_view(), name='deals'),
    url(r'^stats/$', views.PartnerStatisticsListView.as_view(), name='stats'),
    url(r'^payments/$', views.PartnerPaymentsListView.as_view(), name='payments'),
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
    url(r'^(?P<pk>\d+)/$', views.SummitTypeView.as_view(), name='detail'),
]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^entry/$', views.entry, name='entry'),

    url(r'^db/', include(database_patterns, namespace='db')),
    url(r'^account/', include(account_patterns, namespace='account')),
    url(r'^partner/', include(partner_patterns, namespace='partner')),
    url(r'^meeting_types/', include(meeting_patterns, namespace='meeting_type')),
    url(r'^summits/', include(summit_patterns, namespace='summit')),

    url(r'^churches/(?P<pk>\d+)/$', views.ChurchDetailView.as_view(), name='church_detail'),
    url(r'^home_groups/(?P<pk>\d+)/$', views.HomeGroupDetailView.as_view(), name='home_group_detail'),


    url(r'^password_view/(?P<activation_key>\w+)/$', views.edit_pass, name='password_view'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
