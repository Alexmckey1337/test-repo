from django.conf.urls import url, include


urlpatterns = [
    url(r'^', include('account.api.urls')),
    url(r'^', include('event.api.urls')),
    url(r'^', include('task.api.urls')),
    url(r'^', include('hierarchy.api.urls')),
    url(r'^', include('location.api.urls')),
    url(r'^', include('navigation.api.urls')),
    url(r'^', include('notification.api.urls')),
    url(r'^', include('partnership.api.urls')),
    url(r'^', include('payment.api.urls')),
    url(r'^', include('report.api.urls')),

    url(r'^', include('group.api.urls')),

    url(r'^', include('status.api.urls')),
    url(r'^', include('summit.api.urls')),
]
