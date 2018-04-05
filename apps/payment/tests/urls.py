from django.urls import path, include
from apps.payment.api import views

urlpatterns = [
    path('payment/<int:pk>/', views.PaymentUpdateDestroyView.as_view()),
    path('payments/', views.PaymentListView.as_view()),
    path('payments/deal/', views.PaymentDealListView.as_view()),
    path('', include('edem.urls'))
]
