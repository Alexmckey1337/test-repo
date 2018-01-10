from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

from apps.controls import views


app_name = 'controls'

urlpatterns = [
    url(r'^db_access/$', views.db_access, name='db_access'),
]
