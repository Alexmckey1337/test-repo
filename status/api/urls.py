from django.conf.urls import url, include
from rest_framework import routers

from status.api import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'statuses', views.StatusViewSet)
router_v1_0.register(r'divisions', views.DivisionViewSet)

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),
]
