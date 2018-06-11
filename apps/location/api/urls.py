from django.urls import path, include
from rest_framework import routers

from apps.location.api import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register('countries', views.OldCountryViewSet)
router_v1_0.register('regions', views.OldRegionViewSet)
router_v1_0.register('cities', views.OldCityViewSet)

urlpatterns = [
    path('', include(router_v1_0.urls)),
    path('city/', views.CitySearchListView.as_view()),
    path('vo/city/', views.VoCitySearchListView.as_view())
]
