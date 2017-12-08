from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

from apps.event import views

app_name = 'events'


def redirect_to_meetings(request):
    if not request.user.can_see_churches():
        return redirect(reverse('db:people'))
    return redirect(reverse('events:meeting_report_list'))


urlpatterns = [
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
