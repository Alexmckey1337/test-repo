from django.urls import include, path
from rest_framework import routers

from apps.help.api import views

router = routers.DefaultRouter()

router.register('manuals', views.ManualViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
