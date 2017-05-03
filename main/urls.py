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


def redirect_to_meetings(request):
    if not request.user.can_see_churches():
        return redirect(reverse('db:people'))
    return redirect(reverse('events:meeting_report_list'))


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
]

events_patterns = [
    url(r'^$', login_required(redirect_to_meetings, login_url='entry'), name='main'),
    url(r'^home/reports/$', views.meeting_report_list, name='meeting_report_list'),
    url(r'^home/reports/(?P<pk>\d+)/$', views.meeting_report_detail, name='meeting_report_detail'),
    url(r'^home/statistics/$', views.meeting_report_statistics, name='meeting_report_statistics'),
    url(r'^church/reports/$', views.church_report_list, name='church_report_list'),
    url(r'^church/reports/(?P<pk>\d+)/$', views.church_report_detail, name='church_report_detail'),
    url(r'^church/statistics/$', views.church_statistics, name='church_report_statistics'),
]

summit_patterns = [
    url(r'^$', views.summits, name='list'),
    url(r'^(?P<pk>\d+)/$', views.SummitTypeView.as_view(), name='detail'),
    url(r'^tickets/$', views.SummitTicketListView.as_view(), name='tickets'),
    url(r'^tickets/(?P<pk>\d+)/$', views.SummitTicketDetailView.as_view(), name='ticket-detail'),
]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^entry/$', views.entry, name='entry'),

    url(r'^db/', include(database_patterns, namespace='db')),
    url(r'^account/', include(account_patterns, namespace='account')),
    url(r'^partner/', include(partner_patterns, namespace='partner')),
    url(r'^events/', include(events_patterns, namespace='events')),
    url(r'^summits/', include(summit_patterns, namespace='summit')),

    url(r'^churches/(?P<pk>\d+)/$', views.ChurchDetailView.as_view(), name='church_detail'),
    url(r'^home_groups/(?P<pk>\d+)/$', views.HomeGroupDetailView.as_view(), name='home_group_detail'),

    url(r'^password_view/(?P<activation_key>\w+)/$', views.edit_pass, name='password_view'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
