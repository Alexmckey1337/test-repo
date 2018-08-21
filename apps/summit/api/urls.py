from django.urls import path, include
from rest_framework import routers

from apps.summit.api import views, views_app, views_entry

router_v1_0 = routers.DefaultRouter()
router_v1_0.register('summit_profiles', views.SummitProfileViewSet, base_name='summit_profiles')
router_v1_0.register('summit_tickets', views.SummitTicketViewSet)
router_v1_0.register('summit_search', views.SummitUnregisterUserViewSet, base_name='summit_search')
router_v1_0.register('summit_lessons', views.SummitLessonViewSet)

router_v1_0.register('summit', views.SummitViewSet)
router_v1_0.register('summit_visitors_location', views_app.SummitVisitorLocationViewSet)
router_v1_0.register('summit_event_table', views_app.SummitEventTableViewSet)
router_v1_0.register('summit_attends', views_app.SummitAttendViewSet)

router_app = routers.DefaultRouter()
router_app.register('summits', views_app.SummitTypeForAppViewSet, base_name='summits')
router_app.register('open_summits', views_app.OpenSummitsForAppViewSet, base_name='open_summits')
router_app.register('users', views_app.SummitProfileForAppViewSet, base_name='users')
router_app.register('draw_users', views_app.SummitProfileWithLess10AbsentForAppViewSet, base_name='draw_users')
router_app.register('telegram_payment', views_app.TelegramPaymentsViewSet, base_name='telegram_payment'),

custom_urls = [
    path('generate_code/<str:filename>.pdf', views.generate_code, name='generate_code'),
    path('summit/<int:summit_id>/master/<int:master_id>.pdf',
         views.summit_report_by_participant, name='summit-report-participant'),
    path('summit/<int:summit_id>/report_by_bishops/',
         views.summit_report_by_bishops, name='summit-report-bishops'),
    path('generate_summit_tickets/<int:summit_id>/', views.generate_summit_tickets, name='generate_code'),
    path('generate_tickets/<int:summit_id>/author/<int:author_id>/', views.generate_tickets_by_author, name='generate_code_by_author'),
    path('summit/profile/<int:profile_id>/send_code/', views.send_code, name='send_code'),
    path('summit/<int:summit_id>/send_unsent_codes/', views.send_unsent_codes, name='send_unsent_codes'),
    path('summit/<int:summit_id>/send_unsent_schedules/',
         views.send_unsent_schedules, name='send_unsent_schedules'),
    path('summit/<int:summit_id>/stats/attends/',
         views.HistorySummitAttendStatsView.as_view(), name='attend-stats'),
    path('summit/<int:summit_id>/stats/latecomers/',
         views.HistorySummitLatecomerStatsView.as_view(), name='latecomer-stats'),
    path('summit/<int:summit_id>/stats/master/<int:master_id>/disciples/',
         views.HistorySummitStatByMasterDisciplesView.as_view(), name='master-disciples-stats'),

    path('summits/<int:pk>/devices/', views.SummitUserDeviceView.as_view(), name='summit-device-list'),
    path('summits/<int:pk>/users/', views.SummitProfileListView.as_view(), name='summit-profile-list'),
    path('summits/<int:pk>/tickets/', views.SummitTicketsView.as_view(), name='summit-tickets'),
    path('summits/<int:pk>/authors/', views.SummitAuthorListView.as_view(), name='summit-authors-list'),
    path('summits/<int:pk>/bishop_high_masters/',
         views.SummitBishopHighMasterListView.as_view(), name='summit-masters'),
    path('summits/<int:pk>/export_users/',
         views.SummitProfileListExportView.as_view(), name='summit-profile-export'),
    path('summits/<int:pk>/stats/', views.SummitStatisticsView.as_view(), name='summit-stats'),
    path('summits/<int:pk>/export_stats/',
         views.SummitStatisticsExportView.as_view(), name='summit-stats-export'),
    path('summit_ticket/<int:ticket>/print/', views.SummitTicketMakePrintedView.as_view(),
         name='summit-ticket-print'),
]

custom_app = [
    path('summits/<int:summit_id>/users/', views_app.SummitProfileTreeForAppListView.as_view(),
         name='summit-app-profile-list'),
    path('summits/<int:summit_id>/request_count/', views_app.app_request_count,
         name='summit-app-profile-request-count'),
    path('summits/<int:summit_id>/users/<int:master_id>/', views_app.SummitProfileTreeForAppListView.as_view(),
         name='summit-app-profile-list-master'),
]

summit_entries_urls = [
    path('reset_entry/<str:code>/', views_entry.ResetEntryView.as_view(), name='reset_entry'),
    path('block/<str:code>/', views_entry.BlockUserView.as_view(), name='block_user_entry'),
    path('unblock/<str:code>/', views_entry.UnblockUserView.as_view(), name='unblock_user_entry'),
    path('reset/codes/', views_entry.ResetAllCodesView.as_view(), name='reset_codes_entry'),
    path('load/codes/', views_entry.LoadNewCodesView.as_view(), name='load_codes_entry'),
    path('reset/entries/', views_entry.ResetAllEntriesView.as_view(), name='reset_entries_entry'),
    path('multi/', views_entry.FinishLessonView.as_view(), name='multi_entry'),
    path('one/', views_entry.StartLessonView.as_view(), name='one_entry'),

    path('block/', views_entry.BlockAllView.as_view(), name='block_all_entry'),
    path('unblock/', views_entry.UnblockAllView.as_view(), name='unblock_all_entry'),
]

urlpatterns = [
    path('', include(router_v1_0.urls)),
    path('', include(custom_urls)),

    path('app/', include(router_app.urls)),
    path('app/', include(custom_app)),
    path('summit_entries/', include(summit_entries_urls)),
]
