from django.urls import include, path
from rest_framework import routers

from apps.partnership.api import views

router_v1_1 = routers.DefaultRouter()
router_v1_1.register('partnerships', views.PartnershipViewSet, base_name='partner')

router_v1_0 = routers.DefaultRouter()
router_v1_0.register('deals', views.DealViewSet)
router_v1_0.register('partner_groups', views.PartnerGroupViewSet)

router_v1_0.register('church_partners', views.ChurchPartnerViewSet, base_name='church_partner')
router_v1_0.register('church_deals', views.ChurchDealViewSet)

custom_urls = [
    path('users/<int:user_id>/set_partner_role/', views.SetPartnerRoleView.as_view(), name="set_partner_role"),
    path('users/<int:user_id>/delete_partner_role/',
         views.DeletePartnerRoleView.as_view(), name="delete_partner_role"),
    path('users/<int:user_id>/update_partner_role/',
         views.UpdatePartnerRoleView.as_view(), name="update_partner_role"),
    path('partners/<int:partner_id>/last_deals/', views.LastPartnerDealsView.as_view(), name="partner-last_deals"),
    path('partners/<int:partner_id>/last_payments/',
         views.LastPartnerPaymentsView.as_view(), name="church_partner-last_payments"),
    path('church_partners/<int:partner_id>/last_deals/', views.LastChurchPartnerDealsView.as_view(),
         name="partner-last_deals"),
    path('church_partners/<int:partner_id>/last_payments/',
         views.LastChurchPartnerPaymentsView.as_view(), name="church_partner-last_payments"),
]

urlpatterns = [
    path('', include(router_v1_0.urls)),
    path('', include(router_v1_1.urls)),
    path('', include(custom_urls)),
]
