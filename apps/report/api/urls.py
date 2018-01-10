from django.urls import path, include
from rest_framework import routers

from apps.report.api import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register('user_reports', views.UserReportViewSet)
router_v1_0.register('week_reports', views.WeekReportViewSet)
router_v1_0.register('month_reports', views.MonthReportViewSet)
router_v1_0.register('year_reports', views.YearReportViewSet)

urlpatterns = [
    path('v1.0/', include(router_v1_0.urls)),
]
