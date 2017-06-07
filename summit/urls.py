# -*- coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from summit import views

router_v1_0 = routers.DefaultRouter()
router_v1_0.register(r'summit_ankets', views.SummitProfileViewSet, base_name='summit_ankets')
router_v1_0.register(r'summit_tickets', views.SummitTicketViewSet)
router_v1_0.register(r'summit_search', views.SummitUnregisterUserViewSet, base_name='summit_search')
router_v1_0.register(r'summit_lessons', views.SummitLessonViewSet)

router_v1_0.register(r'summit', views.SummitViewSet)
router_v1_0.register(r'summit_types', views.SummitTypeViewSet)
router_v1_0.register(r'summit_ankets_with_notes', views.SummitAnketWithNotesViewSet,
                     base_name='ankets_with_notes')
router_v1_0.register(r'summit_visitors_location', views.SummitVisitorLocationViewSet)
router_v1_0.register(r'summit_event_table', views.SummitEventTableViewSet)
router_v1_0.register(r'summit_attends', views.SummitAttendViewSet)

router_app = routers.DefaultRouter()
router_app.register(r'summits', views.SummitTypeForAppViewSet, base_name='summits')
router_app.register(r'users', views.SummitAnketForAppViewSet, base_name='users')

custom_urls = [
    url(r'^generate_code/.+\.pdf', views.generate_code, name='generate_code'),
    url(r'^summit/(?P<summit_id>\d+)/master/(?P<master_id>\d+)\.pdf',
        views.summit_report_by_participant, name='summit-report-participant'),
    url(r'^generate_summit_tickets/(?P<summit_id>\d+)/', views.generate_summit_tickets, name='generate_code'),

    url(r'^summits/(?P<pk>\d+)/users/$', views.SummitProfileListView.as_view(), name='summit-profile-list'),
    url(r'^summits/(?P<pk>\d+)/export_users/$',
        views.SummitProfileListExportView.as_view(), name='summit-profile-export'),
    url(r'^summit_ticket/(?P<ticket>\d+)/print/$', views.SummitTicketMakePrintedView.as_view(),
        name='summit-ticket-print'),
]

custom_app = [
    url(r'^summits/(?P<summit_id>\d+)/users/$', views.SummitProfileTreeForAppListView.as_view(),
        name='summit-app-profile-list'),
    url(r'^summits/(?P<summit_id>\d+)/users/(?P<master_id>\d+)/$', views.SummitProfileTreeForAppListView.as_view(),
        name='summit-app-profile-list-master'),
]

urlpatterns = [
    url(r'^v1.0/', include(router_v1_0.urls)),
    url(r'^app/', include(router_app.urls)),

    url(r'^v1.0/', include(custom_urls)),
    url(r'^app/', include(custom_app)),
]
