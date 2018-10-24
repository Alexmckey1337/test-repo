from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt

from apps.manager.api import views

urlpatterns = [
	re_path(r'^$', views.GroupManagerListView.as_view(), name='group-manager-list-create'),
	re_path(r'^(?P<pk>[0-9]+)/$', views.GroupManagerDetailView.as_view(), name='group-manager-retrieve-update'),
]
