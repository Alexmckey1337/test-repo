from django.urls import path, include
from rest_framework import routers

from apps.testing.api.views import TestResultViewSet

router_v1 = routers.DefaultRouter()
router_v1.register('test_results', TestResultViewSet)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
