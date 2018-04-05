from django.urls import path

from apps.navigation.api import views

urlpatterns = [
    path('update_columns/', views.redis_update_columns),
]
