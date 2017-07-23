from django.conf.urls import url, include


urlpatterns = [
    url(r'^', include('account.urls')),
    url(r'^', include('event.urls')),
    url(r'^', include('hierarchy.urls')),
    url(r'^', include('location.urls')),
    url(r'^', include('navigation.urls')),
    url(r'^', include('notification.urls')),
    url(r'^', include('partnership.urls')),
    url(r'^', include('payment.urls')),
    url(r'^', include('report.urls')),

    url(r'^', include('group.urls')),

    url(r'^', include('status.urls')),
    url(r'^', include('summit.urls')),
]
