from django.urls import include, path
from rest_framework import routers

from apps.event.api import views

router_v1_0 = routers.DefaultRouter()

router_v1_0.register('home_meetings', views.MeetingViewSet)
router_v1_0.register('church_reports', views.ChurchReportViewSet)

custom_urls = [
    path('church_reports/stats/', views.ChurchReportStatsView.as_view(), name="church_report-stats"),
]

urlpatterns = [
    path('', include(custom_urls)),
    path('', include(router_v1_0.urls)),
]
