from django.urls import path, include

from apps.payment import views

urlpatterns = [
    path('payment/deal/<int:pk>/', views.DealPaymentView.as_view(), name='payment-deal'),
    path('', include('edem.urls'))
]
