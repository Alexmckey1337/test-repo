# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

from main import views


def redirect_to_churches(request):
    if not request.user.can_see_churches():
        return redirect(reverse('db:people'))
    return redirect(reverse('db:churches'))


database_patterns = (
    [
        url(r'^$', login_required(redirect_to_churches, login_url='entry'), name='main'),
        url(r'^people/$', views.PeopleListView.as_view(), name='people'),
        url(r'^churches/$', views.ChurchListView.as_view(), name='churches'),
        url(r'^home_groups/$', views.HomeGroupListView.as_view(), name='home_groups'),
    ], 'db')

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^entry/$', views.entry, name='entry'),
    url(r'^entry/restore/$', views.restore, name='restore'),
    url(r'^password_view/(?P<activation_key>\w+)/$', views.edit_pass, name='password_view'),

    url(r'^account/', include('account.urls', namespace='account')),
    url(r'^db/', include(database_patterns, namespace='db')),
    url(r'^events/', include('event.urls', namespace='events')),
    url(r'^partner/', include('partnership.urls', namespace='partner')),
    url(r'^payment/', include('payment.urls', namespace='payment')),
    url(r'^summits/', include('summit.urls', namespace='summit')),
    url(r'^tasks/', include('task.urls', namespace='tasks')),

    url(r'^churches/(?P<pk>\d+)/$', views.ChurchDetailView.as_view(), name='church_detail'),
    url(r'^home_groups/(?P<pk>\d+)/$', views.HomeGroupDetailView.as_view(), name='home_group_detail'),

    url(r'^privacy_policy', views.privacy_policy, name='privacy_policy'),  # for mobile app
    url(r'^ticket_scanner', views.ticket_scanner, name='ticket_scanner'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
