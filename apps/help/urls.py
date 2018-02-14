# -*- coding: utf-8
from apps.help import views
from django.urls import reverse, path
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def redirect_to_help(request):
    return redirect(reverse('help:category_list'))


app_name = 'help'

urlpatterns = [
    path('', login_required(redirect_to_help, login_url='entry'), name='main'),
    path('categories/', views.manual_category_list, name='category_list'),
    path('manual/<int:pk>/', views.manual_detail, name='manual_detail')
]
