from django.urls import path, include
from rest_framework import routers

from apps.location.api import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register('countries', views.CountryViewSet)
router_v1_0.register('regions', views.RegionViewSet)
router_v1_0.register('cities', views.CityViewSet)

urlpatterns = [
    path('', include(router_v1_0.urls)),
]
