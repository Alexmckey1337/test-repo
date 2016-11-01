from django.conf.urls import url, include
from rest_framework import routers

from report import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'user_reports', views.UserReportViewSet)
router_v1_0.register(r'week_reports', views.WeekReportViewSet)
router_v1_0.register(r'month_reports', views.MonthReportViewSet)
router_v1_0.register(r'year_reports', views.YearReportViewSet)

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),
]