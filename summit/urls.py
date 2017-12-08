from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

from summit import views

app_name = 'summit'


def redirect_to_summits(request):
    return redirect(reverse('summit:open'))


urlpatterns = [
    url(r'^$', login_required(redirect_to_summits, login_url='entry'), name='main'),
    url(r'^(?P<pk>\d+)/$', views.SummitDetailView.as_view(), name='detail'),
    url(r'^(?P<summit_id>\d+)/status/$', views.SummitEmailTasksView.as_view(), name='status'),
    url(r'^(?P<summit_id>\d+)/schedule/$', views.SummitScheduleTasksView.as_view(), name='schedule'),
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
