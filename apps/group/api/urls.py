from django.urls import path, include
from rest_framework import routers

from apps.group.api import views


router_v1_0 = routers.DefaultRouter()

router_v1_0.register('churches', views.ChurchViewSet, base_name='church')
router_v1_0.register('home_groups', views.HomeGroupViewSet)

urlpatterns = [
    path('tables/church/', views.ChurchTableView.as_view(), name="tables-church"),
    path('tables/home_group/', views.HomeGroupTableView.as_view(), name="tables-home_group"),

    path('vo/home_groups/', views.VoHGListView.as_view(), name="vo-home_group"),
    path('vo/home_groups/directions/', views.VoDirectionListView.as_view(), name="vo-home_group-direction"),

    path('exports/church/', views.ChurchExportView.as_view(), name="exports-church"),
    path('exports/home_group/', views.HomeGroupExportView.as_view(), name="exports-home_group"),

    path('locations/church/', views.ChurchLocationListView.as_view()),
    path('locations/home_group/', views.HomeGroupLocationListView.as_view()),

    path('', include(router_v1_0.urls)),
]
