from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse, path

from apps.proposal import views

app_name = 'proposal'


urlpatterns = [
    path('', views.ProposalListView.as_view(), name='list'),
    path('<int:pk>/', views.ProposalDetailView.as_view(), name='detail'),
]
