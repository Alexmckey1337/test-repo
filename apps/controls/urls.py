from django.urls import path

from apps.controls import views


app_name = 'controls'

urlpatterns = [
    path('db_access/', views.db_access_list, name='db_access_lists'),
    path('db_access/<int:pk>/', views.db_access_detail, name='db_access_detail'),
    path('summit_panel/', views.summit_panel_list, name='summit_panel'),
]
