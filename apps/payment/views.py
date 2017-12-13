from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from apps.partnership.models import Deal, Partnership
from apps.payment.models import Currency


class DealPaymentView(LoginRequiredMixin, DetailView):
    model = Deal
    context_object_name = 'deal'
    template_name = 'payment/deal.html'

    def get_queryset(self):
        return self.model.objects.base_queryset().annotate_full_name()

    def get_context_data(self, **kwargs):
        ctx = super(DealPaymentView, self).get_context_data(**kwargs)

        ctx['payments'] = self.object.payments.base_queryset().annotate_manager_name()
        # TODO test
        ctx['currencies'] = Currency.objects.all()
        ctx['partners'] = Partnership.objects.annotate_full_name().filter(
            pk__in=Partnership.objects.exclude(pk=self.object.partnership.id)[:11].values_list('id', flat=True))

        return ctx


class PartnerPaymentView(LoginRequiredMixin, DetailView):
    model = Partnership
    context_object_name = 'partner'
    template_name = 'payment/partner.html'

    def get_queryset(self):
        return self.model.objects.base_queryset().annotate_full_name()

    def get_context_data(self, **kwargs):
        ctx = super(PartnerPaymentView, self).get_context_data(**kwargs)

        ctx['payments'] = self.object.payments.base_queryset().annotate_manager_name()
        ctx['extra_payments'] = self.object.extra_payments.base_queryset().annotate_manager_name()
        ctx['deal_payments'] = self.object.deal_payments.base_queryset().annotate_manager_name()
        # TODO test
        ctx['partners'] = Partnership.objects.annotate_full_name().filter(
            pk__in=Partnership.objects.exclude(pk=self.object.id)[:11].values_list('id', flat=True))

        return ctx
