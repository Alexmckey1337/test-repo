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


def redirect_to_tasks(request):
    if not request.user.hierarchy.level <= 1:
        return redirect(reverse('db:people'))
    return redirect(reverse('tasks:task_list'))


def redirect_to_summits(request):
    return redirect(reverse('summit:open'))


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
    url(r'^summary/$', views.PartnerSummaryView.as_view(), name='partnership_summary'),
]

account_patterns = [
    url(r'^(\d+)/$', views.account, name='detail'),
    url(r'^(?P<user_id>\d+)/logs/$', views.UserLogsListView.as_view(), name='logs'),
    url(r'^(?P<user_id>\d+)/owner_logs/$', views.OwnerLogsListView.as_view(), name='owner_logs'),
    url(r'^logs/(?P<log_id>\d+)/$', views.UserLogDetailView.as_view(), name='log-detail'),
]

events_patterns = [
    url(r'^$', login_required(redirect_to_meetings, login_url='entry'), name='main'),
    url(r'^home/reports/$', views.meeting_report_list, name='meeting_report_list'),
    url(r'^home/reports/(?P<pk>\d+)/$', views.meeting_report_detail, name='meeting_report_detail'),
    url(r'^home/statistics/$', views.meeting_report_statistics, name='meeting_report_statistics'),
    url(r'^home/summary/$', views.meetings_summary, name='meetings_summary'),
    url(r'^church/reports/$', views.church_report_list, name='church_report_list'),
    url(r'^church/reports/(?P<pk>\d+)/$', views.church_report_detail, name='church_report_detail'),
    url(r'^church/statistics/$', views.church_statistics, name='church_report_statistics'),
    url(r'^church/summary/$', views.reports_summary, name='reports_summary'),
    url(r'^church/payments/$', views.report_payments, name='report_payments'),
]

task_patterns = [
    url(r'^$', login_required(redirect_to_tasks, login_url='entry'), name='main'),
    url(r'^all/$', views.task_list, name='task_list'),
]

summit_patterns = [
    url(r'^$', login_required(redirect_to_summits, login_url='entry'), name='main'),
    url(r'^(?P<pk>\d+)/$', views.SummitDetailView.as_view(), name='detail'),
    url(r'^open/$', views.OpenSummitListView.as_view(), name='open'),
    url(r'^closed/$', views.ClosedSummitListView.as_view(), name='closed'),
    url(r'^(?P<pk>\d+)/report/$', views.SummitBishopReportView.as_view(), name='report'),
    url(r'^(?P<pk>\d+)/statistics/$', views.SummitStatisticsView.as_view(), name='stats'),
    url(r'^profile/(?P<pk>\d+)/$', views.SummitProfileDetailView.as_view(), name='profile-detail'),
    url(r'^profile/(?P<profile_id>\d+)/emails/$',
        views.SummitProfileEmailListView.as_view(), name='profile-email-list'),
    url(r'^emails/(?P<pk>\d+)/$', views.SummitProfileEmailDetailView.as_view(), name='profile-email-detail'),
    url(r'^emails/(?P<pk>\d+)/text/$', views.SummitProfileEmailTextView.as_view(), name='profile-email-text'),
    url(r'^tickets/$', views.SummitTicketListView.as_view(), name='tickets'),
    url(r'^tickets/(?P<pk>\d+)/$', views.SummitTicketDetailView.as_view(), name='ticket-detail'),

    url(r'^(?P<pk>\d+)/history/statistics/$', views.SummitHistoryStatisticsView.as_view(), name='history-stats'),
]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^entry/$', views.entry, name='entry'),
    url(r'^entry/restore/$', views.restore, name='restore'),

    url(r'^db/', include(database_patterns, namespace='db')),
    url(r'^account/', include(account_patterns, namespace='account')),
    url(r'^partner/', include(partner_patterns, namespace='partner')),
    url(r'^events/', include(events_patterns, namespace='events')),
    url(r'^summits/', include(summit_patterns, namespace='summit')),
    url(r'^payment/deal/(?P<pk>\d+)/$', views.DealPaymentView.as_view(), name='payment-deal'),
    url(r'^payment/partner/(?P<pk>\d+)/$', views.PartnerPaymentView.as_view(), name='payment-partner'),

    url(r'^churches/(?P<pk>\d+)/$', views.ChurchDetailView.as_view(), name='church_detail'),
    url(r'^home_groups/(?P<pk>\d+)/$', views.HomeGroupDetailView.as_view(), name='home_group_detail'),
    url(r'^tasks/', include(task_patterns, namespace='tasks')),

    url(r'^password_view/(?P<activation_key>\w+)/$', views.edit_pass, name='password_view'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
