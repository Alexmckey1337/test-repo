from django.urls import path, include
from rest_framework import routers

from apps.group.api import views


router_v1_0 = routers.DefaultRouter()

router_v1_0.register('churches', views.ChurchViewSet, base_name='church')
router_v1_0.register('home_groups', views.HomeGroupViewSet)

urlpatterns = [
    path('tables/church/', views.ChurchTableView.as_view(), name="tables-church"),
    path('exports/church/', views.ChurchExportView.as_view(), name="exports-church"),
    path('locations/church/', views.ChurchLocationListView.as_view()),
    path('', include(router_v1_0.urls)),
]
