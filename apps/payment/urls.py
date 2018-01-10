from django.urls import path

from apps.payment import views

app_name = 'payment'


urlpatterns = [
    path('deal/<int:pk>/', views.DealPaymentView.as_view(), name='deal'),
    path('partner/<int:pk>/', views.PartnerPaymentView.as_view(), name='partner'),
]
