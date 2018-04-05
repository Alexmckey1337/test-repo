from django.urls import path, include
from rest_framework import routers

from . import views

router_v1_0 = routers.DefaultRouter()

router_v1_0.register('tasks', views.TaskViewSet)

urlpatterns = [
    path('', include(router_v1_0.urls)),
]
