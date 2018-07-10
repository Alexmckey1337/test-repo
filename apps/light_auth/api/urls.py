from django.urls import path

from apps.light_auth.api import views

app_name = 'light_auth'

urlpatterns = [
    path('create/<int:pk>/', views.LightAuthCreateView.as_view(), name='create'),
    path('send_confirm/<int:pk>/', views.LightAuthConfirmPhoneNumberView.as_view(), name='send_confirm'),
    path('reset_password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('verify_phone/', views.VerifyPhoneView.as_view(), name='verify_phone'),
    path('login/', views.LightLoginView.as_view(), name='login'),
]
