from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from apps.proposal.api import views

urlpatterns = [
    path('proposal/create/', views.CreateProposalView.as_view(), name='proposal-create'),
    path('proposal/<int:pk>/receive/', views.ReceiveProposalView.as_view(), name='proposal-receive'),
    path('proposal/<int:pk>/reopen/', views.ReopenProposalView.as_view(), name='proposal-reopen'),
    path('proposal/<int:pk>/reject/', views.RejectProposalView.as_view(), name='proposal-reject'),
    path('proposal/<int:pk>/process/', views.ProcessProposalView.as_view(), name='proposal-process'),
    path('proposal/', csrf_exempt(views.proposal), name='proposal-list'),

    path('event_proposal/create/', views.CreateEventProposalView.as_view(), name='event_proposal-create'),
    path('event_proposal/<int:pk>/receive/', views.ReceiveEventProposalView.as_view(), name='event_proposal-receive'),
    path('event_proposal/<int:pk>/reopen/', views.ReopenEventProposalView.as_view(), name='event_proposal-reopen'),
    path('event_proposal/<int:pk>/reject/', views.RejectEventProposalView.as_view(), name='event_proposal-reject'),
    path('event_proposal/<int:pk>/process/', views.ProcessEventProposalView.as_view(), name='event_proposal-process'),
    path('event_proposal/', csrf_exempt(views.event_proposal), name='event_proposal-list'),
]
