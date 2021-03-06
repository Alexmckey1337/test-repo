from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic.base import TemplateView

from apps.account.models import CustomUser
from apps.hierarchy.models import Department, Hierarchy
from apps.partnership.models import PartnerGroup, PartnerRole
from apps.payment.models import Currency


class CanSeePartnersMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_partners():
            raise PermissionDenied
        return super(CanSeePartnersMixin, self).dispatch(request, *args, **kwargs)


class CanSeePartnerSummaryMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_partner_summary():
            raise PermissionDenied
        return super(CanSeePartnerSummaryMixin, self).dispatch(request, *args, **kwargs)


class CanSeeDealsMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_deals():
            raise PermissionDenied
        return super(CanSeeDealsMixin, self).dispatch(request, *args, **kwargs)


class CanSeeDealPaymentsMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_deal_payments():
            raise PermissionDenied
        return super(CanSeeDealPaymentsMixin, self).dispatch(request, *args, **kwargs)


class CanSeePartnerStatsMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.can_see_partner_stats():
            raise PermissionDenied
        return super(CanSeePartnerStatsMixin, self).dispatch(request, *args, **kwargs)


class PartnerListView(LoginRequiredMixin, CanSeePartnersMixin, TemplateView):
    template_name = 'partner/partners.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super(PartnerListView, self).get_context_data(**kwargs)

        extra_context = {
            'departments': Department.objects.all(),
            'partner_groups': PartnerGroup.objects.all(),
            'hierarchies': Hierarchy.objects.order_by('level'),
            'currencies': Currency.objects.all(),
            'levels': [{'id': r[0], 'title': r[1]} for r in PartnerRole.LEVELS],
            'statuses': [
                {'id': 'vip', 'title': 'VIP'},
                {'id': 'ruby', 'title': 'Рубиновый'},
                {'id': 'gold', 'title': 'Голд'},
                {'id': 'any', 'title': 'Любой'},
                {'id': 'empty', 'title': 'Никакой'},
            ],
            'active_status_options': [{'id': 'True', 'title': 'Активный'}, {'id': 'False', 'title': 'Не активный'}]
        }
        user = self.request.user
        if user.is_staff or user.has_operator_perm:
            extra_context['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
        elif not user.hierarchy:
            extra_context['masters'] = list()
        elif user.hierarchy.level < 2:
            extra_context['masters'] = user.__class__.get_tree(
                user).filter(is_active=True, hierarchy__level__gte=1)
        else:
            extra_context['masters'] = CustomUser.objects.filter(is_active=True, hierarchy__level__gte=1)
        extra_context['master_options'] = [{'id': m.pk, 'title': m.fullname} for m in extra_context['masters']]

        ctx.update(extra_context)
        return ctx


class PartnerListSummaryView(LoginRequiredMixin, CanSeePartnerSummaryMixin, TemplateView):
    template_name = 'partner/partnership_summary.html'
    login_url = 'entry'


class PartnerDetailSummaryView(LoginRequiredMixin, CanSeePartnerSummaryMixin, TemplateView):
    template_name = 'partner/partnership_summary_detail.html'
    login_url = 'entry'
    manager = None

    def dispatch(self, request, *args, **kwargs):
        manager_id = kwargs.get('manager_id')
        self.manager = None if manager_id == 'all' else get_object_or_404(CustomUser, pk=manager_id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['manager'] = self.manager

        return ctx


class PartnerStatisticsListView(LoginRequiredMixin, CanSeePartnerStatsMixin, TemplateView):
    template_name = 'partner/stats.html'
    login_url = 'entry'


class PartnerPaymentsListView(LoginRequiredMixin, CanSeeDealPaymentsMixin, TemplateView):
    template_name = 'partner/payments.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super(PartnerPaymentsListView, self).get_context_data(**kwargs)

        currencies = Currency.objects.all()
        ctx['currencies'] = currencies
        ctx['currency_options'] = [{'id': c.pk, 'title': c.name} for c in currencies]
        ctx['partner_groups'] = PartnerGroup.objects.all()
        ctx['deal_type_options'] = [
            {'id': '1', 'title': 'Партнерские'},
            {'id': '2', 'title': 'Десятины'},
        ]
        # ctx['supervisors'] = CustomUser.objects.filter(
        #     checks__isnull=False).order_by('last_name').distinct("id", "last_name")
        # ctx['managers'] = CustomUser.objects.filter(
        #     Q(partner_role__level__lte=settings.PARTNER_LEVELS['manager']) |
        #     Q(disciples_deals__isnull=False)).order_by('last_name').distinct("id", "last_name")

        return ctx


class DealListView(LoginRequiredMixin, CanSeeDealsMixin, TemplateView):
    template_name = 'partner/deals.html'
    login_url = 'entry'

    def get_context_data(self, **kwargs):
        ctx = super(DealListView, self).get_context_data(**kwargs)

        currencies = Currency.objects.all()
        ctx['currencies'] = currencies
        ctx['currency_options'] = [{'id': c.pk, 'title': c.short_name} for c in currencies]
        ctx['partner_groups'] = PartnerGroup.objects.all()
        ctx['payment_status_options'] = [
            {'id': '0', 'title': 'Hе оплачена'},
            {'id': '1', 'title': 'Оплачена частично'},
            {'id': '2', 'title': 'Оплачена полностью'},
        ]
        ctx['deal_type_options'] = [
            {'id': '1', 'title': 'Партнерские'},
            {'id': '2', 'title': 'Десятины'},
        ]

        return ctx
