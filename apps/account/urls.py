from django.urls import path

from apps.account import views

app_name = 'account'

urlpatterns = [
    path('<int:user_id>/', views.account, name='detail'),
    path('<int:user_id>/logs/', views.UserLogsListView.as_view(), name='logs'),
    path('<int:user_id>/owner_logs/', views.OwnerLogsListView.as_view(), name='owner_logs'),
    path('logs/<int:log_id>/', views.UserLogDetailView.as_view(), name='log-detail'),
]
