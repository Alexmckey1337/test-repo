from django.conf.urls import url

from account import views

app_name = 'account'

urlpatterns = [
    url(r'^(\d+)/$', views.account, name='detail'),
    url(r'^(?P<user_id>\d+)/logs/$', views.UserLogsListView.as_view(), name='logs'),
    url(r'^(?P<user_id>\d+)/owner_logs/$', views.OwnerLogsListView.as_view(), name='owner_logs'),
    url(r'^logs/(?P<log_id>\d+)/$', views.UserLogDetailView.as_view(), name='log-detail'),
]
