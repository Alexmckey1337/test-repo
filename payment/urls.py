from django.conf.urls import url

from payment import views

app_name = 'payment'


urlpatterns = [
    url(r'^deal/(?P<pk>\d+)/$', views.DealPaymentView.as_view(), name='deal'),
    url(r'^partner/(?P<pk>\d+)/$', views.PartnerPaymentView.as_view(), name='partner'),
]
