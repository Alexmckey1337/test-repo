from django.urls import path

from apps.proposal import views

app_name = 'proposal'


urlpatterns = [
    path('user/', views.ProposalListView.as_view(), name='list'),
    path('user/<int:pk>/', views.ProposalDetailView.as_view(), name='detail'),
    path('event/', views.EventProposalListView.as_view(), name='event-list'),
    path('event/<int:pk>/', views.EventProposalDetailView.as_view(), name='event-detail'),
]
