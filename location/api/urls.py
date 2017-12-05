from django.conf.urls import url, include
from rest_framework import routers

from location.api import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'countries', views.CountryViewSet)
router_v1_0.register(r'regions', views.RegionViewSet)
router_v1_0.register(r'cities', views.CityViewSet)

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),
]
