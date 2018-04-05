from django.urls import path, include
from rest_framework import routers

from apps.notification.api import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register('notifications', views.NotificationViewSet)

custom_urls = [
    # path('entry/$', views.entry, name='entry'),
    # path('events/$', views.events, name='events'),
]

urlpatterns = [
    path('', include(router_v1_0.urls)),

    path('', include(custom_urls)),
]
