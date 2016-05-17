from django.conf.urls import patterns, include, url
from django.conf.urls import include, url
import views

urlpatterns = [
    url(r'^entry/$', views.entry, name='entry'),
    url(r'^events/$', views.events, name='events'),
    url(r'^account/([0-9]+)/$', views.account, name='account'),
    url(r'^account_create/$', views.account_create, name='account_create'),
    url(r'^account_edit/([0-9]+)/$', views.account_edit, name='account_edit'),
    url(r'^reports/$', views.reports, name='reports'),
#    url(r'^settings$', views.settings, name='settings'),
    url(r'^settings_disciples/$', views.settings_disciples, name='settings_disciples'),
    url(r'^settings_events/$', views.settings_events, name='settings_events'),
    url(r'^notifications/$', views.notifications, name='notifications'),
    url(r'^synchronize/$', views.synchronize, name='synchronize'),
    url(r'^$', views.reports, name='index'),
]
