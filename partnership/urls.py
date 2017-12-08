from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse

from partnership import views

app_name = 'partner'


def redirect_to_deals(request):
    if request.user.can_see_deals():
        return redirect(reverse('partner:deals'))
    if request.user.can_see_partners():
        return redirect(reverse('partner:list'))
    if request.user.can_see_partner_stats():
        return redirect(reverse('partner:stats'))
    if request.user.can_see_deal_payments():
        return redirect(reverse('partner:payments'))
    raise PermissionDenied


urlpatterns = [
    url(r'^$', login_required(redirect_to_deals, login_url='entry'), name='main'),
    url(r'^list/$', views.PartnerListView.as_view(), name='list'),
    url(r'^deals/$', views.DealListView.as_view(), name='deals'),
    url(r'^stats/$', views.PartnerStatisticsListView.as_view(), name='stats'),
    url(r'^payments/$', views.PartnerPaymentsListView.as_view(), name='payments'),
    url(r'^summary/$', views.PartnerListSummaryView.as_view(), name='partnership_summary-list'),
    # url(r'^summary/(?P<manager_id>\d+)/$', views.PartnerDetailSummaryView.as_view(), name='partnership_summary-detail'),
    url(r'^summary/(?P<manager_id>(\d+|all))/$',
        views.PartnerDetailSummaryView.as_view(), name='partnership_summary-detail'),
]
