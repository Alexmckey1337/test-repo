from django.urls import path

from apps.controls import views


app_name = 'controls'

urlpatterns = [
    path('db_access/', views.db_access, name='db_access'),
]
