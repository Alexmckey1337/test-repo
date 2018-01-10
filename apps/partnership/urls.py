from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse, path, re_path

from apps.partnership import views

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
    path('', login_required(redirect_to_deals, login_url='entry'), name='main'),
    path('list/', views.PartnerListView.as_view(), name='list'),
    path('deals/', views.DealListView.as_view(), name='deals'),
    path('stats/', views.PartnerStatisticsListView.as_view(), name='stats'),
    path('payments/', views.PartnerPaymentsListView.as_view(), name='payments'),
    path('summary/', views.PartnerListSummaryView.as_view(), name='partnership_summary-list'),
    re_path(r'^summary/(?P<manager_id>(\d+|all))/$',
            views.PartnerDetailSummaryView.as_view(), name='partnership_summary-detail'),
]
