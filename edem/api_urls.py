from django.conf.urls import url, include


urlpatterns = [
    url(r'^', include('apps.account.api.urls')),
    url(r'^', include('apps.event.api.urls')),
    url(r'^', include('apps.task.api.urls')),
    url(r'^', include('apps.hierarchy.api.urls')),
    url(r'^', include('apps.location.api.urls')),
    url(r'^', include('apps.navigation.api.urls')),
    url(r'^', include('apps.notification.api.urls')),
    url(r'^', include('apps.partnership.api.urls')),
    url(r'^', include('apps.payment.api.urls')),
    url(r'^', include('apps.report.api.urls')),

    url(r'^', include('apps.group.api.urls')),

    url(r'^', include('apps.status.api.urls')),
    url(r'^', include('apps.summit.api.urls')),
]
