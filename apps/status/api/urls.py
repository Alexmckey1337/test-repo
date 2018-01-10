from django.urls import path, include
from rest_framework import routers

from apps.status.api import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register('statuses', views.StatusViewSet)
router_v1_0.register('divisions', views.DivisionViewSet)

urlpatterns = [
    path('', include(router_v1_0.urls)),
]
