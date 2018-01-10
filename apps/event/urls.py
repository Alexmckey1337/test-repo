from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse, path

from apps.event import views

app_name = 'events'


def redirect_to_meetings(request):
    if not request.user.can_see_churches():
        return redirect(reverse('db:people'))
    return redirect(reverse('events:meeting_report_list'))


urlpatterns = [
    path('', login_required(redirect_to_meetings, login_url='entry'), name='main'),
    path('home/reports/', views.meeting_report_list, name='meeting_report_list'),
    path('home/reports/<int:pk>/', views.meeting_report_detail, name='meeting_report_detail'),
    path('home/statistics/', views.meeting_report_statistics, name='meeting_report_statistics'),
    path('home/summary/', views.meetings_summary, name='meetings_summary'),
    path('church/reports/', views.church_report_list, name='church_report_list'),
    path('church/reports/<int:pk>/', views.church_report_detail, name='church_report_detail'),
    path('church/statistics/', views.church_statistics, name='church_report_statistics'),
    path('church/summary/', views.reports_summary, name='reports_summary'),
    path('church/payments/', views.report_payments, name='report_payments'),
]
