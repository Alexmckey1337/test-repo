from django.urls import include, path


urlpatterns = [
    path('', include('apps.account.api.urls')),
    path('events/', include('apps.event.api.urls')),
    path('', include('apps.task.api.urls')),
    path('', include('apps.hierarchy.api.urls')),
    path('', include('apps.location.api.urls')),
    path('', include('apps.navigation.api.urls')),
    path('', include('apps.notification.api.urls')),
    path('', include('apps.partnership.api.urls')),
    path('', include('apps.payment.api.urls')),
    path('', include('apps.report.api.urls')),

    path('', include('apps.group.api.urls')),

    path('', include('apps.status.api.urls')),
    path('', include('apps.summit.api.urls')),
    path('controls/', include('apps.controls.api.urls')),
]
