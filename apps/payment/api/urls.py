from django.urls import path, include
from apps.payment.api import views

payment_urlpatterns = [
    path('payments/<int:pk>/', views.PaymentUpdateDestroyView.as_view(), name='payment-delete'),
    path('payments/<int:pk>/', views.PaymentUpdateDestroyView.as_view(), name='payment-update'),
    path('payments/<int:pk>/detail/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/', views.PaymentListView.as_view(), name='payment-list'),
    path('payments/deal/', views.PaymentDealListView.as_view(), name='payment-deal-list'),
    path('payments/church_report/', views.PaymentChurchReportListView.as_view(), name='payment-church_report-list'),
    path('payments/<int:pk>/detail/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/export/', views.PaymentDealListView.as_view(), name='payment-export'),
    path('payments/supervisors/', views.PaymentSupervisorListView.as_view(), name='payment-supervisors'),
]

urlpatterns = [
    path('', include(payment_urlpatterns)),
]
