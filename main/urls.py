# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import reverse

from main import views

def redirect_to_deals(request):
    return redirect(reverse('partner-deals'))

urlpatterns = [
    url(r'^entry/$', views.entry, name='entry'),
    url(r'^events/$', views.events, name='events'),
    url(r'^partner/$', redirect_to_deals, name='partner'),
    url(r'^partner/list/$', views.partner, name='partner-list'),
    url(r'^partner/deals/$', views.deals, name='partner-deals'),
    url(r'^partner/stats/$', views.stats, name='partner-stats'),
    url(r'^account/([0-9]+)/$', views.account, name='account'),
    url(r'^account_edit/([0-9]+)/$', views.account_edit, name='account_edit'),
    url(r'^reports/$', views.reports, name='reports'),
    url(r'^summits/$', views.summits, name='summits'),
    url(r'^summit_info/([0-9]+)/$', views.summit_info, name='summit_info'),

    url(r'^churches/$', views.churches, name='churches'),
    url(r'^churches/all_users/$', views.churches_all_users, name='churches_all_users'),
    url(r'^churches/([0-9]+)/$', views.church_detail, name='church_detail'),
    url(r'^home_groups/$', views.home_groups, name='home_groups'),
    url(r'^home_groups/([0-9]+)/$', views.home_group_detail, name='home_group_detail'),

    url(r'^$', views.index, name='index'),
    url(r'^event_info/$', views.event_info, name='event_info'),
    url(r'^password_view/(?P<activation_key>\w+)/$', views.edit_pass, name='password_view'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
