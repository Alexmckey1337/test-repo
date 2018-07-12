from django.urls import path, include
from rest_framework import routers

from apps.account.api import calls as calls_views
from apps.account.api import views, old_views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register('short_users', views.UserShortViewSet, base_name='short_users')
router_v1_0.register('exist_users', views.ExistUserListViewSet, base_name='exist_users')
router_v1_0.register('dashboard_users', views.DashboardMasterTreeFilterViewSet, base_name='dashboard_users')

router_v1_1 = routers.DefaultRouter()
router_v1_1.register('users', views.UserViewSet, base_name='users_v1_1')

custom_urls = [
    path('login/', old_views.login_view),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('password_forgot/', old_views.password_forgot, ),
    path('password_view/', old_views.password_view, ),
]

custom_v1_1_urls = [
    path('tables/user/', views.UserTableView.as_view(), name="tables-user"),
    path('exports/user/', views.UserExportView.as_view(), name="exports-user"),

    path('users/for_select/', views.UserForSelectView.as_view(), name="users-select"),
    path('users/partner_managers/', views.PartnerManagersView.as_view(), name="users-select"),
    path('calls_to_user/', calls_views.calls_to_user, name='calls_to_user'),
    path('all_calls/', calls_views.all_calls, name='all_calls'),
    path('asterisk_users/', calls_views.asterisk_users, name='asterisk_users'),
    path('change_asterisk_user/', calls_views.change_asterisk_user, name='change_asterisk_user'),

    path('vo/users/<int:pk>/', views.VoUserDetailView.as_view(), name='vo-user-detail'),
    path('vo/users/<int:pk>/master/', views.VoMasterDetailView.as_view(), name='vo-master-detail'),
    path('vo/messengers/', views.VoMessengerListView.as_view(), name='vo-messenger-list'),
    path('vo/hierarchies/', views.VoHierarchyListView.as_view(), name='vo-hierarchy-list'),
]

urlpatterns = [
    path('', include(custom_urls)),
    path('', include(router_v1_0.urls)),

    path('', include(custom_v1_1_urls)),
    path('', include(router_v1_1.urls)),
]
