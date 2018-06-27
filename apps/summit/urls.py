from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import path, reverse

from apps.summit import views

app_name = 'summit'


def redirect_to_summits(request):
    return redirect(reverse('summit:open'))


urlpatterns = [
    path('', login_required(redirect_to_summits, login_url='entry'), name='main'),
    path('<int:pk>/', views.SummitDetailView.as_view(), name='detail'),
    path('<int:pk>/info/', views.SummitInfoView.as_view(), name='info'),
    path('<int:summit_id>/status/', views.SummitEmailTasksView.as_view(), name='status'),
    path('<int:summit_id>/schedule/', views.SummitScheduleTasksView.as_view(), name='schedule'),
    path('open/', views.OpenSummitListView.as_view(), name='open'),
    path('closed/', views.ClosedSummitListView.as_view(), name='closed'),
    path('<int:pk>/report/', views.SummitBishopReportView.as_view(), name='report'),
    path('<int:pk>/statistics/', views.SummitStatisticsView.as_view(), name='stats'),
    path('profile/<int:pk>/', views.SummitProfileDetailView.as_view(), name='profile-detail'),
    path('profile/<int:profile_id>/emails/',
         views.SummitProfileEmailListView.as_view(), name='profile-email-list'),
    path('emails/<int:pk>/', views.SummitProfileEmailDetailView.as_view(), name='profile-email-detail'),
    path('emails/<int:pk>/text/', views.SummitProfileEmailTextView.as_view(), name='profile-email-text'),
    path('tickets/', views.SummitTicketListView.as_view(), name='tickets'),
    path('tickets/<int:pk>/', views.SummitTicketDetailView.as_view(), name='ticket-detail'),
    path('tickets/author/<int:author_id>/', views.SummitTicketByAuthorListView.as_view(), name='tickets-author'),

    path('<int:pk>/history/statistics/', views.SummitHistoryStatisticsView.as_view(), name='history-stats'),
]
