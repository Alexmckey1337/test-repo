from django.contrib import admin
from django.conf.urls import url, include
from rest_framework import routers
import account.views
import hierarchy.views
import notification.views
import event.views
import status.views
import navigation.views
import partnership.views
import tv_crm.views
import summit.views
import report.views
import location.views

router = routers.DefaultRouter()
router.register(r'users', account.views.UserViewSet)
router.register(r'short_users', account.views.UserShortViewSet)
router.register(r'hierarchy', hierarchy.views.HierarchyViewSet)
router.register(r'departments', hierarchy.views.DepartmentViewSet)
router.register(r'notifications', notification.views.NotificationViewSet)
router.register(r'event_types', event.views.EventTypeViewSet)
router.register(r'event_ankets', event.views.EventAnketViewSet)
router.register(r'events', event.views.EventViewSet)
router.register(r'participations', event.views.ParticipationViewSet)
router.register(r'statuses', status.views.StatusViewSet)
router.register(r'divisions', status.views.DivisionViewSet)
#router.register(r'navigation', navigation.views.NavigationViewSet)
router.register(r'partnerships', partnership.views.PartnershipViewSet)
router.register(r'partnerships_unregister_search', partnership.views.PartnershipsUnregisterUserViewSet)
router.register(r'deals', partnership.views.DealViewSet)
router.register(r'tv_call', tv_crm.views.LastCallViewSet)
router.register(r'tv_call_stat', tv_crm.views.CallStatViewSet)
router.register(r'synopsis', tv_crm.views.SynopsisViewSet)
router.register(r'summit', summit.views.SummitViewSet)
router.register(r'summit_ankets', summit.views.SummitAnketViewSet)
router.register(r'tables', navigation.views.TableViewSet)
router.register(r'columnTypes', navigation.views.ColumnTypeViewSet)
router.register(r'columns', navigation.views.ColumnViewSet)
router.register(r'summit_types', summit.views.SummitTypeViewSet)
router.register(r'summit_search', summit.views.SummitUnregisterUserViewSet)
router.register(r'user_reports', report.views.UserReportViewSet)
router.register(r'week_reports', report.views.WeekReportViewSet)
router.register(r'month_reports', report.views.MonthReportViewSet)
router.register(r'year_reports', report.views.YearReportViewSet)
router.register(r'countries', location.views.CountryViewSet)
router.register(r'regions', location.views.RegionViewSet)
router.register(r'cities', location.views.CityViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('account.urls')),
    url(r'^api/', include('event.urls')),
    url(r'^api/', include('partnership.urls')),
    url(r'^api/', include('tv_crm.urls')),
    url(r'^api/', include('hierarchy.urls')),
    url(r'^api/', include('navigation.urls')),
    url(r'^api/', include('summit.urls')),
    url(r'^', include('main.urls')),
    url(r'^', include('django.contrib.auth.urls')),
]
