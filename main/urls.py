from django.conf.urls import url
import views

urlpatterns = [
    url(r'^entry/$', views.entry, name='entry'),
    url(r'^events/$', views.events, name='events'),
    url(r'^deals/$', views.deals, name='deals'),
    url(r'^account/([0-9]+)/$', views.account, name='account'),
    url(r'^account_edit/([0-9]+)/$', views.account_edit, name='account_edit'),
    url(r'^reports/$', views.reports, name='reports'),
    url(r'^summits/$', views.summits, name='summits'),
    url(r'^summit_info/([0-9]+)/$', views.summit_info, name='summit_info'),
    url(r'^$', views.index, name='index'),
    url(r'^event_info/$', views.event_info, name='event_info'),
    url(r'^password_view/(?P<activation_key>\w+)/$', views.edit_pass, name='password_view'),
]
