from django.urls import path

from apps.proposal.api import views

urlpatterns = [
    path('proposal/create/', views.CreateProposalView.as_view(), name='proposal-create'),
    path('proposal/<int:pk>/receive/', views.ReceiveProposalView.as_view(), name='proposal-receive'),
    path('proposal/<int:pk>/reopen/', views.ReopenProposalView.as_view(), name='proposal-reopen'),
    path('proposal/<int:pk>/reject/', views.RejectProposalView.as_view(), name='proposal-reject'),
    path('proposal/<int:pk>/process/', views.ProcessProposalView.as_view(), name='proposal-process'),
]
